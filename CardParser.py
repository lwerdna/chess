#!/usr/bin/python

# reads "cards" format of chess position file(s) which is:
#
# <fen>
# [<question>]
# [<answer>]
# [#<comment>]
# 
# where <fen> is a complete or incomplete fen string
# question might be some text like "white to move, mate in 3"
# answer might be some text like "Qd5" etc...
# comments are preceeded by pound/hash # and have no effect
#
# from this, flash cards can be generated, or you can play cards against a computer

import os
import sys

import re

import Common

def parseCards(fileNames):
    cards = []

    # state machine variables
    state = 'WAIT'
    currFen = currQuestion = currAnswer = None
    
    # collect lines from all files
    lines = []
    for fName in fileNames:
        fobj = open(fName, 'r')
        lines += fobj.readlines()
        fobj.close()

    lines = map(lambda x: x.strip(), lines)

    # loop over lines
    for line in lines:
        # in all states, skip comments
        if re.match(r'^#', line): continue

        # wait state:
        #  - skip blank lines -> reset state
        #  - consume FEN string -> incr state
        if state == 'WAIT':
            if re.match(r'^\s*$', line): continue
            # must be FEN
            if re.match(Common.regexFen, line):
                currFen = line
            elif re.match(Common.regexFenLazy, line):
                currFen = line + ' w KQkq - 0 1'
            else:
                raise Exception("expected FEN string, got: -%s-" % line)

            state = 'WAITQUESTION'
            continue

        # question state:
        #  - blank lines terminate the current position -> reset state
        #  - anything else is the question -> incr state
        if state == 'WAITQUESTION':
            if re.match(r'^\s+$', line):
                cards.append({'fen':currFen, 'question':currQuestion, 'answer':currAnswer})
                currFen = currQuestion = currAnswer = None
                state = 'WAIT'
                continue

            currQuestion = line
            state = 'WAITANSWER'
            continue

        # answer state:
        #  - blank lines terminate the current position -> reset state
        #  - anything else is the question -> reset state
        if state == 'WAITANSWER':
            if not re.match(r'^\s+$', line):
                currAnswer = line

            cards.append({'fen':currFen, 'question':currQuestion, 'answer':currAnswer})
            currFen = currQuestion = currAnswer = None
            state = 'WAIT'
            continue

    return cards

if __name__ == '__main__':
    fNames = sys.argv[1:]

    cards = parseCards(fNames)

    for (i,card) in enumerate(cards):
        print 'card %d:' % i
        print "FEN: %s" % card['fen']
        print "  Q: %s" % card['question']
        print "  A: %s" % card['answer']
        print ''

