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

import re
import sys
import Tkinter

import Common
import ChessBoard
import PgnParser

class PgnViewer(Tkinter.Frame):
    def __init__(self, parent, pieceWidth=64, pieceHeight=64):
        Tkinter.Frame.__init__(self, parent)

        self.parent = parent
       
        self.boardMap = {}

        self.PgnParser = None
        self.stateIndex = 0

        # widget
        self.chessBoard = ChessBoard.ChessBoard(self, pieceWidth, pieceHeight)
        self.chessBoard.setFEN(Common.initChessFEN)
        self.chessBoard.refreshCanvasFromState()

        # status thingies
        self.playerInfoW = Tkinter.Label(self, text="", bg="white", fg="black")
        self.playerTimeW = Tkinter.Label(self, text="", bg="green", fg="black")
        self.playerInfoB = Tkinter.Label(self, text="", bg="black", fg="white")
        self.playerTimeB = Tkinter.Label(self, text="", bg="green", fg="black")
    
        # buttons go into frame
        self.btnFrame = Tkinter.Frame(self)
        self.btnFlip = Tkinter.Button(self.btnFrame, text="FLIP", command=self.btnFlipCb)
        self.btnStart = Tkinter.Button(self.btnFrame, text="|<", command=self.btnStartCb)
        self.btnBackward = Tkinter.Button(self.btnFrame, text="<", command=self.btnBackwardCb)
        self.btnForward = Tkinter.Button(self.btnFrame, text=">", command=self.btnForwardCb)
        self.btnEnd = Tkinter.Button(self.btnFrame, text=">|", command=self.btnEndCb)

        self.playerInfoW.grid(row=0, column=1, sticky=Tkinter.E + Tkinter.W)
        self.playerTimeW.grid(row=0, column=0)
        self.playerInfoB.grid(row=0, column=2, sticky=Tkinter.E + Tkinter.W)
        self.playerTimeB.grid(row=0, column=3)

        self.chessBoard.grid(row=1, column=0, columnspan=4)
        self.playerInfoW.grid(row=2, column=1, sticky=Tkinter.E + Tkinter.W)
        self.playerTimeW.grid(row=2, column=0)
        self.playerInfoB.grid(row=2, column=2, sticky=Tkinter.E + Tkinter.W)
        self.playerTimeB.grid(row=2, column=3)

        self.btnFlip.pack(side=Tkinter.LEFT)
        self.btnStart.pack(side=Tkinter.LEFT)
        self.btnBackward.pack(side=Tkinter.LEFT)
        self.btnForward.pack(side=Tkinter.LEFT)
        self.btnEnd.pack(side=Tkinter.LEFT)
        self.btnFrame.grid(row=3, columnspan=4)

    # load a match from a pgn file
    # set our chessboard to the first state of the match
    def loadPgn(self, path):
        match = self.match = PgnParser.PgnChessMatchIteratorFile(path).next()

        initFen = Common.initChessFEN
        if 'SetUp' in match.tags:
            if match.tags['SetUp'] == '1':
                if 'FEN' in match.tags:
                    initFen = match.comments['FEN']
      
        self.playerInfoW.config(text=match.tags['White'])
        self.playerInfoB.config(text=match.tags['Black'])
        self.chessBoard.setState(match.states[0])
        self.stateIndex = 0
        self.updateDisplay()

    def updateDisplay(self):
        self.chessBoard.clear()
        self.chessBoard.setState(self.match.states[self.stateIndex])

    def btnBackwardCb(self):
        if self.stateIndex <= 0:
            print "at beginning"
        else:
            self.stateIndex -= 1

        self.updateDisplay()

    def btnForwardCb(self):
        if self.stateIndex >= len(self.match.states)-1:
            print "on last move"
        else:
            self.stateIndex += 1

        self.updateDisplay()

    def btnStartCb(self):
        self.stateIndex = 0
        self.updateDisplay()

    def btnEndCb(self):
        self.stateIndex = len(self.match.states)-1
        self.updateDisplay()

    def btnFlipCb(self):
        self.chessBoard.flip()
        self.updateDisplay()

if __name__ == "__main__":
    # root window
    root = Tkinter.Tk()
    root.wm_title("PgnViewer")
    root.configure(background = 'black')

    cb = PgnViewer(root)
    cb.grid()

    cb.loadPgn(sys.argv[1])

    # run
    root.mainloop() 
