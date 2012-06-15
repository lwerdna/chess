#!/usr/bin/python

# this is just a little (8x2) column reserve area for use with crazyhouse boards
#
# 16 pieces should be enough to hold whatever is won from the other side

import re
import Tkinter
 
class ReserveBoard(Tkinter.Frame):
    def __init__(self, parent, pieceWidth=48, pieceHeight=48):
        Tkinter.Frame.__init__(self, parent)

        self.parent = parent

        self.margin = 4

        self.pieceWidth = pieceWidth
        self.pieceHeight = pieceHeight
        self.width = 2*pieceWidth + 2*self.margin
        self.height = 8*pieceHeight + 2*self.margin

        self.canvas = Tkinter.Canvas(parent, width=self.width, height=self.height)

        self.pieces = {'P':1, 'N':1, 'R':1, 'B':1, 'Q':1, 'K':0, \
                       'p':1, 'n':1, 'r':1, 'b':1, 'q':1, 'k':0}

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

            print 'setting self.bitmaps[%s] = %s' % (key, imgPath)
            self.bitmaps[key] = Tkinter.PhotoImage(file=imgPath)


    def addPiece(p):
        self.pieces[p] += 1
        draw()

    def removePiece(p):
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

        square = ['d', 'l'][square]

        if p == ' ':
            return self.bitmaps[square + 'sq48']
        else:
            if not p in fenPieceToImg:
                raise "invalid piece!"

            return self.bitmaps[fenPieceToImg[p] + square + '48']

    def draw(self):
        w = self.pieceWidth
        xCoord = self.margin + w/2
        yCoord = self.margin + w/2

        pieceToCoords = {}
        pieceToCoords['P'] = [xCoord, yCoord]
        pieceToCoords['B'] = [xCoord + w, yCoord]
        pieceToCoords['N'] = [xCoord, yCoord + w]
        pieceToCoords['R'] = [xCoord + w, yCoord + w]
        pieceToCoords['Q'] = [xCoord, yCoord + 2*w]
        pieceToCoords['K'] = [xCoord + w, yCoord + 2*w]

        yCoord = self.margin + w/2 + 4*w
        pieceToCoords['p'] = [xCoord, yCoord]
        pieceToCoords['b'] = [xCoord + w, yCoord]
        pieceToCoords['n'] = [xCoord, yCoord + w]
        pieceToCoords['r'] = [xCoord + w, yCoord + w]
        pieceToCoords['q'] = [xCoord, yCoord + 2*w]
        pieceToCoords['k'] = [xCoord + w, yCoord + 2*w]
   
        self.canvas.delete(Tkinter.ALL)

        for (p,n) in self.pieces.iteritems():
            if not n:
                continue

            [x,y] = pieceToCoords[p]

            print 'drawing a %s at (%d,%d)' % (p, x, y)

            self.canvas.create_image( \
                [x, y], \
                image = self.fenPieceToBitmap(p, 0)
            )

            self.canvas.create_text(x-w/2, y-w/2, text="%d" % n, anchor=Tkinter.NW)

def doTest():
    # root window
    root = Tkinter.Tk()
    root.wm_title("Reserve Board Test\n")

    # reserve board on root
    rb = ReserveBoard(root)
    rb.draw()

    # run
    root.mainloop() 

if __name__ == "__main__":
    doTest()
