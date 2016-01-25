#!/usr/bin/python

import PgnParser

it = PgnParser.PgnChessMatchIteratorFile('pec.pgn')

fobj = open('pec.cards', 'w')

for m in it:
    fobj.write('%s\n' % m.initState.toFEN())
    fobj.write('%s: %s to move\n' % (m.tags['White'], {'w':'white','b':'black'}[m.initState.activePlayer]))
    fobj.write('%s: %s\n' % (m.tags['Black'], ' '.join(map(lambda x: str(x), m.moves))))
    fobj.write('\n')

fobj.close()
    
