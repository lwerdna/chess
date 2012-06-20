#!/usr/bin/python

import re
import Tkinter

import Common
import ChessLogic

class ChessBoard(Tkinter.Frame):
    def __init__(self, parent, pieceWidth=48, pieceHeight=48):
        Tkinter.Frame.__init__(self, parent)

        self.parent = parent

        self.boardMap = {} 

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
        self.bitmaps = {}
        self.loadBitmaps() 

        # 
        self.canvas.grid(row=0, column=0)

    def setBoardMap(self, boardMap):
        self.boardMap = boardMap.copy()
     

    #--------------------------------------------------------------------------
    # drawing stuff
    #--------------------------------------------------------------------------
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
            key = re.sub(r'^(.*)\.gif$', r'\1', imgF)

            imgPath = './images/' + imgF

            #print 'setting self.bitmaps[%s] = %s' % (key, imgPath)
            self.bitmaps[key] = Tkinter.PhotoImage(file=imgPath)

    def draw(self):
        if not self.boardMap:
            raise Exception("ChessBoard cannot draw without boardMap being set!")

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
                    self.boardMap[ \
                        Common.squaresSan[pieceGetSequence[i]] \
                    ], \
                    (i + i/8 + 1)%2 \
                )
            )

class ChessBoardTest(Tkinter.Frame):
    def __init__(self, parent, pieceWidth=48, pieceHeight=48):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
  
        self.boardMap = ChessLogic.fenToBoardMap(Common.initFEN)

        self.cb = ChessBoard(self)
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
        self.boardMap = ChessLogic.nextStateInternal(self.boardMap, whatMove)
        self.cb.setBoardMap(self.boardMap)
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
