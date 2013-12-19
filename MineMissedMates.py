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

import BpgnParser
#import Sunsetter
import Sjeng

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

                    print "appealing to Sjeng..."
                    line = Sjeng.searchMate(8, state)

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
