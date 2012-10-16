#!/usr/bin/python
import sys
import os
import tempfile
import re
import BpgnParser

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

    for m in it:
        try:
            m.sanityCheck()
            m.populateStates()

            for s in m.states:
                print s

            print ''.join(m.comments)  

        except:
            continue

        #break
