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
                break;

            answer.append('%d.%s %s' % (moveNum, moves[0], moves[1]))
            moves = moves[2:]

        moveNum += 1

    return ' '.join(answer)

def parseVariations(moveNum, color, output):
    # return array of [score, variation] pairs
    answer = []    

    strings = output.split("\n")
    
    for string in strings:
        m1 = re.search(r'score cp (-?\d+)', string)
        m2 = re.search(r'multipv (\d+) pv (.*)', string)
        if m1 and m2:
            varIndex = int(m2.group(1))-1
            score = int(m1.group(1))
            variation = m2.group(2)

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

    match = PgnParser.PgnChessMatchIteratorFile(sys.argv[1]).next()

    for (i,state) in enumerate(match.states):
        print "on state: " + state.toFEN()

        if i < len(match.moves):
            print "with move: %s" % str(match.moves[i])

        output = runGetOutput(['./stockfishshim', 'all', state.toFEN()])
        variations = parseVariations(state.fullMoveNum+1, state.activePlayer, output)

        for var in variations:
            print "({%d} %s)" % (var[0], var[1])

        # extract the played move
        top3moves = map(lambda x: re.match(r'^\d\.{1,3} ?(\S+)', x[1]).group(1), variations)

        playedMove = match.moves[i].canonical
        if not (playedMove in top3moves):
            print "played move %s is not in top 3 moves! searching..." % playedMove

            output = runGetOutput(['./stockfishshim', playedMove, state.toFEN()])
            variations = parseVariations(state.fullMoveNum+1, state.activePlayer, output)
            print "({%d} %s)" % (variations[0][0], variations[0][1])

        print "----------------------------------------------------------------"


