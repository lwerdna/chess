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


import re

import Common

# this differs from ChessLogic due to the holdings board and promoted pieces marker '~'
def fenToBoardMap(fen):
    # board map is like:
    # bm['activePlayer'] : 'w'
    # bm['castleAvail'] : 'KQkq'
    # bm['enPassTarget'] : 'e3'
    # bm['halfMoveClock'] : 0
    # bm['fullMoveClock'] : 2
    # bm['a8'] = 'r'
    # bm['b8'] = 'n'
    # ...
    mapping = {}

    # split off the piece placement data
    [placesHoldings, mapping['activePlayer'], mapping['castleAvail'], mapping['enPassTarget'], \
        mapping['halfMoveClock'], mapping['fullMoveNum']] = re.split(' ', fen)

    m = re.match('^(.*)/(.*)$', placesHoldings)
    [places, mapping['holdings']] = [m.group(1), m.group(2)]

    squares = iter(Common.squaresSan)

    while places:
        # map normal pieces (possibly marked with promotion)
        m = re.match(r'^([PRQKNBprqknb]~?)', places)
        if m:
            mapping[squares.next()] = m.group(0)
            places = places[len(m.group(0)):]

        # map blank squares (indicated by number)
        elif places[0] in '12345678':
            for j in range(int(places[0])):
                mapping[squares.next()] = ' '
            places = places[1:]

        # rank separator (ignored)
        elif places[0] == '/':
            places = places[1:]

        # ???
        else:
            raise Exception('unknown character \'%s\' in fen' % places[0])

    return mapping

def boardMapToFen(bm):
    temp = cl.boardMapToFen(bm)

    # re-add the holdings area
    (places, rest) = re.split(r' ', temp, maxsplit=1)
    places = places + '/' + bm['holdings']
    return places + ' ' + rest

def nextState(fen, move, addHoldings=1):
    bm = fenToBoardMap(fen)
    bm = nextStateInternal(bm, move, addHoldings)
    return boardMapToFen(bm)

def nextStateInternal(bm, move, addHoldings=1, ghostHoldings=0):
    bm = bm.copy()

    fallThruChess = 1

    # filter out drops (normal chessboard doesn't understand)
    m = re.match('^([PRNBQK])@([a-h][1-8])[\+#]?$', move)
    if m:
        srcPiece = m.group(1)

        if bm['activePlayer'] == 'w':
            srcPiece = srcPiece.upper()
        else:
            srcPiece = srcPiece.lower()

        dstSquare = m.group(2)

        if bm[dstSquare] != ' ':
            raise Exception("drop on non-empty square -%s-" % dstSquare)
        if srcPiece in 'Pp' and dstSquare[1] in '18':
            raise Exception("illegal pawn drop on rank 1 or 8")

        if not srcPiece in bm['holdings']:
            if ghostHoldings:
                # it's ok! we allow ghost drops
                pass
            else:
                raise Exception("dropping non-existent piece!")
        else:
            bm['holdings'] = re.sub(srcPiece, '', bm['holdings'], count=1)

        # add to board
        bm[dstSquare] = srcPiece

        # toggle turn
        bm['activePlayer'] = {'b':'w', 'w':'b'}[bm['activePlayer']]

        fallThruChess = 0

    # do captures if necessary (taking into account promotion)
    m = re.search('x([a-h][1-8])', move)
    if m:
        dstSquare = m.group(1)
        
        dstPiece = bm[dstSquare]

        # look for en-passant
        if dstPiece == ' ':
            # then is it the en-passant target square?
            if dstSquare != bm['enPassTarget']:
                raise Exception("capting onto empty square!")
                
            dstPiece = Common.casePieceByPlayer('p', bm['activePlayer'])

        # promoted pieces go back to pawns
        m = re.match(r'^(.*)~$', dstPiece)
        if m:
            dstPiece = Common.casePieceByPlayer('p', bm['activePlayer'])

            # strip the ~ (which Chess wouldn't understand)
            bm[dstSquare] = m.group(1)

        # add to holdings (true for crazy, false for bug (goes to partner board instead)
        if addHoldings:
            bm['holdings'] += Common.pieceChangeColorMap[dstPiece]

    # let Chess do the rest
    if fallThruChess:
        bm = cl.nextStateInternal(bm, move)

    # if it was a promotion, mark the promoted piece with '~'
    m = re.search('([a-h][1-8])=([QKPRBN])', move)
    if m:
        bm[m.group(1)] += '~'

    return bm
