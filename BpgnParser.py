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

# parse BPGN (game metadata + moves) into position strings

import os
import re
import sys

import Common
import ChessMove
import PgnTokenizer


###############################################################################
# Match
# - contains tags, comments, moves, and states of a bughouse chess match
# - is able to load itself from bpgn match text
###############################################################################
class PgnChessMatch:
    def __init__(self):
        self.initState = Common.initChessFEN
        self.moves = []
        self.tags = {}
        self.comments = []
        self.states = [self.initState]


    def incrMoveNum(self, fullMove):
        old = fullMove

        m = re.match(r'^(\d+)([AaBb])$', fullMove)
        [num, letter] = [int(m.group(1)), m.group(2)]
        
        if letter in 'ab':
            num += 1

        letter = {'A':'a', 'a':'A', 'B':'b', 'b':'B'}[letter]

        new = str(num) + letter

        #print "incremented from %s to %s" % (old, new)

        return new

    def sanityCheck(self):
        # does the game have ANY moves in it?
        if len(self.moves) == 0:
            raise MatchZeroMovesException("no moves recorded")

        # does the game have missing/out-of-order moves in it?
        expectA = '1A'
        expectB = '1B'
        for m in self.moves:

            if 'TIME_FORFEIT' in m.flags:
                continue

            # bughouse-db games store a repeated move at the end when
            # that player forfeits on time

            fullMove = m.moveNum + m.player

            if fullMove == expectA:
                expectA = self.incrMoveNum(expectA)
            elif fullMove == expectB:
                expectB = self.incrMoveNum(expectB)
            else:
                raise MatchMovesOOOException("expected move %s or %s (got instead:\n %s)" % \
                    (expectA, expectB, str(m)))

    # - parses, populates the tags member
    # - parses, populates the moves member
    # - parses, populates the comments member
    # - calculates the states member
    #
    def parsePgn(self, text):
        tokens = PgnTokenizer.tokenize(text)
        moveNum = 1
        player = 'W'

        while tokens:
            token = tokens.pop(0)

            print "on token: -%s-" % token

            # tag tokens eg: [Event "May 2013 Tourney"]
            m = re.match(r'\[(.*?) "(.*?)"\]', token)
            if m:
                self.tags[m.group(1)] = m.group(2)
                continue

            # comment tokens eg: { good move! also consider Rxe8 }
            m = re.match('^{(.*)}$', token)
            if m:
                # if we're in the moves section, comment applies to a move
                if self.moves:
                    self.moves[-1].addComment(m.group(1))
                # else it applies to the match comments
                else:
                    self.comments.append(m.group(1))

                continue

            # result tokens eg: 0-1
            m = re.match(Common.regexResults, token)
            if m:
                self.result = token

                if tokens:
                    raise Exception("result token was not the final token! next is: " + tokens[0])

                continue

            # move number token eg: 34.
            m = re.match(r'(\d+)\.', token)
            if m:
                if moveNum == int(m.group(1)) + 1:
                    raise Exception("out of order move number: " + token)

                moveNum += 1;
                player = 'W'

            # normal move (SAN)
            m = re.match(Common.regexSanChess, token)
            if m:
                move = ChessMove.ChessMove()
                move.moveNum = moveNum
                move.player = player
                move.san = token
                self.moves.append(move)

                player = {'W':'B', 'B':'W'}[player]

        # calculate all board states
        self.states = [self.initState] 

        for move in self.moves:
            # exceptions (repeated moves due to time forfeiture, etc.) just carry state along...
            if 'TIME_FORFEIT' in move.flags:
                self.states.append(self.states[-1])
                continue
                
            currState = self.states[-1]
            nextState = x.nextState(self.states[-1], move.san)

            print "current state: " + currState
            print "next state: " + nextState

            self.states.append(nextState)

    def __str__(self):
        answer = ''
        #answer = '%s[%s],%s[%s] vs %s[%s],%s[%s]\n' % ( \
        #    self.tags['WhiteA'], self.tags['WhiteAElo'], self.tags['BlackA'], self.tags['BlackAElo'], \
        #    self.tags['BlackB'], self.tags['BlackBElo'], self.tags['WhiteA'], self.tags['WhiteAElo'] \
        #)

        answer += "TAGS:\n"
        for tag,value in self.tags.iteritems():
            answer += "%s: \"%s\"\n" % (tag, value)
        answer += "COMMENTS:\n"
        for c in self.comments:
            answer += c + "\n"
        answer += "MOVES (%d total):\n" % len(self.moves)
        for m in self.moves:
            answer += str(m) + "\n"
        return answer

###############################################################################
# MatchIteratorFile
# - return matches from file containing multiple matches
# - basically, split the text around '[Event "..."]' tags
###############################################################################
class PgnChessMatchIteratorFile:
    def __init__(self, path):
        self.path = path

        self.fp = open(path, 'r')
        self.lineNum = -1

    def __iter__(self):
        self.fp.seek(0, 0)
        self.lineNum = -1
        return self

    def peekLine(self, doStrip=1):
        line = self.fp.readline()
        self.fp.seek(-1*len(line), 1)

        if doStrip:
            line = line.rstrip()

        return line

    def readLine(self):
        self.lineNum += 1
        temp = self.fp.readline()
        #print "read: %s" % temp
        return temp

    def consumeNewLines(self):
        while 1:
            line = self.peekLine(False)
            if not line:
                return False
            if not re.match(r'^\s+$', line):
                break
            self.readLine()
        return True

    # strategy here is simple: consume lines until an Event tag is found
    # in other words, Event tags delimit the matches
    def next(self):
        if not self.consumeNewLines():
            raise StopIteration
        
        matchText = self.readLine()

        if not re.match(r'^\[Event', matchText):
            raise Exception(("expected Event tag at %s:%d\n" + \
                "(instead got: %s)") % (self.path, self.lineNum, matchText))

        # so long as the next line is not an Event tag, add to current match
        while 1:
            line = self.peekLine()
            if not re.match(r'^\[Event', line):
                matchText += '\n' + line
                if not self.readLine():
                    break
            else:
                break

        # return a match
        match = PgnChessMatch()
        match.path = self.path
        match.parsePgn(matchText)
        return match

    def __del__(self):
        if self.fp:
            self.fp.close()

        self.fp = None

###############################################################################
# MatchIteratorDir
# - return matches from a directory containing files
# - basically, loop over MatchIteratorFile for every file in a directory
###############################################################################
class PgnChessMatchIteratorDir:
    def __init__(self, path):
        self.walkObj = os.walk(path)
        self.matchIterFileObj = None
        self.filesList = []

    def __iter__(self):
        return self

    def next(self):
        while 1:
            # first level: does the file iterator still have something left?
            if self.matchIterFileObj:
                try:
                    return self.matchIterFileObj.next()
                except StopIteration: 
                    self.matchIterFileObj = None
    
            # second level, is current list of files exhausted? can we create a new
            # file iterator?
            if self.filesList:
                self.matchIterFileObj = MatchIteratorFile(self.filesList.pop())
                continue
    
            # third level: no file iterator, no files list, descend!
            # purposely don't trap exception: StopIterations should bubble up and tell
            # caller that we're done
            (root, subFolder, files) = self.walkObj.next()
    
            for f in files:
                (dummy, ext) = os.path.splitext(f)
                if ext == '.bpgn':
                    self.filesList.append(os.path.join(root, f))

###############################################################################
# main()
###############################################################################
if __name__ == '__main__':
    gamesCount = 0
    goodGamesCount = 0

    path = sys.argv[1]
    it = None
    if os.path.isfile(path):
        it = MatchIteratorFile(path)
    elif os.path.isdir(path):
        it = MatchIteratorDir(path)
    else:
        raise Exception("WTF?")

    for m in it:
        gamesCount += 1

        try:
            m.sanityCheck()
        except MatchMovesOOOException as e:
            print "%s: skipping match due to out of order (or missing) moves\n%s\n%s" % (m.path, '\n'.join(m.comments), str(e))
            continue
        except MatchZeroMovesException as e:
            print "%s: skipping match due to it being empty (no moves whatsoever)\n%s\n%s" % (m.path, '\n'.join(m.comments), str(e))
            continue

        for s in m.states:
            print s

        goodGamesCount += 1
        #raw_input("hit enter for next game")
        print "%d/%d games are good (%02.2f%%)" % (goodGamesCount, gamesCount, 100.0*goodGamesCount/gamesCount)


