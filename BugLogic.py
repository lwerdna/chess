#!/usr/bin/python

# a Bughouse Board is two Crazyhouse Boards, one flipped

import re
import Tkinter

import Common
import ChessLogic
import CrazyLogic

def fenToBoardMap(fen):
    print "processing fen: -%s-" % fen
    [fenA, fenB] = fen.split(' | ')

    mapping = {}
    mapping['boardA'] = CrazyLogic.fenToBoardMap(fenA)
    mapping['boardB'] = CrazyLogic.fenToBoardMap(fenB)

    return mapping
    
def boardMapToFen(bm):
    return ' | '.join([ \
        CrazyLogic.boardMapToFen(bm['boardA']), \
        CrazyLogic.boardMapToFen(bm['boardA']) \
        ])

def nextState(fen, move):
    bm = fenToBoardMap(fen)
    bm = nextStateInternal(bm, move)
    return boardMapToFen(bm)

def nextStateInternal(bm, move):
    bm = bm.copy()

    playerToBoard = {'a':bm['boardA'], 'A':bm['boardA'], 'b':bm['boardB'], 'B':bm['boardB']}
    playerToBoardOpp = {'a':bm['boardB'], 'A':bm['boardB'], 'b':bm['boardA'], 'B':bm['boardA']}

    # we strip off player indicator to decide which board to send the move to
    regex = r'^\d+([AaBb])\. (.*?)$'
    m = re.match(regex, move)
    if not m:
        raise Exception("missing player indicator for move -%s-" % move)

    [player, move] = [m.group(1), m.group(2)]

    # parse move
    m = re.match(Common.regexSan, move)
    if not m:
        raise Exception("cannot parse move: %s" % move)

    # BPGN uses capital letters for all source pieces in a move
    # PGN distinguishes, using capital letters for white pieces, lowercase for black
    # thus translation is necessary before sending the move down
    if not (m.group('qCastle') or m.group('kCastle')):
        srcPiece = m.group('srcPiece') or {'A':'P','B':'P','a':'p','b':'p'}[player]
            
        if player in 'ab':
            srcPiece = srcPiece.lower()
        else:
            srcPiece = srcPiece.upper()

        move = ''.join(filter(lambda x: x, \
            [srcPiece, m.group('srcHint'), m.group('action'), m.group('dstSquare'), \
                m.group('promote'), m.group('check')]))
    
    # but for captures, we've turned off CrazyBoard's transfer and instead
    # transfer across the table (board A <-> board B)
    # and unlike CrazyBoard's flip of the color, the captured piece's color is preserved in bug
    m = re.search('x([a-h][1-8])', move)
    if m:
        playerToBoardOpp[player]['holdings'] += playerToBoard[player][m.group(1)]

    # CrazyBoard handles removal from holdings during piece drop
    temp = CrazyLogic.nextStateInternal(playerToBoard[player], move)
    playerToBoard[player] = temp

    print "!!!!!!!!"
    print CrazyLogic.boardMapToFen(temp)

    return bm

