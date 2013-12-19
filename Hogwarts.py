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

# Hedwig makes random legal moves
# Neville makes random legal moves, but prefers captures, if available

# you practically have to spam xboard to get it to log anything
# $ xboard -debug -xdebug -debugMode True -nameOfDebugFile /tmp/xboard.log -fcp "./Hogwarts.py"

import re
import pdb
import sys
import random
import fileinput
import traceback

import Common
import ChessMove

boardState = {}

#--------------------------------------------------------------------------
# DEBUG
#--------------------------------------------------------------------------
def debugInit():
    fObj = open('/tmp/hogwarts.log', 'w')
    fObj.write('')
    fObj.close()

def debug(msg):
    msg = '# %s\n' % msg

    fObj = open('/tmp/hogwarts.log', 'a')
    fObj.write(msg)
    fObj.close()
    print msg,

#--------------------------------------------------------------------------
# MAIN
#--------------------------------------------------------------------------
if __name__ == '__main__':
    
    debugInit()

    profile = ''
    if sys.argv[1:]:
        profile = sys.argv[1]
    if not profile in ['Hedwig', 'Neville']:
        debug('unrecognized profile -%s-, defaulting to Hedwig' % profile)
        profile = 'Hedwig'
            

    boardState = x.fenToBoardMap(Common.initFEN)

    # debug
    #boardState = x.fenToBoardMap('rnbqkbnr/pppppp1p/8/6p1/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 0')
    #print boardState
    #moves = x.getLegalMoves(boardState)
    #for m in moves:
    #    print str(m)
    #sys.exit(-1)

    debug('entering input loop')
    while 1:
        try:
            sys.stdout.flush()

            debug('entry state: %s' % x.boardMapToFen(boardState))
    
            line = sys.stdin.readline()
            line = line.rstrip()
            debug('got line: -%s-' % line)
                
            #pdb.set_trace()
   
            ###################################################################
            # startup stuff
            #
            m = re.match('^protover (\d)$', line)
            if m:
                print 'feature' + \
                    ' debug=1' + \
                    ' myname=HOGWARTS' + \
                    ' sigint=0' + \
                    ' sigterm=0'
                continue
    
            # setboard?
            m = re.match('^setboard (.*)$', line)
            if m:
                boardState = x.fenToBoardMap(m.group(1))
                continue
    
            # new?
            m = re.match('^new$', line)
            if m:
                boardState = x.fenToBoardMap(Common.initFEN)
                continue

            ###################################################################
            # ending stuff
            #
            m = re.match('^result .*$', line)
            if m:
                pass

            m = re.match('^quit$', line)
            if m:
                break
    
            ###################################################################
            # a move?
            #
            moveLogic = ''
            if re.match('^[a-h][1-8][a-h][1-8]$', line):
                moveLogic = line
            elif re.match('[a-h][1-8][a-h][1-8][rnbq]$', line):
                moveLogic = line[0:-1] + '=' + line[-1]
            elif line == 'e1g1' or line =='e8g8':
                moveLogic = '0-0'
            elif line == 'e1c1' or line =='e8c8':
                moveLogic = '0-0-0'
            if(moveLogic):
                try:
                    boardState = x.nextStateInternal(boardState, moveLogic)
                except Exception, e:
                    print "Illegal move (%s): %s" % (str(e), line) 
                    type_, value_, traceback_ = sys.exc_info()
                    for tbLine in traceback.format_tb(traceback_):
                        debug(tbLine)
    
                # now that he has moved, we should move!
                moves = x.getLegalMoves(boardState)

                if moves:
                    #for m in moves:
                    #    print m
                    move = None

                    if profile == 'Hedwig':
                        move = moves[ int(random.random() * len(moves)) ]
                    elif profile == 'Neville':
                        captures = filter(lambda x: 'CAPTURE' in x.flags, moves)

                        print "captures are: "
                        print '\n'.join(map(lambda x: str(x), captures))

                        if captures:
                            move = captures[ int(random.random() * len(captures)) ]
                        else:
                            move = moves[ int(random.random() * len(moves)) ]
                        
                    moveText = 'move %s' % move.canonical 
                    debug("sending -%s-" % moveText)
                    print moveText
                
                    boardState = x.nextStateInternal(boardState, move.canonical)
                else:
                    # resign, somehow
                    pass

    
                #pdb.set_trace()

                continue

        except Exception, e:
            type_, value_, traceback_ = sys.exc_info()
            debug(str(type_))
            debug(str(value_))
            for tbLine in traceback.format_tb(traceback_):
                debug(tbLine)



