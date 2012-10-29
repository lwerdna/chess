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
    bfenParts = string.split(bfen, ' ')

    # form args
    cmdAndArgs = ['/home/a/Projects/sunsetter/sunsetter', 'bfen'] + bfenParts
    output = runGetOutput(cmdAndArgs)
    print "it returned: " + output

    #
    maxMateValue = 0
    mateLine = ''
    lines = string.split(output, '\n')
    for line in lines:
        m = re.match(r'^.*val:\s+(\d+).*pos:\s+\d+ (.*)$', line)

        if m:
            (value, line) = m.group(1,2)
            value = int(value)

            if value > 18000:
                mateLine = line
                break

    return mateLine

###############################################################################
# main()
###############################################################################
if __name__ == '__main__':
    bfen = 'B3B2r/p6p/1pbp1p1N/1qbR4/2r1p3/4Pp1k/PP3P1P/n2Q1K1R/rbpP w - - 60 60'

    searchMate(bfen)

