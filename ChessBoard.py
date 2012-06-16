#!/usr/bin/python

import re
import Tkinter
 
class ChessBoard(Tkinter.Frame):
    def __init__(self, parent, pieceWidth=48, pieceHeight=48):
        Tkinter.Frame.__init__(self, parent)

        self.parent = parent

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

        # set up initial positions
        [self.FENactive, self.FENcastling, self.FENenpassant, self.FENhalfmove, self.FENfullmove] = \
            [None, None, None, None, None]
        self.setFEN("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

        # the canvas can directly bind
        #self.canvas.bind("<Button-1>", canvasClick)
        #self.canvas.tag_bind(circ1, "<B1-Motion>", redCircleDrag)
        #self.canvas.tag_bind(circ1, "<Button-1>", redCircle)
        #self.canvas.tag_bind(circ2, "<Button-1>", blueCircle)

        # 
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

    def setFEN(self, fen):
        [places, self.FENactive, self.FENcastling, self.FENenpassant, self.FENhalfmove, self.FENfullmove] = \
            re.split(' ', fen)

        # starts rank 8 (top, 8), goes down to rank 1 (bottom, 1)
        # starts file 1 (left, a), goes over to file 8 (right, h)
        rankPlaces = re.split('/', places)
        if len(rankPlaces) != 8:
            raise "FEN did not contain 8 ranks!"

        # expand the ranks to 64 string
        full64 = []
        for rank in rankPlaces:
            for sym in rank:
                if re.match(r'^\d$', sym):
                    full64 += ' '*int(sym)
                else:
                    full64 += sym
        
        if len(full64) != 64:
            raise "FEN did not contain 64 data!"

        # ok load that into the state
        self.state = list(full64)
     
    def getFEN(self):
        answer = ''

        for i,p in enumerate(full64):
            if p == ' ':
                answer += 1
            else:
                answer += p

        return answer + ' ' + ' '.join([self.FENplaces, self.FENactive, self.FENcastling, self.FENenpassant, self.FENhalfmove, self.FENfullmove])

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
        print "ChessBoard is flipped!"
        self.flippedDisplay = 1

    def draw(self):
        pieceGetSequence = range(64)
        if self.flippedDisplay:
            pieceGetSequence.reverse()

        for i in range(64):
            xCoord = self.pieceWidth/2 + self.pieceWidth * (i%8)
            yCoord = self.pieceHeight/2 + self.pieceHeight * (i/8)

            #print 'drawing a %s at (%d,%d)' % (self.state[i], xCoord, yCoord)

            self.stateImg[i] = self.canvas.create_image( \
                [xCoord, yCoord], \
                image = self.fenPieceToBitmap(self.state[pieceGetSequence[i]], (i + i/8 + 1)%2)
            )

def doTest():
    # root window
    root = Tkinter.Tk()
    root.wm_title("Chess Board Test\n")

    # reserve board on root
    cb = ChessBoard(root)
    cb.draw()
    cb.grid(row=0, column=0)
    cb.flip()
    cb.draw()

    # run
    root.mainloop() 

if __name__ == "__main__":
    doTest()
