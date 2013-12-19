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

# this is just a little (8x2) column reserve area for use with crazyhouse boards
#
# 16 pieces should be enough to hold whatever is won from the other side

import re
import Tkinter
 
class HoldingBoard(Tkinter.Frame):
    def __init__(self, parent, pieceWidth=48, pieceHeight=48):
        Tkinter.Frame.__init__(self, parent)

        self.parent = parent

        self.flippedDisplay = 0
        self.pieceWidth = pieceWidth
        self.pieceHeight = pieceHeight
        self.width = 2*pieceWidth
        self.height = 8*pieceHeight

        self.canvas = Tkinter.Canvas(self, width=self.width, height=self.height)

        self.pieces = {}
        
        self.setFEN('')

        # bitmaps
        self.bitmaps = {}
        self.loadBitmaps() 

        self.canvas.grid(row=0, column=0)

    def loadBitmaps(self):
        imageFiles = [ \
            'bdd48.gif', 'dsq48.gif', 'kll48.gif', 'nld48.gif', 'pld48.gif', 'qld48.gif', \
            'bdl48.gif', 'kdd48.gif', 'lsq48.gif', 'nll48.gif', 'pll48.gif', 'qll48.gif', \
            'rld48.gif', 'bld48.gif', 'kdl48.gif', 'ndd48.gif', 'pdd48.gif', 'qdd48.gif', \
            'rdd48.gif', 'rll48.gif', 'bll48.gif', 'kld48.gif', 'ndl48.gif', 'pdl48.gif', \
            'qdl48.gif', 'rdl48.gif']

        for imgF in imageFiles:
            key = re.sub(r'^(.*)\.gif$', r'\1', imgF)

            imgPath = './images/' + imgF

            #print 'setting self.bitmaps[%s] = %s' % (key, imgPath)
            self.bitmaps[key] = Tkinter.PhotoImage(file=imgPath)


    def addPiece(self, p):
        self.pieces[p] += 1

    def removePiece(self, p):
        if self.pieces[p] == 0:
            raise "removing non-existent piece from reserve!"

        self.pieces[p] -= 1

    def fenPieceToBitmap(self, p, square):
        # square is either 'd'/0 (dark) or 'l'/1 (light)

        fenPieceToImg = { 'P':'pl', 'p':'pd',
                          'B':'bl', 'b':'bd',
                          'N':'nl', 'n':'nd',
                          'R':'rl', 'r':'rd',
                          'Q':'ql', 'q':'qd',
                          'K':'kl', 'k':'kd'
                          }

        square = 'l'

        if p == ' ':
            return self.bitmaps[square + 'sq48']
        else:
            if not p in fenPieceToImg:
                raise "invalid piece!"

            return self.bitmaps[fenPieceToImg[p] + square + '48']

    def flip(self):
        self.flippedDisplay = 1

    def draw(self):
        w = self.pieceWidth
        xCoord = w/2
        yCoord = w/2

        pieceToCoords = {}

        ptcSequence = 'pbnrqkPBNRQK'
        if self.flippedDisplay:
            ptcSequence = 'PBNRQKpbnrqk'

        pieceToCoords[ptcSequence[0]] = [xCoord, yCoord]
        pieceToCoords[ptcSequence[1]] = [xCoord + w, yCoord]
        pieceToCoords[ptcSequence[2]] = [xCoord, yCoord + w]
        pieceToCoords[ptcSequence[3]] = [xCoord + w, yCoord + w]
        pieceToCoords[ptcSequence[4]] = [xCoord, yCoord + 2*w]
        pieceToCoords[ptcSequence[5]] = [xCoord + w, yCoord + 2*w]

        yCoord = w/2 + 4*w
        pieceToCoords[ptcSequence[6]] = [xCoord, yCoord]
        pieceToCoords[ptcSequence[7]] = [xCoord + w, yCoord]
        pieceToCoords[ptcSequence[8]] = [xCoord, yCoord + w]
        pieceToCoords[ptcSequence[9]] = [xCoord + w, yCoord + w]
        pieceToCoords[ptcSequence[10]] = [xCoord, yCoord + 2*w]
        pieceToCoords[ptcSequence[11]] = [xCoord + w, yCoord + 2*w]

        self.canvas.delete(Tkinter.ALL)

        for (p,n) in self.pieces.iteritems():

            [x,y] = pieceToCoords[p]

            #print 'drawing a %s at (%d,%d)' % (p, x, y)

            # if piece no present, print empty square
            if not n:
                p = ' '

            self.canvas.create_image( \
                [x, y], \
                image = self.fenPieceToBitmap(p, 0)
            )
    
            if n:
                self.canvas.create_text(x-w/2, y-w/2, text="%d" % n, anchor=Tkinter.NW)

    # this parses the "holdings" string from BFEN notation...
    # pieces in uppercase belong to white; lowercase belong to white
    # eg BrpBBqppN (white holds 3 bishops and knight, black holds rook, queen, and 3 pawns)
    def setFEN(self, fen):
        # clear current piece holdings count
        for p in list("PNRBKQpnrbkq"):
            self.pieces[p] = 0

        # load it up
        for p in list(fen):
            self.pieces[p] += 1

    def getFEN(self):
        answer = ''

        for p in list("PNRBKQpnrbkq"):
            answer += p*self.pieces[p]

        return answer

def doTest():
    # root window
    root = Tkinter.Tk()
    root.wm_title("Reserve Board Test\n")

    # reserve board on root
    rb = HoldingBoard(root)
    rb.draw()

    # run
    root.mainloop() 

if __name__ == "__main__":
    doTest()
