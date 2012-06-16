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
        [self.whoseTurn, self.FENcastling, self.FENenpassant, self.FENhalfmove, self.FENfullmove] = \
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

    #--------------------------------------------------------------------------
    # FEN notation import/export
    #--------------------------------------------------------------------------
    def setFEN(self, fen):
        [places, self.whoseTurn, self.FENcastling, self.FENenpassant, self.FENhalfmove, self.FENfullmove] = \
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

        return answer + ' ' + ' '.join([self.whoseTurn, self.FENcastling, self.FENenpassant, self.FENhalfmove, self.FENfullmove])

    #--------------------------------------------------------------------------
    # board access stuff
    #--------------------------------------------------------------------------
    def sanToStateIndex(self, square):
        return 8 * (8-int(square[1])) + \
            {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7}[square[0]] \

    # given 'a4', return the piece at a4
    def sanGetPieceAt(self, square):
        return self.state[self.sanToStateIndex(square)]

    def sanSetPieceAt(self, square, p):
        self.state[self.sanToStateIndex(square)] = p

    # given 'b4' and [-1,-1] (move left one, up one), return a5
    def sanSquareShift(self, square, movement):
        x = {'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6, 'g':7, 'h':8}[square[0]]
        y = int(square[1])

        x += movement[0]
        y += movement[1]

        if x<1 or x>8 or y<1 or y>8:
            return None

        return {1:'a', 2:'b', 3:'c', 4:'d', 5:'e', 6:'f', 7:'g', 8:'h'}[x] + \
            str(y)
   
    def sanSquareShifts(self, square, movements):
        return map(lambda x: self.sanSquareShift(square, x), movements)

    def sanIsSameRank(self, a, b):
        return a[1] == b[1]

    def sanIsSameFile(self, a, b):
        return a[0] == b[0]

    #--------------------------------------------------------------------------
    # PGN movetext parsing
    #--------------------------------------------------------------------------
    def getMoveSourceSquares(self, destSquare, piece):
        answers = []

        # these "searchLines" across the chessboard define a line of search that
        # could be blocked by interposing pieces
        searchLinesPawnB = [[[0,1]],[[0,2]]]
        searchLinesPawnW = [[[0,-1],[0,-2]]]

        searchLinesKing = [ \
            [[1,0]], \
            [[1,-1]], \
            [[0,-1]], \
            [[-1,1]], \
            [[-1,0]], \
            [[-1,1]], \
            [[0,1]], \
            [[1,1]] \
        ]

        searchLinesKnight = [ \
            [[-2,1]], \
            [[-1,2]], \
            [[1,2]], \
            [[2,1]], \
            [[1,-2]], \
            [[2,-1]], \
            [[-1,-2]], \
            [[2,-1]] \
        ]

        searchLinesRook = [ \
            [[-1,0],[-2,0],[-3,0],[-4,0],[-5,0],[-6,0],[-7,0]], \
            [[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0]], \
            [[0,1],[0,2],[0,3],[0,4],[0,5],[0,6],[0,7]], \
            [[0,-1],[0,-2],[0,-3],[0,-4],[0,-5],[0,-6],[0,-7]] \
        ]

        searchLinesBishop = [ \
            [[-1,-1],[-2,-2],[-3,-3],[-4,-4],[-5,-5],[-6,-6],[-7,-7]], \
            [[1,-1],[2,-2],[3,-3],[4,-4],[5,-5],[6,-6],[7,-7]], \
            [[-1,1],[-2,2],[-3,3],[-4,4],[-5,5],[-6,6],[-7,7]], \
            [[1,1],[2,2],[3,3],[4,4],[5,5],[6,6],[7,7]] \
        ]

        searchLinesQueen = searchLinesRook + searchLinesBishop

        pieceToSearchLines = { \
                        'p': searchLinesPawnB, 'P':searchLinesPawnW, \
                        'r': searchLinesRook, 'R':searchLinesRook, \
                        'n': searchLinesKnight, 'N':searchLinesKnight, \
                        'q': searchLinesQueen, 'Q':searchLinesQueen, \
                        'b': searchLinesBishop, 'B':searchLinesBishop, \
                        'k': searchLinesKing, 'K':searchLinesKing }

        for searchLine in pieceToSearchLines[piece]:
            for sq in filter(lambda x: x, self.sanSquareShifts(destSquare, searchLine)):
                print "a sq from sanSquareShifts: " + sq

                p = self.sanGetPieceAt(sq)
                # empty square? keep along the searchLine
                if p == ' ':
                    continue
                # found it?
                if p == piece:
                    answers.append(sq)
                # found or not, square is occupied and blocks attacking bishop
                break

        return answers

    def getAttackSourceSquares(self, destSquare, piece):
        if piece == 'p':
            return self.sanSquareShifts(destSquare, [[[-1,1], [1,1]]])
        elif piece == 'P':
            return self.sanSquareShifts(destSquare, [[[1,-1], [-1,-1]]])
        else:
            return self.getMoveSourceSquares(destSquare, piece)

    def execMoveSan(self, move):
        # extended with some bughouse constructs

        origMove = move

        regex = r'(?P<srcPiece>[PNBRQKpnbrqk])?' + \
                r'(?P<srcHint>[a-h1-8]{1,2})?' + \
                r'(?P<action>x)?' + \
                r'(?P<dstSquare>[a-h][1-8])' + \
                r'(?P<promote>=[PNBRQKpnbrqk])?' + \
                r'(?P<check>\+)?'

        m = re.match(regex, move)
        if not m:
            raise Exception("cannot parse move: %s" % move)

        srcPiece = m.group('srcPiece') or {'w':'P', 'b':'p'}[self.whoseTurn]
        srcHint = m.group('srcHint')
        action = m.group('action')
        dstSquare = m.group('dstSquare')
        promote = m.group('promote')
        check = m.group('check')

        # resolve the srcSquare
        srcSquare = ''
        if srcHint and re.match(r'^[a-h][1-8]$', srcHint):
            # given a full hint, source square is resolved
            srcSquare = srcHint
        else:
            # where could piece have come from?
            srcSquares = []
            if action == 'x':
                srcSquares = self.getAttackSourceSquares(dstSquare, srcPiece)
            else:
                srcSquares = self.getMoveSourceSquares(dstSquare, srcPiece)

            print "srcSquares: ", srcSquares

            if srcHint and re.match(r'^[1-8]$', srcHint):
                # given a rank hint, consider only source squres in this rank
                srcSquares = filter(lambda x: x[1] == srcHint, srcSquares)
            elif srcHint and re.match(r'^[a-h]$', srcHint):
                # given a file hint, consider only source squares in that file
                srcSquares = filter(lambda x: x[0] == srcHint, srcSquares)

            # hopefully we're left with one square by now
            if len(srcSquares) < 1:
                raise Exception("could not find source square for move %s" % move)
            elif len(srcSquares) > 1:
                raise Exception("ambiguous source square for move %s" % move)
               
            srcSquare = srcSquares[0]
   
        # modify the state
        self.sanSetPieceAt(srcSquare, ' ')
        self.sanSetPieceAt(dstSquare, srcPiece)

        # swap whose turn it is
        self.whoseTurn = {'w':'b', 'b':'w'}[self.whoseTurn]

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
        print "ChessBoard is flipped!"
        self.flippedDisplay = (self.flippedDisplay + 1) & 1

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

class ChessBoardTest(Tkinter.Frame):
    def __init__(self, parent, pieceWidth=48, pieceHeight=48):
        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
   
        self.cb = ChessBoard(self)
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
        self.cb.execMoveSan(whatMove)
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
