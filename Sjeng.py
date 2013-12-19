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

import re
import string
import subprocess

def runGetOutput(cmdAndArgs):
    print "opening on -%s-" % cmdAndArgs

    try:
        poObj = subprocess.Popen(cmdAndArgs, stdout=subprocess.PIPE);

        while(1):
            print "calling communicate..."
            text = poObj.communicate()[0]
            return text
    except:
        pass

def searchMate(time, bfen):
    # split the bfen into array
    # form args
    cmdAndArgs = ['./sjengshim', 'bughouse', str(time), bfen]
    output = runGetOutput(cmdAndArgs)
    print "it returned: " + output

    #
    maxMateValue = 0
    bestScore = -1;
    bestLine = ''
    mateLine = ''
    lines = string.split(output, '\n')

    # Sjeng maybe return earlier lines with supposed mate, but when further nodes are searched
    # you'll see that the opponent can counter... so we search for the very very last line
    for line in lines:
        # format is: <i_depth> <score> <elapsed> <nodes> <principle variation>
        m = re.match(r'^\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(.*)$', line)

        if m:
            (i_depth, score, elapsed, nodes, line) = m.group(1,2,3,4,5)

            if int(score) > bestScore:
                bestScore = int(score)
                bestLine = line

    #

    m = re.match(r'^\s*(.*#)\s*$', bestLine)
    if m:
        mateLine = m.group(1)

    return mateLine

def searchPossibilitiesBug(time, bfen):
    answer = ''

    # split the bfen into array
    # form args
    cmdAndArgs = ['./sjengshim', 'bughouse', str(time), bfen]
    output = runGetOutput(cmdAndArgs)
    #print "it returned: %s" % output
    lines = string.split(output, '\n')

    for line in lines:
        m = re.match(r'^\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(.*)$', line)

        if m:
            answer += line
            answer += "\n"

    return answer

###############################################################################
# main()
###############################################################################
if __name__ == '__main__':
    #bfen = 'B3B2r/p6p/1pbp1p1N/1qbR4/2r1p3/4Pp1k/PP3P1P/n2Q1K1R/rbpP w - - 60 60'
    bfen = 'r2q1rk1/p1p1Bppp/2p5/5N2/3n4/5Q2/P1P2PPP/R4RK1/NbbBnPpPp w Qq - 0 0'

    mate = searchMate(8, bfen)

    if mate:
        print "MATE FOUND! ", mate

