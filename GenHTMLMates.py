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
import sqlite3
import string
import traceback
import random

import re
import GenTools
import CrazyLogic

###############################################################################
# main()
###############################################################################

puzzleArray = []

if __name__ == '__main__':

    imgPath = './images/'

    anki = False
    if len(sys.argv) > 1 and sys.argv[1] == 'anki':
        anki = True
        imgPath = '' # just drop 'em in whatever.media

    conn = sqlite3.connect("MineMissedMates.db")
    curs = conn.cursor()

    bpgns = curs.execute("select position, mate from data where mate != ''") 
    
    for rowIdx, row in enumerate(bpgns.fetchall()):

        (bfen, line) = map(lambda x: str(x), row)

        m = re.match('^(.*?) ', line)
        if not m:
            raise Exception("WTF? can't get first move from %s" % line)

        hint = m.group(1)

        boardMap = CrazyLogic.fenToBoardMap(bfen)

        flipped = 0
        if boardMap['activePlayer'] == 'b':
            flipped = 1

        html = GenTools.boardMapToHtml(boardMap, flipped, imgPath)
        html += "<h2>Puzzle %d</h2>\n" % rowIdx
        html += "<hr>\n"

        if anki:
            html = re.sub('\n', '', html)
            html = '%s;figure it out?' % html

        puzzleArray.append(html)

    #if anki:
        #random.shuffle(puzzleArray)

    for p in puzzleArray:
        print p
