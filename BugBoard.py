#!/usr/bin/python

# a Bughouse Board is two Crazyhouse Boards, one flipped

import re
import Tkinter

import ChessLogic
import CrazyLogic
import BugLogic
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
        self.boardB.flip()

        self.width = 2*self.boardA.width
        self.height = 2*self.boardA.height

        self.boardA.grid(row=0, column=0)
        self.boardB.grid(row=0, column=1)

    def setBoardMap(self, boardMap):
        self.boardMap = boardMap.copy()
        self.boardA.setBoardMap(self.boardMap['boardA'])
        self.boardB.setBoardMap(self.boardMap['boardB'])

    def setBugFEN(self, bfen):
        self.boardMap = BugLogic.fenToBoardMap(bfen)

    def draw(self):
        self.boardA.draw()
        self.boardB.draw()

def doTest():
    # root window
    root = Tkinter.Tk()
    root.wm_title("BugBoard")

    cb = BugBoard(root)

    fen = "r1b1k1nr/ppp1qpPp/2n5/1B1p1n1N/3P4/2P5/P1P1QPnP/R1BK2NR/PPBpp b kq - 142 164" + \
            " | " + \
            "2Nrkb1r/pPpbqppp/2p5/8/3N4/2P1B3/P1P1QPpP/R3K2R/Ppb w KQk - 142 163"

    cb.setBoardMap(BugLogic.fenToBoardMap(fen))
    cb.draw()
    
    cb.grid()

    # run
    root.mainloop() 

if __name__ == "__main__":
    doTest()

