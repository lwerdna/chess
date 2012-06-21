#!/usr/bin/python

# a Crazy(House) board is a chessboard with a little holding area to the side

import re
import Tkinter

import Common
import CrazyLogic
import ChessLogic
import ChessBoard
import HoldingBoard

class CrazyBoard(Tkinter.Frame):
    def __init__(self, parent, pieceWidth=48, pieceHeight=48):
        Tkinter.Frame.__init__(self, parent)

        self.parent = parent

        # on piece capture, send to other side
        self.transferPieces = 1

        # left side
        self.chessBoard = ChessBoard.ChessBoard(self, pieceWidth, pieceHeight)
        # right side
        self.holdingBoard = HoldingBoard.HoldingBoard(self, pieceWidth, pieceHeight)

        self.width = self.chessBoard.width + self.holdingBoard.width
        self.height = self.chessBoard.height

        self.chessBoard.grid(row=0, column=0, padx=2)
        self.holdingBoard.grid(row=0, column=1, pady=2)

        self.boardMap = {}

    def setBoardMap(self, bm):
        self.boardMap = bm

        # filter out stuff that normal chess doesn't understand
        # filter '~' promotion marker
        temp = {}
        for key,val in bm.iteritems():
            temp[key] = val.replace('~', '')
        self.chessBoard.setBoardMap(temp)

        self.holdingBoard.setFEN(bm['holdings'])

    def flip(self):
        self.chessBoard.flip()
        self.holdingBoard.flip()

    def draw(self):
        self.chessBoard.draw()
        self.holdingBoard.draw()

class CrazyBoardTest(Tkinter.Frame):
    def __init__(self, parent, pieceWidth=48, pieceHeight=48):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
   
        self.boardMap = CrazyLogic.fenToBoardMap(Common.initCrazyFEN)

        self.cb = CrazyBoard(self)
        self.cb.setBoardMap(self.boardMap)
        self.cb.draw()
        self.cb.pack()

        self.b = Tkinter.Button(self, text="flip", command=self.flipIt)
        self.b.pack()

        self.moveEntry = Tkinter.Entry(self)
        self.moveEntry.pack()
        self.execMove = Tkinter.Button(self, text="execute move", command=self.executeMove)
        self.execMove.pack()

    def flipIt(self):
        self.cb.flip()
        self.cb.draw()

    def executeMove(self):
        whatMove = self.moveEntry.get()
        print "Executing: " + whatMove
        self.boardMap = CrazyLogic.nextStateInternal(self.boardMap, whatMove)
        self.cb.setBoardMap(self.boardMap)
        self.cb.draw()

def doTest():
    # root window
    root = Tkinter.Tk()
    root.wm_title("CrazyBoard Test\n")

    # holding board on root
    cbt = CrazyBoardTest(root)
    cbt.pack()

    # run
    root.mainloop() 

if __name__ == "__main__":
    doTest()

