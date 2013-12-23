#!/usr/bin/python

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

def numberizeVariation(moveNum, color, pv):
    answer = []

    moves = pv.split(' ')

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

def parseVariations(moveNum, color, output):
    # return array of [score, variation] pairs
    answer = []    

    strings = output.split("\n")
   
    for string in strings:
        # if stockfish finds mate, he won't output the usual mult-pv, he'll just
        # spit out the mate line, for example:
        # info depth 100 seldepth 3 score mate -1 nodes 607 nps 14116 time 43 multipv 1 pv f8c5 f3f7
        # bestmove f8c5 ponder f3f7
#        m = re.search(r' score mate .* pv (.*)', string)
#        if m:
#            bestScore = 1000;
#            if color in 'bB':
#                bestScore *= -1;
#            temp = numberizeVariation(moveNum, color, m.group(1)) 
#            answer = [ [ bestScore, temp ], \
#                        [ bestScore, temp ], \
#                        [ bestScore, temp ] ]
#            break;

        m1 = re.search(r'score (mate|cp) (-?\d+)', string)
        m2 = re.search(r'multipv (\d+) pv (.*)', string)
        if m1 and m2:
            varIndex = int(m2.group(1))-1

            score = int(m1.group(2)) * .01
            if(m1.group(1) == 'mate'):
                score *= 1000;

            variation = m2.group(2)

            if color in ['b', 'B']:
                score *= -1

            # ensure answer array has enough size for this MultiPV
            while varIndex >= len(answer):
                answer.append([None,None])
             
            answer[varIndex] = [score, numberizeVariation(moveNum, color, variation)]

    return answer

###############################################################################
# main()
###############################################################################
if __name__ == '__main__':
    gamesCount = 0
    goodGamesCount = 0

    pgnPath = sys.argv[1]

    match = PgnParser.PgnChessMatchIteratorFile(pgnPath).next()
    matchQuiz = match.copy()
    matchAnswers = match.copy()

    for (i,state) in enumerate(match.states):
        print "on state: " + state.toFEN()

        if i < len(match.moves):
            print "with move: %s" % str(match.moves[i])

        output = runGetOutput(['./stockfishshim', 'all', state.toFEN()])
        variations = parseVariations(state.fullMoveNum, state.activePlayer, output)

        top3moves = []
        top3scores = []
        for (score, line) in variations:
            matchQuiz.moves[i].comments = {''}
            matchAnswers.moves[i].comments = {''}

            temp = "({%.2f} %s)" % (score, line)
            print temp
            if i < len(match.moves):
                matchAnswers.moves[i].extraString += ("\n%s" % temp)

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
                variations = parseVariations(state.fullMoveNum, state.activePlayer, output)
                print variations
                temp = "({%.2f} %s)" % (variations[0][0], variations[0][1])
                print temp
                matchAnswers.moves[i].extraString += ("\n%s" % temp)
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


