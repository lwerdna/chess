#!/usr/bin/python

# a Bughouse Board is two Crazyhouse Boards, one flipped

import re
import Tkinter

import ChessBoard
import ReserveBoard
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
        # we strip off player indicator to decide which board to send the move to

        pieceChangeColorMap = {'p':'P', 'P':'p', \
                               'r':'R', 'R':'r', \
                               'b':'B', 'B':'b', \
                               'n':'N', 'N':'n', \
                               'q':'Q', 'Q':'q'}

        # we mainly thunk through to CrazyBoard
        self.chessBoard.execMoveSan(move)

        # but if transfering is enabled (normal CrazyHouse) we intercept:
        if self.transferPiece:
            # captures (to add to holdings)
            m = re.find('x([prnbqkPRNBQK])', move)
            if m:
                self.reserveBoard.addPiece(pieceChangeColorMap(m.group(1)))
        
            # drops (to remove from holdings)
            m = re.find('([prnbqkPRNBQK])@', move)
            if m:
                self.reserveBoard.removePiece(m.group(1))


    def setBFEN(self, bfen):
        [l,r] = bfen.split(' | ')

        self.boardA.setFEN(l)
        self.boardB.setFEN(r)

    def getBFEN(self, bfen):
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

