#!/usr/bin/python
import re
import os
import sys
import tempfile
import sqlite3

import BpgnParser
'''
/* hold 10 full moves in */
create table openings(ply1 string, ply2 string, ply3 string, ply4 string,
ply5 string, ply6 string, ply7 string, ply8 string, ply9 string, ply10 string,
ply11 string, ply12 string, ply13 string, ply14 string, ply15 string, ply16
string, ply17 string, ply18 string, ply19 string, ply20 string, count int);
'''

###############################################################################
# main()
###############################################################################

inserts = 0

if __name__ == '__main__':
    gamesCount = 0
    goodGamesCount = 0

    conn = sqlite3.connect("openings.db")
    curs = conn.cursor()

    path = sys.argv[1]
    it = None

    if os.path.isfile(path):
        it = BpgnParser.MatchIteratorFile(path)
    elif os.path.isdir(path):
        print "making dir"
        it = BpgnParser.MatchIteratorDir(path)
    else:
        raise Exception("WTF?")

    print "k now"
    for match in it:
        try:
            match.sanityCheck()

            movesA = match.getMovesBoardA()
            movesB = match.getMovesBoardB()

            newRows = []

            if len(movesA) >= 20:
                newRows.append(map(lambda x: movesA[x].san, range(20)))
            if len(movesB) >= 20:
                newRows.append(map(lambda x: movesB[x].san, range(20)))
              
            for newRow in newRows:
                fmtArgs = newRow + newRow
                #print "fmtArgs: ", fmtArgs
                #print "lengtH: %d " % len(fmtArgs)

                statement = ('' + \
                    "insert or replace into openings " + \
                    "values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', " + \
                    "    coalesce( " + \
                    "        (select count from openings where " + \
                    "            ply1=='%s' and ply2=='%s' and ply3=='%s' and ply4=='%s' and ply5=='%s' and ply6=='%s' " + \
                    "            and ply7=='%s' and ply8=='%s' and ply9=='%s' and ply10=='%s' and ply11=='%s' and ply12=='%s'" + \
                    "            and ply13=='%s' and ply14=='%s' and ply15=='%s' and ply16=='%s' and ply17=='%s' and ply18=='%s'" + \
                    "            and ply19=='%s' and ply20=='%s'" + \
                    "        )," + \
                    "        0" + \
                    "    )" + \
                    "    + 1" + \
                    ");") % tuple(fmtArgs)
               
                #print statement
                print "inserted my %d'th row" % inserts
                curs.execute(statement)
                conn.commit()
                inserts = inserts + 1

                #print statement

        except Exception as e:
            print e
            continue

        #break

    conn.close()
