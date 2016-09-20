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

#!/usr/bin/python

import re
import os
import sys
import tempfile
import sqlite3

import Tkinter

import Common
import ChessBoard
import CrazyLogic

def genLineCondition(currentLine):
    statement = ''

    if(currentLine):
        statement += ' where'

        for i in range(len(currentLine)):
            if i != 0:
                statement += " and"

            statement += " ply%d='%s'" % (i+1, currentLine[i])

    return statement

def getTotalBranches(cursor, currentLine):
    statement = 'select count(ply1) from openings'
    statement += genLineCondition(currentLine)
    #print statement
    return cursor.execute(statement).fetchone()[0]

def getPossibleNextPly(cursor, currentLine):
    statement = 'select distinct ply%d from openings' % (len(currentLine) + 1)
    statement += genLineCondition(currentLine)
    #print statement
    return map(lambda x: str(x[0]), cursor.execute(statement).fetchall())

def fenPieceToBitmapFile(p, square):
    # square is either 'd'/0 (dark) or 'l'/1 (light)

    mapping =       { 'P':'pl', 'p':'pd',
                      'B':'bl', 'b':'bd',
                      'N':'nl', 'n':'nd',
                      'R':'rl', 'r':'rd',
                      'Q':'ql', 'q':'qd',
                      'K':'kl', 'k':'kd'
                      }

    # knock off the promoted modifier
    p = re.sub('~', '', p)

    colorChar = ['d', 'l'][square]

    if p == ' ':
        return colorChar + 'sq48.gif'
    else:
        if not p in mapping:
            while 1:
                raise Exception("invalid piece! (%s)" % p)

        return mapping[p] + colorChar + '48.gif'


def boardMapToHtml(boardMap, flipped=0):
    html = '<table border=0 cellpadding=0 cellspacing=0>\n'

    pieceGetSequence = range(64)
    if flipped:
        pieceGetSequence.reverse()

    html += '<tr>\n'

    for i in range(64):
        # end current row, start new row
        if not (i%8):
            html += '\n</tr>\n'
            html += '<tr>\n'

        # table cell has image in it
        # get either 0,1,2,... or 63,62,61,...
        tmp = pieceGetSequence[i]
        # map 0->'a8', 63->'h1', etc.
        tmp = Common.squaresSan[tmp]
        # map 'a8' to 'r' or 'R' for example (getting piece)
        tmp = boardMap[tmp]
        # finally, map that piece to a filename
        tmp = fenPieceToBitmapFile(tmp, (i+i/8+1)%2)

        html += ' <td><img src="%s" /></td>\n' %  tmp

    html += '\n</tr>\n'
    html += '</table>\n'

    return html

###############################################################################
# main()
###############################################################################

g_curs = None

def genCards(currentLine, depth):
    if depth == 12:
        return;

    #--------
    # get the branches
    totalBranches = getTotalBranches(g_curs, currentLine)
    possibleNextPly = getPossibleNextPly(g_curs, currentLine)

    # calculate the popularity of each candidate move
    possibleNextPlyPopularity = {}
    for candidate in possibleNextPly:
        cTotalBranches = 1.0 * getTotalBranches(curs, currentLine + [candidate])
        possibleNextPlyPopularity[candidate] = (cTotalBranches / totalBranches) * 100
    # sort the possibilities
    possibleNextPly = sorted(possibleNextPly, key = lambda x: possibleNextPlyPopularity[x], reverse=True)

    # and filter the bad ones
    possibleNextPly = filter(lambda x: possibleNextPlyPopularity[x] >= 10.0, possibleNextPly)

    #--------
    # play the moves to get the board state
    boardMap = CrazyLogic.fenToBoardMap(Common.initCrazyFEN)
    for move in currentLine:
        boardMap = CrazyLogic.nextStateInternal(boardMap, move, 0, 1)
        
    # draw the board, get the html
    # if black to play, flip board so we see from black's angle
    doFlip = len(currentLine) % 2

    html = ''
    html += boardMapToHtml(boardMap, doFlip)
    html = re.sub('\n', '', html)
    html = re.sub('\.\/images\/', '', html)

    # draw the answers
    html += ';'
    for index, thing in enumerate(possibleNextPly):
        html += ("%s (%.02f%%)" % (possibleNextPly[index], possibleNextPlyPopularity[possibleNextPly[index]]))
        html += '<br />'

    # draw the line
    html += '<br />'
    html += '(line here is: ' + ','.join(currentLine) + ')'

    print html

    #--------
    # now recur
    for ply in possibleNextPly:
        genCards(currentLine + [ply], depth+1)

if __name__ == '__main__':
    gamesCount = 0
    goodGamesCount = 0

    conn = sqlite3.connect("openings.db")
    curs = conn.cursor()
    g_curs = curs

    genCards([], 0)
