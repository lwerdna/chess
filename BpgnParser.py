#!/usr/bin/python

# parse BPGN (game metadata + moves) into position strings

import os
import re
import sys

import Common
import BugLogic
import BpgnTokenizer

###############################################################################
# Move
# - contains number, san, player of a move
###############################################################################

class Move:
    def __init__(self):
        self.player = ''    # 'a','A','b','B'
        self.moveNum = ''   # 1,2,3,...
        self.san = ''       # P@e7+
        self.comments = []  # {53.057}
        self.time = None    # 118.953
        self.flags = {}     # 'TIME_FORFEIT', etc.

    def addComment(self, comment):
        # time comment?
        if re.match(r'\d+\.\d+', comment):
            self.time = float(comment)
        # forfeit on time comment? (these are repeated in bughouse-db results)
        elif re.search('forfeits on time', comment):
            self.flags['TIME_FORFEIT'] = 1

        # add to list
        self.comments.append(comment)

    def __str__(self):
        answer = self.moveNum + self.player + '. ' + self.san

        if self.time:
            answer += "\nTIME: %s " % self.time

        answer += "\nFLAGS: "
        for k,v in self.flags.iteritems():
            answer += k + ' '

        answer += '\nCOMMENTS: '
        for c in self.comments:
            answer += ' {%s}' % c

        return answer

class MatchMovesOOOException(Exception):
    pass
class MatchZeroMovesException(Exception):
    pass

###############################################################################
# Match
# - contains tags, comments, moves, and states of a bughouse chess match
# - is able to load itself from bpgn match text
###############################################################################
class Match:
    def __init__(self):
        self.initState = Common.initBugFEN
        self.moves = []
        self.tags = {}
        self.comments = []
        self.states = [self.initState]

        self.path = ''

        self.movesSeenBefore = {}

    def populateState(self, i):
        while len(self.moves) >= len(self.states):
            self.states += ['']
        
        move = self.moves[i]

        # exceptions (repeated moves due to time forfeiture, etc.) just carry state along...
        if 'TIME_FORFEIT' in move.flags:
            self.states[i+1] = self.states[i]
        # valid moves progress the state
        else:
            self.states[i+1] = BugLogic.nextState(self.states[i], move.player, move.san)

    def populateStates(self):
        self.states = [self.initState]

        for i in range(len(self.moves)):
            self.populateState(i)

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

    def parseBpgn(self, text):
        tokens = BpgnTokenizer.tokenize(text)

        currMove = 0

        for token in tokens:
            #print "on token: -%s-" % token

            # tag tokens
            m = re.match(r'\[(.*?) "(.*?)"\]', token)
            if m:
                self.tags[m.group(1)] = m.group(2)

                continue

            # comment tokens
            m = re.match('^{(.*)}$', token)
            if m:
                # if we're in the moves section, comment applies to a move
                if self.moves:
                    self.moves[-1].addComment(m.group(1))
                else:
                    self.comments.append(m.group(1))

                continue

            # result tokens
            m = re.match(r'^.*(0-0$|0-1$|1-0$|1/2-1/2$|\*$)', token)
            if m:
                self.result = token

                if token != tokens[-1]:
                    raise Exception("expected match result")

                continue

            # move number token
            m = re.match(r'(\d+)([abAB])\.', token)
            if m:
                move = Move()
                move.moveNum = m.group(1)
                move.player = m.group(2)
                self.moves.append(move)

            # normal move (SAN)
            m = re.match(Common.regexSan, token)
            if m:
                self.moves[-1].san = token


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
class MatchIteratorFile:
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
        match = Match()
        match.path = self.path
        match.parseBpgn(matchText)
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
class MatchIteratorDir:
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

        m.populateStates()
        #print str(m)

        #for s in m.states:
        #    print s

        goodGamesCount += 1
        #raw_input("hit enter for next game")
        print "%d/%d games are good (%02.2f%%)" % (goodGamesCount, gamesCount, 100.0*goodGamesCount/gamesCount)


