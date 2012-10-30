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
