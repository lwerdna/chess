#!/usr/bin/python

import re
import string
import subprocess

def runGetOutput(cmdAndArgs):
    #print "opening on -%s-" % cmdAndArgs

    try:
        poObj = subprocess.Popen(cmdAndArgs, stdout=subprocess.PIPE);

        while(1):
            print "calling communicate..."
            text = poObj.communicate()[0]
            return text
    except:
        pass

def searchMate(bfen):
    # split the bfen into array
    # form args
    cmdAndArgs = ['./sjengshim', 'bughouse', bfen]
    output = runGetOutput(cmdAndArgs)
    print "it returned: " + output

    #
    maxMateValue = 0
    bestLine = ''
    mateLine = ''
    lines = string.split(output, '\n')

    # Sjeng maybe return earlier lines with supposed mate, but when further nodes are searched
    # you'll see that the opponent can counter... so we search for the very very last line
    for line in lines:
        # format is: <i_depth> <score> <elapsed> <nodes> <principle variation>
        m = re.match(r'^\s+\d+\s+\d+\s+\d+\s+\d+\s+(.*)$', line)

        if m:
            bestLine = m.group(1)

    m = re.match(r'^\s*(.*#)\s*$', bestLine)
    if m:
        mateLine = m.group(1)

    return mateLine

###############################################################################
# main()
###############################################################################
if __name__ == '__main__':
    #bfen = 'B3B2r/p6p/1pbp1p1N/1qbR4/2r1p3/4Pp1k/PP3P1P/n2Q1K1R/rbpP w - - 60 60'
    bfen = 'r2q1rk1/p1p1Bppp/2p5/5N2/3n4/5Q2/P1P2PPP/R4RK1/NbbBnPpPp w Qq - 0 0'

    mate = searchMate(bfen)

    if mate:
        print "MATE FOUND! ", mate

