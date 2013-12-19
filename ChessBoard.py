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
from ChessState import ChessState

class ChessBoard(Tkinter.Frame):
    def __init__(self, parent, pieceWidth=48, pieceHeight=48):
        Tkinter.Frame.__init__(self, parent)

        self.parent = parent

        self.chessState = {} 

        self.flippedDisplay = 0

        self.pieceWidth = pieceWidth
        self.pieceHeight = pieceHeight
        self.width = 8*pieceWidth
        self.height = 8*pieceHeight
        self.canvas = Tkinter.Canvas(self, width=self.width, height=self.height)

        # [0,1,2,...] = [a8,a7,a6,...]
        self.state = [' ']*64
        self.stateImg = [None]*64

        # bitmaps
        # maps 'bdd' to 'bdd48.gif', etc.
        self.bitmapFiles = {}
        # maps 'bdd' to PhotoImage instance, etc.
        self.bitmaps = {}
        self.loadBitmaps() 

        # 
        self.canvas.grid(row=0, column=0)

    def setState(self, state):
        self.chessState = state.copy()

    def setFEN(self, fen):
        self.chessState = ChessState(fen)

    #--------------------------------------------------------------------------
    # drawing stuff
    #--------------------------------------------------------------------------

    # maps {p,b,n,r,q,k,P,B,N,R,Q,K} X {0,1} to eg: "bdd48"
    #
    def fenPieceToBitmapFileRootName(self, p, square):
        # square is either 'd'/0 (dark) or 'l'/1 (light)

        mapping =       { 'P':'pl', 'p':'pd',
                          'B':'bl', 'b':'bd',
                          'N':'nl', 'n':'nd',
                          'R':'rl', 'r':'rd',
                          'Q':'ql', 'q':'qd',
                          'K':'kl', 'k':'kd'
                          }

        colorChar = ['d', 'l'][square]

        if p == ' ':
            return colorChar + 'sq48'
        else:
            if not p in mapping:
                raise "invalid piece!"

            return mapping[p] + colorChar + '48'

    def fenPieceToBitmap(self, p, square):
        rootName = self.fenPieceToBitmapFileRootName(p, square)
        return self.bitmaps[rootName]

    def fenPieceToBitmap(self, p, square):
        rootName = self.fenPieceToBitmapFileRootName(p, square)
        return self.bitmaps[rootName]

    def fenPieceToBitmapFile(self, p, square):
        rootName = self.fenPieceToBitmapFileRootName(p, square)
        return './images/' + rootName + '.gif'

    def flip(self):
        self.flippedDisplay = (self.flippedDisplay + 1) & 1

    def loadBitmaps(self):
        imageFiles = [ \
            'bdd48.gif', 'dsq48.gif', 'kll48.gif', 'nld48.gif', 'pld48.gif', 'qld48.gif', \
            'bdl48.gif', 'kdd48.gif', 'lsq48.gif', 'nll48.gif', 'pll48.gif', 'qll48.gif', \
            'rld48.gif', 'bld48.gif', 'kdl48.gif', 'ndd48.gif', 'pdd48.gif', 'qdd48.gif', \
            'rdd48.gif', 'rll48.gif', 'bll48.gif', 'kld48.gif', 'ndl48.gif', 'pdl48.gif', \
            'qdl48.gif', 'rdl48.gif']

        for imgF in imageFiles:
            # strip off the ".gif" - keys are just "bdd", "dsq", etc.
            key = re.sub(r'^(.*)\.gif$', r'\1', imgF)

            imgPath = './images/' + imgF

            #print 'setting self.bitmaps[%s] = %s' % (key, imgPath)
            self.bitmapFiles[key] = imgPath
            self.bitmaps[key] = Tkinter.PhotoImage(file=imgPath)

    def draw(self):
        if not self.chessState:
            raise Exception("ChessBoard cannot draw without chessState being set!")

        pieceGetSequence = range(64)
        if self.flippedDisplay:
            pieceGetSequence.reverse()

        for i in range(64):
            xCoord = self.pieceWidth/2 + self.pieceWidth * (i%8)
            yCoord = self.pieceHeight/2 + self.pieceHeight * (i/8)

            #print 'drawing a %s at (%d,%d)' % (self.state[i], xCoord, yCoord)

            self.stateImg[i] = self.canvas.create_image( \
                [xCoord, yCoord], \
                image = self.fenPieceToBitmap( \
                    self.chessState.squares[ \
                        Common.squaresSan[pieceGetSequence[i]] \
                    ], \
                    (i + i/8 + 1)%2 \
                )
            )

    def draw_html(self):
        if not self.chessState:
            raise Exception("ChessBoard cannot draw without chessState being set!")

        html = '<table border=0 cellpadding=0 cellspacing=0>\n'

        pieceGetSequence = range(64)
        if self.flippedDisplay:
            pieceGetSequence.reverse()

        html += '<tr>\n'

        for i in range(64):
            # end current row, start new row
            if not (i%8):
                html += '\n</tr>\n'
                html += '<tr>\n'

            # table cell has image in it
            # get either 0,1,2,... or 63,62,61,...
            tmp = pieceGetSequence[i]
            # map 0->'a8', 63->'h1', etc.
            tmp = Common.squaresSan[tmp]
            # map 'a8' to 'r' or 'R' for example (getting piece)
            tmp = self.chessState.squares[tmp]
            # finally, map that piece to a filename
            tmp = self.fenPieceToBitmapFile(tmp, (i+i/8+1)%2)

            html += ' <td><img src="%s" /></td>\n' %  tmp

        html += '\n</tr>\n'
        html += '</table>\n'

        return html

# test frame that holds a ChessBoard widget
#
class ChessBoardTest(Tkinter.Frame):
    def __init__(self, parent, pieceWidth=48, pieceHeight=48):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
  
        self.chessState = ChessState(Common.initChessFEN)

        self.cb = ChessBoard(self)
        self.cb.setState(self.chessState)
        self.cb.draw()
        self.cb.pack()

        self.b = Tkinter.Button(self, text="flip", command=self.flipIt)
        self.b.pack()

        self.b = Tkinter.Button(self, text="html", command=self.html)
        self.b.pack()

        self.moveEntry = Tkinter.Entry(self)
        self.moveEntry.pack()
        self.execMove = Tkinter.Button(self, text="execute move", command=self.executeMove)
        self.execMove.pack()

    def flipIt(self):
        self.cb.flip()
        self.cb.draw()

    def html(self):
        print self.cb.draw_html()

    def executeMove(self):
        whatMove = self.moveEntry.get()
        print "Executing: " + whatMove
        self.chessState = self.chessState.transition(whatMove)
        self.cb.setState(self.chessState)
        self.cb.draw()

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

