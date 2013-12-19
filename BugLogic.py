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

# a Bughouse Board is two Crazyhouse Boards, one flipped

import re
import Tkinter

import Common
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
        pieceCode = playerToBoard[player][m.group(1)]

        # look for en-passant
        if pieceCode == ' ':
            # then is it the en-passant target square?
            if m.group(1) != playerToBoard[player]['enPassTarget']:
                raise Exception("capturing onto empty square!")
                
            pieceCode = {'a':'P', 'b':'P', 'A':'p', 'B':'p'}[player]

        # promoted pieces back to pawns
        if re.match(r'^(.*)~$', pieceCode):
            pieceCode = {'a':'P', 'b':'P', 'A':'p', 'B':'p'}[player]

        playerToBoardOpp[player]['holdings'] += pieceCode

    # CrazyBoard handles removal from holdings during piece drop
    temp = CrazyLogic.nextStateInternal(playerToBoard[player], move, False)

    if player in 'Aa':
        bm['boardA'] = temp
    else:
        bm['boardB'] = temp

    return bm

