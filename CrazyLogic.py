
import re

import Common
import ChessLogic

# this differs from ChessLogic due to the holdings board and promoted pieces marker '~'
def fenToBoardMap(fen):
    mapping = {}

    # split off the piece placement data
    [placesHoldings, mapping['activePlayer'], mapping['castleAvail'], mapping['enPassTarget'], \
        mapping['halfMoveClock'], mapping['fullMoveNum']] = re.split(' ', fen)

    m = re.match('^(.*)/(.*)$', placesHoldings)
    [places, mapping['holdings']] = [m.group(1), m.group(2)]

    squares = iter(Common.squaresSan)

    for c in places:
        # map normal pieces
        if re.match(r'^[PRQKNBprqknb]~?$', c):
            mapping[squares.next()] = c
        # map blank squares
        elif c in '12345678':
            for j in range(int(c)):
                mapping[squares.next()] = ' '
        # rank separator
        elif c == '/':
            pass
        # ???
        else:
            raise Exception('unknown character \'%s\' in fen' % c)

    return mapping

def boardMapToFen(bm):
    temp = ChessLogic.boardMapToFen(bm)

    # re-add the holdings area
    (places, rest) = re.split(r' ', temp, maxsplit=1)
    places = places + '/' + bm['holdings']
    return places + ' ' + rest

def nextState(fen, move, addHoldings=1):
    bm = fenToBoardMap(fen)
    bm = nextStateInternal(bm, move, addHoldings)
    return boardMapToFen(bm)

def nextStateInternal(bm, move, addHoldings=1):
    bm = bm.copy()

    fallThruChess = 1

    # filter out drops (normal chessboard doesn't understand)
    m = re.match('^([PRNBQK])@([a-h][1-8])\+?$', move)
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
            raise Exception("dropping non-existent piece!")

        # remove holdings
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

        # promoted pieces go back to pawns
        if re.match(r'^.*~$', dstPiece):
            dstPiece = {'w':'p', 'b':'P'}[bm['activePlayer']]

        # add to holdings
        if addHoldings:
            bm['holdings'] += Common.pieceChangeColorMap[dstPiece]

    # let Chess do the rest
    if fallThruChess:
        bm = ChessLogic.nextStateInternal(bm, move)

    return bm
