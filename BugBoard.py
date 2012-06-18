#!/usr/bin/python

# a Bughouse Board is two Crazyhouse Boards, one flipped

import re
import Tkinter

import ChessBoard
import CrazyBoard

class BugBoard(Tkinter.Frame):
    def __init__(self, parent, pieceWidth=48, pieceHeight=48):
        Tkinter.Frame.__init__(self, parent)

        self.parent = parent

        # two boards
        self.boardA = CrazyBoard.CrazyBoard(self, pieceWidth, pieceHeight)
        self.boardB = CrazyBoard.CrazyBoard(self, pieceWidth, pieceHeight)

        # turn CrazyHouse transfer off on both boards (we direct pieces to different boards)
        self.boardA.transferPieces = 0
        self.boardB.transferPieces = 0
        self.boardB.flip()

        self.width = 2*self.boardA.width
        self.height = 2*self.boardA.height

        self.boardA.grid(row=0, column=0)
        self.boardB.grid(row=0, column=1)

    def execMoveSan(self, move):
        playerToBoard = {'a':self.boardA, 'A':self.boardA, 'b':self.boardB, 'B':self.boardB}
        playerToBoardOpp = {'a':self.boardB, 'A':self.boardB, 'b':self.boardA, 'B':self.boardA}

        # we strip off player indicator to decide which board to send the move to
        regex = r'^\d+([AaBb])\. (.*?){\d+\.\d+}$'

        m = re.match(regex, move)
        if not m:
            raise Exception("invalid move -%s-" % move)

        [player, move] = [m.group(1), m.group(2)]

        # BPGN uses capital letters for all source pieces in a move
        # PGN distinguishes, using capital letters for white pieces, lowercase for black
        # thus translation is necessary before sending the move down
        if move != 'O-O' and move != 'O-O-O':
            # note the difference here between this and the normal SAN movetext
            # - source pieces are always capitalized (differentiates between b for
            #   bishop and b rank source hint
            # - "action" character @ added for drop
            regex = r'(?P<srcPiece>[PNBRQK])?' + \
                    r'(?P<srcHint>[a-h1-8]{1,2})?' + \
                    r'(?P<action>[x@])?' + \
                    r'(?P<dstSquare>[a-h][1-8])' + \
                    r'(?P<promote>=[PNBRQKpnbrqk])?' + \
                    r'(?P<check>[\+#])?'
    
            m = re.match(regex, move)
            if not m:
                raise Exception("cannot parse move: %s" % move)
    
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
            playerToBoardOpp[player].holdingAddPiece( \
                playerToBoard[player].sanGetPieceAt(m.group(1)) \
            )

        # CrazyBoard handles removal from holdings during piece drop
        playerToBoard[player].execMoveSan(move)

    def setBFEN(self, bfen):
        [l,r] = bfen.split(' | ')

        self.boardA.setFEN(l)
        self.boardB.setFEN(r)

    def getBFEN(self):
        return self.boardA.getFEN() + ' | ' + self.boardB.getFEN()

    def draw(self):
        self.boardA.draw()
        self.boardB.draw()

def doTest():
    # root window
    root = Tkinter.Tk()
    root.wm_title("BugBoard")

    cb = BugBoard(root)
    cb.grid()

    cb.setBFEN("r1b1k1nr/ppp1qpPp/2n5/1B1p1n1N/3P4/2P5/P1P1QPnP/R1BK2NR/PPBpp b kq - 142 164 | 2Nrkb1r/pPpbqppp/2p5/8/3N4/2P1B3/P1P1QPpP/R3K2R/Ppb w KQk - 142 163")
    cb.draw()

    # run
    root.mainloop() 

if __name__ == "__main__":
    doTest()

