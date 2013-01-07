#!/usr/bin/python

import re
import sys
import string

import Sjeng
import BugLogic
import BpgnParser

def holdingsDifference(x, y):
    while 1:
        if not x and not y:
            break

        if not x:
            return y[0]

        if not y:
            return x[0]

        x = x[1:]
        y = y[1:]


    return ''

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "syntax: %s <bpgn> <player>" % sys.argv[0]
        exit(-1)
   
    bpgnfile = sys.argv[1]
    player = sys.argv[2] 

    matchIterator = BpgnParser.MatchIteratorFile(bpgnfile)
    m = matchIterator.next()
    print m.tags

    # can find player in the match comments?
    playerChar = ''
    if m.tags['WhiteA'] == player:
        playerChar = 'A'
    elif m.tags['BlackA'] == player:
        playerChar = 'a'
    elif m.tags['WhiteB'] == player:
        playerChar = 'B'
    elif m.tags['BlackB'] == player:
        playerChar = 'b'
    else:
        print "couldn't find player in this game!"
        exit(-1)

    # just repeat the first part of the BPGN
    #
    print '[Event "%s"]' % (m.tags['Event'])
    del m.tags['Event']
    for k,v in m.tags.iteritems():
        print '[%s "%s"]' % (k,v)
    
    for c in m.comments:
        print '{%s}' % c
    
    # for each move, add a comment showing sjeng's analysis
    #
    m.populateStates()
    
    for i, move in enumerate(m.moves):
        comment = ''

        #print "move.player is -%s-" % move.player

        if move.player == playerChar:
            boardState = ''
            boardStates = string.split(m.states[i], ' | ')
            if playerChar in "Aa":
                boardState = boardStates[0]
            else:
                boardState = boardStates[1]

            #print "!!!!!!!!!!!!!!!!!!!"
            #print "!!!!!!!!!!!!!!!!!!!"
            #print "!!!!!!!!!!!!!!!!!!!"
            #print "!!!!!!!!!!!!!!!!!!!"
            #print "calling searchPossibilitiesBug(16, %s)" % boardState

            analysis = Sjeng.searchPossibilitiesBug(16, boardState)
    
            comment = '{\n%s\n}' % analysis
    
        print move, ' ', comment
   
    # repeat the last part of the BPGN
    #
    print ' ', m.tags['Result']
    
