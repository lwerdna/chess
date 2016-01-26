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

# parse PGN (game metadata + moves) into position strings

import os
import re
import sys
import Common

class TokenizerTrailingException(Exception):
    pass
class TokenizerUnmatchedQuotesException(Exception):
    pass
class TokenizerUnmatchedBracketsException(Exception):
    pass
class TokenizerUnmatchedCurlyBracketsException(Exception):
    pass
class TokenizerMalformedMoveNumberException(Exception):
    pass
class TokenizerMalformedMoveException(Exception):
    pass

# given a string from a PGN file, return a list of tokens
# lowest level tokenizer - all symbols and stuff are split up

def tokenize(code):
    tokens = []

    while code:
        m = ''
        snippet = code[0:16] + "..."

        #print "code[0] is: " + repr(code[0])

        # tags
        if code[0] == '[':
            m = re.match(r'^\[\w+ ".*?"\]', code)
            if not m:
                raise TokenizerUnmatchedBracketsException(snippet)

        # comments
        elif code[0] == '{':
            m = re.match(r'^{.*?}', code)
            if not m:
                raise TokenizerUnmatchedCurlyBracketsException(snippet)

        # result
        # this must come before move number (forms intersect)
        elif re.match(Common.regexResults, code):
            m = re.match(Common.regexResults, code)

        # move number
        elif code[0].isdigit():
            # black (digit followed by 3 periods)
            m = re.match(r'^\d+\.\.\.', code)
            if not m:
                # white (digit followed by 1 period)
                m = re.match(r'^\d+\.', code)
                if not m:
                    raise TokenizerMalformedMoveNumberException(snippet)

        # ignore spaces
        elif re.match('\s', code[0]):
            code = code[1:]
            continue

        # otherwise it must be a move
        else:
            m = re.match(Common.regexSanChess, code)
            if not m:
                raise TokenizerMalformedMoveException(snippet)

        tokens.append(m.group(0))
        code = code[len(m.group(0)):]

    return tokens

if __name__ == '__main__':
    fp = open(sys.argv[1], 'r')
    code = fp.read()
    fp.close()

    tokens = tokenize(code)

    for i,t in enumerate(tokens):
        print "token %08d: %s" % (i,t)


