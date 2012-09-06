#!/usr/bin/python

# parse BPGN (game metadata + moves) into position strings

import os
import re
import sys

import Common
import BugLogic

class TokenizerTrailingException(Exception):
    pass
class TokenizerUnmatchedQuotesException(Exception):
    pass
class TokenizerUnmatchedBracketsException(Exception):
    pass
class TokenizerUnmatchedCurlyBracketsException(Exception):
    pass

# given a string from a BPGN file, return a list of tokens
# lowest level tokenizer - all symbols and stuff are split up

# difficulty:
# spaces delimit tokens normally
def tokenize(code):
    tokens = []
    curr = ''
    curr2 = ''

    while code:
        continueCurrentToken = 0

        # tags
        if code[0] == '[':
            m = re.match(r'^\[\w+ ".*?"\]', code)
            if not m:
                raise TokenizerUnmatchedBracketsException

            curr2 = m.group(0)
            code = code[len(curr2):]

        # comments
        elif code[0] == '{':
            m = re.match(r'^{.*?}', code)
            if not m:
                raise TokenizerUnmatchedCurlyBracketsException

            curr2 = m.group(0)
            code = code[len(curr2):]

        # encounter space? consume it, end current token
        elif code[0] in ' \n':
            code = code[1:]

        # otherwise its a normal character
        else:
            curr += code[0]
            code = code[1:]
            continueCurrentToken = 1

        # add what we've been working on?
        #
        if not continueCurrentToken:
            if curr:
                tokens.append(curr)
                curr = ''

        if curr2:
            tokens.append(curr2)
            curr2 = ''

    if curr:
        raise TokenizerTrailingException

    return tokens

if __name__ == '__main__':
    fp = open(sys.argv[1], 'r')
    code = fp.read()
    fp.close()

    tokens = tokenize0(code)

    for i,t in enumerate(tokens):
        print "token %03d: %s" % (i,t)


