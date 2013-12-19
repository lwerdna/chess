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
# bughouse opening oracle, 2012 andrewl

FILTER_EXOTIC_MOVES = 0

import re
import os
import sys
import tempfile
import sqlite3

def clearScreen():
    print '\n'*128

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

###############################################################################
# main()
###############################################################################

if __name__ == '__main__':
    gamesCount = 0
    goodGamesCount = 0

    conn = sqlite3.connect("openings.db")
    curs = conn.cursor()

    currentLine = []

    while 1:
        clearScreen()
        currentPly = len(currentLine) + 1
        print "%s to move" % (['BLACK', 'WHITE'][currentPly % 2])
        print "current line: %s" % ','.join(currentLine)
        totalBranches = getTotalBranches(curs, currentLine)
        #print "number of lines from this point: ", totalBranches
        possibleNextPly = getPossibleNextPly(curs, currentLine)
        #print "possible moves at this point: ", possibleNextPly
        
        # calculate the popularity of each candidate move
        possibleNextPlyPopularity = {}
        for candidate in possibleNextPly:
            cTotalBranches = 1.0 * getTotalBranches(curs, currentLine + [candidate])
            possibleNextPlyPopularity[candidate] = (cTotalBranches / totalBranches) * 100

        # sort on popularity, decreasing
        possibleNextPly = sorted(possibleNextPly, key = lambda x: possibleNextPlyPopularity[x], reverse=True)

        if FILTER_EXOTIC_MOVES:
            possibleNextPly = filter(lambda x: possibleNextPlyPopularity[x] > 1.0, possibleNextPly)

        # given menu
        print " q - quit"
        print " u - undo (go back a ply)"
        for index, thing in enumerate(possibleNextPly):
            print "% 2d - %s (%.02f%%)" % (index, possibleNextPly[index], possibleNextPlyPopularity[possibleNextPly[index]])

        # get/process user input
        userInput = raw_input("enter option: ")
        if userInput == 'q':
            break
        elif userInput == 'u':
            if currentLine:
                currentLine = currentLine[:-1]
            else:
                print "ERROR: current line is empty (can't go back)"
        else:
            ind = int(userInput)
            if ind < 0 or ind >= len(possibleNextPly):
                print "ERROR: index out of range"
            else:
                currentLine += [ possibleNextPly[ind] ]

    # exit out of user input loop
    conn.close()
