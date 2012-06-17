#!/usr/bin/python

# a Crazy(House) board is a chessboard with a little holding area to the side

import re
import Tkinter

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
        self.chessBoard.draw()
        # right side
        self.holdingBoard = HoldingBoard.HoldingBoard(self, pieceWidth, pieceHeight)
        self.holdingBoard.draw()

        self.width = self.chessBoard.width + self.holdingBoard.width
        self.height = self.chessBoard.height

        #self.chessBoard.pack(side=Tkinter.LEFT)
        #self.holdingBoard.pack(side=Tkinter.LEFT)

        self.chessBoard.grid(row=0, column=0, padx=2)
        self.holdingBoard.grid(row=0, column=1, pady=2)

        #print self.chessBoard.grid_info()
        #print self.holdingBoard.grid_info()
        #w = Tkinter.Label(self, text="row0_column2", bg="red", fg="white")
        #w.grid(row=0, column=2)
        #w = Tkinter.Label(self, text="row1_column2", bg="red", fg="white")
        #w.grid(row=1, column=2)
        #w = Tkinter.Label(self, text="row2_column2", bg="red", fg="white")
        #w.grid(row=2, column=2)
        #w = Tkinter.Label(self, text="Red", bg="red", fg="white")
        #w.grid(row=0, column=0)
        #w = Tkinter.Label(self, text="Red", bg="red", fg="white")
        #w.grid(row=0, column=0)

    def setFEN(self, fen):
        # is normal FEN string, except the 9'th rank designates the holding area
        # eg input: 
        # r2k1r2/pbppNppp/1p2p1nb/1P5N/3N4/4Pn1q/PPP1QP1P/2KR2R1/BrpBBqppN w - - 45 56
        #
        # so we lazily split off the holdings rank, then send the rest to the chessboard
        [l,r] = re.split(r' ', fen, maxsplit=1)

        ranks = re.split(r'/', l)

        holdings = ''

        if len(ranks) == 8:
            # no holdings
            pass
        elif len(ranks) == 9:   
            holdings = ranks[8]
        else:
            raise "invalid FEN string for CrazyBoard!"

        # normal chessboard
        normalFEN = '/'.join(ranks[0:8]) + ' ' + r
        self.chessBoard.setFEN(normalFEN)

        # holding board
        self.holdingBoard.setFEN(holdings)

    def getFEN(self):
        fen = self.chessBoard.getFEN()

        # split off ranks
        [l,r] = re.split(r' ', fen, maxsplit=1)

        # add holdings rank
        l = l + '/' + self.holdingBoard.getFEN()
        
        # reassemble, return
        return l + ' ' + r

    def sanGetPieceAt(self, square):
        return self.chessBoard.sanGetPieceAt(square)

    def execMoveSan(self, move):
        pieceChangeColorMap = {'p':'P', 'P':'p', \
                               'r':'R', 'R':'r', \
                               'b':'B', 'B':'b', \
                               'n':'N', 'N':'n', \
                               'q':'Q', 'Q':'q'}

        # filter out drops (normal chessboard doesn't understand)
        m = re.match('^([prnbqkPRNBQK])@([a-h][1-8])\+?$', move)
        if m:
            self.holdingBoard.removePiece(m.group(1))
            self.chessBoard.sanSetPieceAt(m.group(2), m.group(1))
            self.chessBoard.toggleTurn()
        else:
            # for other moves, make the chessboard make them
            self.chessBoard.execMoveSan(move)

            # but add captured pieces to holdings
            if self.transferPieces:
                # captures (to add to holdings)
                m = re.search('x([a-h][1-8])', move)
                if m:
                    self.holdingBoard.addPiece( \
                        pieceChangeColorMap[ \
                            self.board.sanGetPieceAt(m.group(1)) \
                        ] \
                    )

    def holdingAddPiece(self, p):
        self.holdingBoard.addPiece(p)

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
   
        self.cb = CrazyBoard(self)
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
    root.wm_title("CrazyBoard Test\n")

    # holding board on root
    cbt = CrazyBoardTest(root)
    cbt.pack()


    # run
    root.mainloop() 

if __name__ == "__main__":
    doTest()

