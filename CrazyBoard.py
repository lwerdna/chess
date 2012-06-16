#!/usr/bin/python

# a Crazy(House) board is a chessboard with a little reserve area to the side

import re
import Tkinter

import ChessBoard
import ReserveBoard

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
        self.reserveBoard = ReserveBoard.ReserveBoard(self, pieceWidth, pieceHeight)
        self.reserveBoard.draw()

        self.width = self.chessBoard.width + self.reserveBoard.width
        self.height = self.chessBoard.height

        #self.chessBoard.pack(side=Tkinter.LEFT)
        #self.reserveBoard.pack(side=Tkinter.LEFT)

        self.chessBoard.grid(row=0, column=0, padx=2)
        self.reserveBoard.grid(row=0, column=1, pady=2)

        #print self.chessBoard.grid_info()
        #print self.reserveBoard.grid_info()
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

        # reserve board
        self.reserveBoard.setFEN(holdings)

    def getFEN(self):
        fen = self.chessBoard.getFEN()

        # split off ranks
        [l,r] = re.split(r' ', fen, maxsplit=1)

        # add holdings rank
        l = l + '/' + self.reserveBoard.getFEN()
        
        # reassemble, return
        return l + ' ' + r

    def execMoveSan(self, move):
        pieceChangeColorMap = {'p':'P', 'P':'p'
                               'r':'R', 'R':'r'
                               'b':'B', 'B':'b'
                               'n':'N', 'N':'n'
                               'q':'Q', 'Q':'q'}

        # we mainly thunk through to ChessBoard
        self.chessBoard.execMoveSan(move)

        # but if transfering is enabled (normal CrazyHouse) we intercept:
        if self.transferPieces:
            # captures (to add to holdings)
            m = re.find('x([prnbqkPRNBQK])', move)
            if m:
                self.reserveBoard.addPiece(pieceChangeColorMap(m.group(1)))
        
            # drops (to remove from holdings)
            m = re.find('([prnbqkPRNBQK])@', move)
            if m:
                self.reserveBoard.removePiece(m.group(1))

    def flip(self):
        self.chessBoard.flip()
        self.reserveBoard.flip()

    def draw(self):
        self.chessBoard.draw()
        self.reserveBoard.draw()

def doTest():
    # root window
    root = Tkinter.Tk()
    root.wm_title("Crazy Board Test\n")
    root.configure(background = 'black')

    # reserve board on root
    cb = CrazyBoard(root)
    cb.grid()

    # run
    root.mainloop() 

if __name__ == "__main__":
    doTest()

