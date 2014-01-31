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
import time
import Tkinter 

import Common
from ChessState import ChessState
from ChessMove import ChessMove

DARK_SQUARE_COLOR = '#58ae8b'
LIGHT_SQUARE_COLOR = '#feffed'

class ChessBoard(Tkinter.Frame):
    def __init__(self, parent, squareWidth=64, squareHeight=64):
        Tkinter.Frame.__init__(self, parent)

        self.parent = parent

        self.chessState = None

        self.squareWidth = squareWidth
        self.squareHeight = squareHeight
        self.width = 8*squareWidth
        self.height = 8*squareHeight
        self.canvas = Tkinter.Canvas(self, width=self.width, height=self.height)

        # in addition to easy lookup, ref's to PhotoImage must be kept, else the
        # surrounding image (from canvas.create_image()) will be left empty
        self.pieceToPhoto = {}
        for piece in 'pnbrqkPNBRQK':
            self.pieceToPhoto[piece] = Tkinter.PhotoImage(file='./images/%s.gif' % piece)

        for ridx, rname in enumerate(list('87654321')):
            for fidx, fname in enumerate(list('abcdefgh')):
                tag = fname + rname
                color = [DARK_SQUARE_COLOR, LIGHT_SQUARE_COLOR][(ridx-fidx)%2]
                shade = ['dark', 'light'][(ridx-fidx)%2]

                tags = [fname+rname, shade, 'square']

                self.canvas.create_rectangle(
                    fidx*squareWidth, ridx*squareHeight,
                    fidx*squareWidth+squareWidth, ridx*squareHeight+squareHeight,
                    outline=color, fill=color, tag=tags)
        
        self.canvas.grid(row=0, column=0)

    def clear(self):
        self.canvas.delete('piece')
        self.refreshCanvasFromState()

    def setState(self, state):
        self.chessState = state.copy()
        self.refreshCanvasFromState()

    def setFEN(self, fen):
        self.chessState = ChessState(fen)
        self.refreshCanvasFromState()

# canvasx, canvasy

    def flip(self):
        for item in self.canvas.find_all():
            coords = self.canvas.coords(item)
            if self.canvas.type(item) == 'rectangle':
                # then coords is a bounding box
                coords[1] = abs(7 - (coords[1] / self.squareHeight)) * self.squareHeight
                coords[3] = coords[1] + self.squareHeight
            
            self.canvas.coords(item, *coords)

    def placePiece(self, square, piece):
        if not piece in 'pnbrqkPNBRQK ': 
            raise "invalid piece: '%s'" % piece
        if piece == ' ':
            return
        # canvas rectangle objects are tagged with 'a1', etc.
        item = self.canvas.find_withtag(square)
        # get bounding box of rectangle (we'll draw piece here)
        coords = self.canvas.coords(item)
        # do it
        photo = self.pieceToPhoto[piece]
        image = self.canvas.create_image(coords[0], coords[1], image=photo, 
            state=Tkinter.NORMAL, anchor=Tkinter.NW, tag='piece')

    def refreshCanvasFromState(self):
        if not self.chessState:
            raise Exception("no chessState set!")
       
        self.canvas.delete('piece')

        for rname in '87654321':
            for fname in 'abcdefgh':
                sname = fname + rname

                if self.chessState[sname] != ' ':
                    #time.sleep(.1)
                    self.canvas.update_idletasks()
                    self.placePiece(sname, self.chessState[sname])

# test frame that holds a ChessBoard widget
#
class ChessBoardTest(Tkinter.Frame):
    def __init__(self, parent, squareWidth=64, squareHeight=64):
        self.player = 'w'
        self.moveNum = 1

        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
  
        self.chessState = ChessState(Common.initChessFEN)

        self.cb = ChessBoard(self)
        self.cb.setState(self.chessState)
        self.cb.refreshCanvasFromState()
        self.cb.pack()

        self.b = Tkinter.Button(self, text="flip", command=self.flipIt)
        self.b.pack()

        self.b2 = Tkinter.Button(self, text="clear", command=self.clearIt)
        self.b2.pack()

        #self.b = Tkinter.Button(self, text="html", command=self.html)
        #self.b.pack()

        self.moveEntry = Tkinter.Entry(self)
        self.moveEntry.pack()
        self.execMove = Tkinter.Button(self, text="execute move", command=self.executeMove)
        self.execMove.pack()

    def clearIt(self):
        self.cb.clear()

    def flipIt(self):
        self.cb.flip()

    def executeMove(self):
        whatMove = self.moveEntry.get()
        print "executing: " + whatMove
        move = ChessMove(self.player, self.moveNum, whatMove)
        self.chessState = self.chessState.transition(move)
        self.cb.setState(self.chessState)

        print "new state: " + str(self.chessState)

        self.player = {'w':'b', 'b':'w'}[self.player]
        self.moveNum += 1

def doTest():
    # root window
    root = Tkinter.Tk()
    root.wm_title("Chess Board Test\n")

    # reserve board on root
    cbt = ChessBoardTest(root)
    cbt.pack()

    # run
    root.mainloop() 

if __name__ == "__main__":
    doTest()

