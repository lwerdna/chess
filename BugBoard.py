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
        self.leftBoard = CrazyBoard.CrazyBoard(self, pieceWidth, pieceHeight)
        self.rightBoard = CrazyBoard.CrazyBoard(self, pieceWidth, pieceHeight)
        self.rightBoard.flip()
        self.rightBoard.draw()

        self.width = 2*self.leftBoard.width
        self.height = 2*self.leftBoard.height

        self.leftBoard.grid(row=0, column=0)
        self.rightBoard.grid(row=0, column=1)

    def setBFEN(self, bfen):
        [l,r] = bfen.split(' | ')

        self.leftBoard.setFEN(l)
        self.rightBoard.setFEN(r)

    def getBFEN(self, bfen):
        return self.leftBoard.getFEN() + ' | ' + self.rightBoard.getFEN()

    def draw(self):
        self.leftBoard.draw()
        self.rightBoard.draw()

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

