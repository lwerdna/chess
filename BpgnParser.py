#!/usr/bin/python

import re
import sys

class Move:
    def __init__(self, moveNum, moveTxt, time):
        self.moveNum = moveNum
        self.moveTxt = moveTxt
        self.time = time

    def __str__(self):
        answer = ''

        answer += '%s %s %s' % (self.moveNum, self.moveTxt, self.time)

        return answer

class Parser:
    def __init__(self, fpath):

        self.tags = {}
        self.comments = []
        self.moves = []

        self.parseFile(fpath)

    def parse(self, con):
        lines = con.split("\n")

        for line in lines:
            # skip empty lines
            if not line:
                continue

            # parse tags
            if re.match(r'^\[', line):
                for m in re.finditer(r'\[(.*?) "(.*?)"\]', line):
                    self.tags[m.group(1)] = m.group(2)
                continue

            # parse single-line comments
            m = re.match(r'^\s*{(.*)}\s*$', line)
            if m:
                self.comments.append(m.group(1)) 
                continue

            # parse movetext
            if re.match(r'^[12][abAB]\.', line):
                for m in re.finditer(r'(\d+[abAB])\. (.*?)({.*?})', line):
                    (moveNum, moveTxt, time) = m.group(1,2,3)

                    self.moves.append(Move(moveNum, moveTxt, time))

        #for i,s in enumerate(lines):
        #    print "[%d] %s\n" % (i,s)

    def parseFile(self, con):
        fp = open(sys.argv[1], 'r')
        contents = fp.read()
        fp.close()
        self.parse(contents)

    def __str__(self):
        answer = ''

        answer += "TAGS:\n"
        for tag,value in self.tags.iteritems():
            answer += "%s: \"%s\"\n" % (tag, value)

        answer += "COMMENTS:\n"
        for c in self.comments:
            answer += c + "\n"

        answer += "MOVES:\n"
        for m in self.moves:
            answer += str(m) + "\n"

        return answer

if __name__ == '__main__':
    p = Parser(sys.argv[1])

    print str(p)
