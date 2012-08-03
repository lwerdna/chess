#!/usr/bin/python

import re
import sys
import BpgnParser
import BugLogic

def holdingsDifference(x, y):
    while 1:
        if not x and not y:
            break

        if not x:
            return y[0]

        if not y:
            return x[0]

        x = x[1:]
        y = y[1:]


    return ''


matchIterator = BpgnParser.MatchIteratorFile(sys.argv[1])
m = matchIterator.next()

print '[Event "%s"]' % (m.tags['Event'])
del m.tags['Event']
for k,v in m.tags.iteritems():
    print '[%s "%s"]' % (k,v)

for c in m.comments:
    print '{%s}' % c

m.populateStates()

lastState = ''
for i, s in enumerate(m.states):

    if not lastState:
        lastState = s
        continue
   
    comment = ''    
    if re.search(r'x', m.moves[i-1].san):
        bmLast = BugLogic.fenToBoardMap(lastState)
        bmThis = BugLogic.fenToBoardMap(s)
    
        xfer = holdingsDifference(bmThis['boardA']['holdings'], bmLast['boardA']['holdings'])
        if xfer:
            comment += '{captured on B: ' + xfer + '} '
        xfer = holdingsDifference(bmThis['boardB']['holdings'], bmLast['boardB']['holdings'])
        if xfer:
            comment += '{captured on A: ' + xfer + '} '

        comment = comment.lstrip()
        comment = comment.rstrip()

    print m.moves[i-1], ' ', comment

#    print('left holdings before: ' + ''.join(list(leftHoldings)))
#    print('left holdings after: ' + ''.join(list(leftHoldings_)))
#    print('right holdings before: ' + ''.join(list(rightHoldings)))
#    print('right holdings after: ' + ''.join(list(rightHoldings_)))

    lastState = s

print ' ', m.tags['Result']

