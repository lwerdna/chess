#!/usr/bin/python
import re
import os
import sys
import sqlite3
import string
import traceback

import BpgnParser
import Sunsetter

###############################################################################
# main()
###############################################################################
if __name__ == '__main__':
    gamesCount = 0
    goodGamesCount = 0

    path = sys.argv[1]
    it = None

    if os.path.isfile(path):
        it = BpgnParser.MatchIteratorFile(path)
    elif os.path.isdir(path):
        it = BpgnParser.MatchIteratorDir(path)
    else:
        raise Exception("WTF?")

    # get in database
    # sqlite> .schema
    # CREATE TABLE data(position string, mate string);
    # CREATE INDEX position_index on data(position);
    conn = sqlite3.connect("MineMissedMates.db")
    curs = conn.cursor()

    for m in it:
        try:
            m.sanityCheck()
            m.populateStates()

            for (num,s) in enumerate(m.states):
                #print "on state >>>%s<<<" % s
                # no mates in the opening, please
                if num < 8:
                    print "skipping state %d since in opening" % num
                    continue

                (aState, bState) = string.split(s, ' | ')

                # is already seen? continue on
                for state in [aState, bState]:
                    print "considering state: %s" % state

                    curs.execute('select position from data where position=\"%s\"' % state)
                    row = curs.fetchone()
                    if row:
                        print "ALREADY SEEN THIS POSITION!"
                        continue

                    print "appealing to sunsetter..."
                    line = Sunsetter.searchMate(state)

                    if line:
                        print "FOUND MATE! %s" % line
                    else:
                        line = ''

                    statement = "insert or replace into data values ('%s', '%s')" % (state, line)
                    print "executing SQL: %s" % statement
                    curs.execute(statement)
                    conn.commit()

        except Exception as e:
            print e
            print "shit", sys.exc_info()[0]
            print traceback.print_tb(sys.exc_traceback)
