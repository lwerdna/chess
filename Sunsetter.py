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

