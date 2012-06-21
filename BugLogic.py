#!/usr/bin/python

# a Bughouse Board is two Crazyhouse Boards, one flipped

import re
import Tkinter

import Common
import ChessLogic
import CrazyLogic

def fenToBoardMap(fen):
    [fenA, fenB] = fen.split(' | ')

    mapping = {}
    mapping['boardA'] = CrazyLogic.fenToBoardMap(fenA)
    mapping['boardB'] = CrazyLogic.fenToBoardMap(fenB)

    return mapping
    
def boardMapToFen(bm):
    return ' | '.join([ \
        CrazyLogic.boardMapToFen(bm['boardA']), \
        CrazyLogic.boardMapToFen(bm['boardB']) \
        ])

def nextState(fen, player, move):
    bm = fenToBoardMap(fen)
    bm = nextStateInternal(bm, player, move)
    return boardMapToFen(bm)

def nextStateInternal(bm, player, move):
    bm = bm.copy()

    playerToBoard = {'a':bm['boardA'], 'A':bm['boardA'], 'b':bm['boardB'], 'B':bm['boardB']}
    playerToBoardOpp = {'a':bm['boardB'], 'A':bm['boardB'], 'b':bm['boardA'], 'B':bm['boardA']}

    # parse move
    m = re.match(Common.regexSan, move)
    if not m:
        raise Exception("cannot parse move: %s" % move)

    # but for captures, we've turned off CrazyBoard's transfer and instead
    # transfer across the table (board A <-> board B)
    # and unlike CrazyBoard's flip of the color, the captured piece's color is preserved in bug
    m = re.search('x([a-h][1-8])', move)
    if m:
        playerToBoardOpp[player]['holdings'] += playerToBoard[player][m.group(1)]

    # CrazyBoard handles removal from holdings during piece drop
    temp = CrazyLogic.nextStateInternal(playerToBoard[player], move, False)

    if player in 'Aa':
        bm['boardA'] = temp
    else:
        bm['boardB'] = temp

    return bm

