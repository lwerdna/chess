#!/usr/bin/python
#------------------------------------------------------------------------------
# Copyright 2012, 2013 Andrew Lamoureux
#
# This file is a part of FunChess
#
# FunChess is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------
# use stockfish to create a quiz/answer pgn from a game pgn
#------------------------------------------------------------------------------

import os
import re
import sys
import subprocess

import Common
import ChessMove
import PgnTokenizer
import PgnParser
from ChessState import ChessState

def runGetOutput(cmdAndArgs):
    print "opening on -%s-" % cmdAndArgs

    try:
        poObj = subprocess.Popen(cmdAndArgs, stdout=subprocess.PIPE);

        while(1):
            #print "calling communicate..."
            text = poObj.communicate()[0]
            return text
    except Exception as e:
        print e

# translate stockfish's custom way of representing moves
#
# stockfish|SAN
# ---------+---
# e8c8     |O-O-O
# e7e8q    |e8=q
#
# this requires playing through the moves of the variation, which is very inefficient :/
#
# input:
#   variation, eg: "b2b4 c5f2 f3f2 e8c8 g8f6 d2d3 c6b4 e7e8q..."
# returns:
#   normalized variation, eg: "b2b4 c5f2 f3f2 e8c8 g8f6 d2d3 c6b4 e8=Q..."
#
def destockfishifyVariation(variation, chessState):
    state = chessState.copy()
    sans = variation.split(' ')
    result = []

    print "destocking: %s" % variation

    for before in sans:
        if before == 'e8c8' and (state['a8'] + state['b8'] + state['c8'] + state['d8'] + state['e8'] == 'r   k'):
            if state.activePlayer != 'b':
                raise "stockfish wants to castle with e8c8, but it's not black's turn!"
            if not 'q' in state.castleAvail:
                raise "stockfish wants to castle with e8c8, but black queenside castle is not available!"
            after = 'O-O-O'

        elif before == 'e8g8' and (state['e8'] + state['f8'] + state['g8'] + state['h8'] == 'k  r'):
            if state.activePlayer != 'b':
                raise "stockfish wants to castle with e8g8, but it's not black's turn!"
            if not 'k' in state.castleAvail:
                raise "stockfish wants to castle with e8g8, but black kingside castle is not available!"
            after = 'O-O'

        elif before == 'e1c1' and (state['a1'] + state['b1'] + state['c1'] + state['d1'] + state['e1'] == 'R   K'):
            if state.activePlayer != 'w':
                raise "stockfish wants to castle with e1c1, but it's not white's turn!"
            if not 'Q' in state.castleAvail:
                raise "stockfish wants to castle with e1c1, but white queenside castle is not available!"
            after = 'O-O-O'

        elif before == 'e1g1' and (state['e1'] + state['f1'] + state['g1'] + state['h1'] == 'K  R'):
            if state.activePlayer != 'w':
                raise "stockfish wants to castle with e1g1, but it's not white's turn!"
            if not 'K' in state.castleAvail:
                raise "stockfish wants to castle with e1g1, but white kingside castle is not available!"
            after = 'O-O'

        elif len(before) == 5:
            if not before[4] in 'nbrqNBRQ':
                raise "don't know how to handle stockfish move %s (thought it was a promotion)" % before

            after = before[2:4] + '=' + before[4].upper()

        else:
            # no translated needed
            after = before

        if after != before:
            print "translated %s to %s" % (before, after)

        
        # we have to carefully see if stockfish can play the moves it gives
        # I made bug report here: http://support.stockfishchess.org/discussions/problems/3265-bug-stockfish-moves-into-check-with-queenside-castle
        try:
            # progress the state to to be able to translate further moves...
            temp = ChessMove.ChessMove(state.activePlayer, '1', after)
            state = state.transition(temp)

            # save the translated move (if it was able to be played!)
            result.append(after)
        except:
            print "WTF! Stockfish played another illegal move!" 
            break

    return ' '.join(result)

def numberizeVariation(moveNum, color, pv):
    answer = []

    moves = pv.split(' ')

    moves = moves[0:8]

    while(moves):
        if (not answer) and (color in ['b', 'B']):
            answer.append('%d... %s' % (moveNum, moves[0]))
            moves = moves[1:]
            
        else:
            if len(moves) < 2:
                answer.append('%d.%s' % (moveNum, moves[0]))
                moves = moves[1:]
            else:
                answer.append('%d.%s %s' % (moveNum, moves[0], moves[1]))
                moves = moves[2:]

        moveNum += 1

    temp = ' '.join(answer)
    return temp

# returns array of [score, variation] pairs
def parseVariations(moveNum, color, output, state):
    answer = []    

    strings = output.split("\n")
   
    for string in strings:
        # example line we're trying to parse:
        # info depth 14 seldepth 23 score cp 266 nodes 1938924 nps 1990681 time 974 multipv 2 pv b2b4 c5f2 f3f2 g8f6 d2d3 c6b4 ... 
        # or in the case of mate:
        # info depth 100 seldepth 3 score mate -1 nodes 607 nps 14116 time 43 multipv 1 pv f8c5 f3f7
        m = re.search(r'score (mate|cp) (-?\d+).*multipv (\d+) pv (.*)', string)
        if m: 
            # score parsing
            score = int(m.group(2)) * .01
            # adjust for black 
            if color in ['b', 'B']:
                score *= -1
            # adjust for mate (convention: score of 1000 pawns)
            if(m.group(1) == 'mate'):
                score *= 100000;

            # ensure answer array has enough size for this MultiPV
            varIndex = int(m.group(3))-1
            while varIndex >= len(answer):
                answer.append(None)
           
            # save
            variation = m.group(4)
            answer[varIndex] = [score, variation]

    # post-process variations (stockfish -> more readable)
    for i in range(len(answer)):
        variation = answer[i][1]
        variation = destockfishifyVariation(variation, state)
        variation = numberizeVariation(moveNum, color, variation)
        answer[i][1] = variation

    # done
    return answer

###############################################################################
# main()
###############################################################################
if __name__ == '__main__':
    gamesCount = 0
    goodGamesCount = 0

    pgnPath = sys.argv[1]

    startMove = 1
    if len(sys.argv) > 2:
        startMove = int(sys.argv[2])

    match = PgnParser.PgnChessMatchIteratorFile(pgnPath).next()
    matchQuiz = match.copy()
    matchAnswers = match.copy()

    for (i,state) in enumerate(match.states):
        if state.fullMoveNum < startMove:
            continue

        print "on state: " + state.toFEN()

        if i < len(match.moves):
            print "with move: %s" % str(match.moves[i])
            matchQuiz.moves[i].comments = {''}
            matchAnswers.moves[i].comments = {''}

        output = runGetOutput(['./stockfishshim', 'all', state.toFEN()])
        variations = parseVariations(state.fullMoveNum, state.activePlayer, output, state)

        top3moves = []
        top3scores = []
        for (score, line) in variations:

            temp = "({%.2f} %s)" % (score, line)
            print temp
            if i < len(match.moves):
                matchAnswers.moves[i].variations.append(temp)

            m = re.match(r'^\d+\.{1,3} ?(\S+)', line)
            if m:
                thisMove = m.group(1)
                top3moves.append(thisMove)
                top3scores.append(score)
            else:
                raise Exception("couldn't extract first move from %s" % line)

        # extract the played move (if it's not the last move of the game)
        if(i < len(match.moves)):
            playedMove = match.moves[i].canonical
            playedScore = None

            # calculate score of the played move
            if playedMove in top3moves:
                playedScore = top3scores[top3moves.index(playedMove)]
            else: 
                output = runGetOutput(['./stockfishshim', playedMove, state.toFEN()])
                variations = parseVariations(state.fullMoveNum, state.activePlayer, output, state)
                temp = "({%.2f} %s)" % (variations[0][0], variations[0][1])
                print temp

                matchAnswers.moves[i].variations.append(temp)
                playedScore = variations[0][0]

            # classify the move
            diff = abs(abs(top3scores[0]) - abs(playedScore))

            if diff > 2:
                print "BLUNDER!"
            elif diff > 0.9:
                print "MISTAKE!"
            elif diff > 0.3:
                print "Innacuracy!"
            
            if i < len(match.moves):
                if diff > 2:
                    matchQuiz.moves[i].comments = {'BLUNDER'}
                elif diff > 0.9:
                    matchQuiz.moves[i].comments = {'MISTAKE'}
                elif diff > 0.3:
                    matchQuiz.moves[i].comments = {'INNACURACY'}

        print "----------------------------------------------------------------"

    m = re.match(r'(.*)\.pgn', pgnPath)
    base = m.group(1)

    quizPath = base + '-quiz.pgn'
    answersPath = base + '-answers.pgn'
    
    print "writing quiz to: %s" % quizPath
    fobj = open(quizPath, 'w')
    fobj.write(str(matchQuiz))
    fobj.close()

    print "writing answers to: %s" % answersPath
    fobj = open(answersPath, 'w')
    fobj.write(str(matchAnswers))
    fobj.close()
    
    print "opening quiz... (answers will open when you exit)" 
    runGetOutput(['scid', quizPath])
    print "opening answers..."
    runGetOutput(['scid', answersPath])


