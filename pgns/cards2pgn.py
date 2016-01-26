#!/usr/bin/python

# converts the "cards" format of chess position file which is:
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

sys.path.append('..')

import Common
import PgnTokenizer

def parseCards(fileName):
    cards = []

    # setup
    regexFenQuick = Common.regexFenPosition[:-1] + r' [wb]'

    # state machine variables
    state = 'WAIT'
    currFen = currQuestion = currAnswer = None
    
    # collect lines from all files
    lines = []
    fobj = open(fileName, 'r')
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
            elif re.match(regexFenQuick, line):
                currFen = line + ' KQkq - 0 1'
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

def isValidMoveText(text):
    ok = 1

    try:
        tokens = PgnTokenizer.tokenize(text)
       
        for token in tokens:
            # 1) comments
            if re.match('^{(.*)}$', token):
                pass
            # 2) move numbers
            elif re.match(r'(\d+)\.', token):
                pass
            # 3) normal move (SAN)
            elif re.match(Common.regexSanChess, token):
                pass
            # 4)  result
            elif re.match(Common.regexResults, token):
                pass
            # 5) nope
            else:
                print "token -%s- is not allowed" % token
                ok = 0
                break
    except:
        pass

    return ok

if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise Exception("missing <infile> <outfile> params")

    (inFile, outFile) = sys.argv[1:]


    cards = parseCards(inFile)

    fObj = open(outFile, 'w')

    for (i,card) in enumerate(cards):
        (fen, question, answer) = (card['fen'], card['question'], card['answer'])

        # detect result (Result tag must match end of movetext)

        result = '*'
        moveText = ''
        if not answer or re.match(r'^\s*$', answer):
            moveText = '{ null } *'
        elif isValidMoveText(answer):
            append = True

            try:
                ansToks = PgnTokenizer.tokenize(answer)
                if ansToks and re.match(Common.regexResults, ansToks[-1]):
                    result = ansToks[-1]
                    append = False
            except:
                print "answer: -%s- is not valid movetext, commenting it..." % answer
                pass
                
            if append:
                moveText = '%s %s' % (answer, result)
            else:
                moveText = answer
        else:
            moveText = '{ %s } *' % answer

        pgnEntry = ''
        # mandatory tags (seven tag roster)
        pgnEntry += '[Event "Event %d"]\n' % (i+1)
        pgnEntry += '[Site "Site"]\n'
        pgnEntry += '[Date "1-1-2000"]\n'
        pgnEntry += '[Round "Round"]\n'
        pgnEntry += '[White "white"]\n'
        pgnEntry += '[Black "black"]\n'
        pgnEntry += '[Result "%s"]\n' % result
        # initial board position tag
        pgnEntry += '[FEN "%s"]\n' % fen
        # our custom tag
        pgnEntry += '[Question "%s"]\n' % question
        pgnEntry += '\n'
        # movetext section
        pgnEntry += '%s\n\n' % moveText

        fObj.write(pgnEntry)

    fObj.close()
        
