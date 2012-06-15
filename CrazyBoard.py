#!/usr/bin/python

# a Crazy(House) board is a chessboard with a little reserve area to the side

import re
import Tkinter

import ChessBoard
import ReserveBoard

class CrazyBoard(Tkinter.Frame):
    def __init__(self, parent, pieceWidth=48, pieceHeight=48):
        Tkinter.Frame.__init__(self, parent)

        self.parent = parent

        # left side
        self.chessBoard = ChessBoard.ChessBoard(self, pieceWidth, pieceHeight)
        self.chessBoard.draw()
        # right side
        self.reserveBoard = ReserveBoard.ReserveBoard(self, pieceWidth, pieceHeight)
        self.reserveBoard.draw()

        self.margin = 4;
        self.width = self.margin + self.chessBoard.width + self.reserveBoard.width + self.margin
        self.height = self.margin + self.chessBoard.height + self.margin

        #self.chessBoard.pack(side=Tkinter.LEFT)
        #self.reserveBoard.pack(side=Tkinter.LEFT)

        self.chessBoard.grid(row=0, column=0)
        self.reserveBoard.grid(row=0, column=1)

        #print self.chessBoard.grid_info()
        #print self.reserveBoard.grid_info()
        w = Tkinter.Label(self, text="row0_column2", bg="red", fg="white")
        w.grid(row=0, column=2)
        w = Tkinter.Label(self, text="row1_column2", bg="red", fg="white")
        w.grid(row=1, column=2)
        w = Tkinter.Label(self, text="row2_column2", bg="red", fg="white")
        w.grid(row=2, column=2)
        #w = Tkinter.Label(self, text="Red", bg="red", fg="white")
        #w.grid(row=0, column=0)
        #w = Tkinter.Label(self, text="Red", bg="red", fg="white")
        #w.grid(row=0, column=0)

def doTest():
    # root window
    root = Tkinter.Tk()
    root.wm_title("Crazy Board Test\n")

    # reserve board on root
    cb = CrazyBoard(root)
    cb.grid()

    # run
    root.mainloop() 

if __name__ == "__main__":
    doTest()

