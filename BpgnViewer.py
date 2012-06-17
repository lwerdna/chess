#!/usr/bin/python

import re
import sys
import Tkinter

import ChessBoard
import CrazyBoard
import ReserveBoard
import BugBoard
import BpgnParser

class BpgnViewer(Tkinter.Frame):
    def __init__(self, parent, pieceWidth=48, pieceHeight=48):
        Tkinter.Frame.__init__(self, parent)

        self.parent = parent
        
        self.initBFEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR/ w KQkq - 0 1 | rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR/ w KQkq - 0 1'

        self.bpgnParser = None
        # state after 0'th move is initial board state
        # state after 1'st move is in moveNumberToBFEN[1]
        # etc...
        self.moveNumberToBFEN = {0: self.initBFEN}
        # 0 is initial state, 1 is first move, etc.
        self.moveNumber = 0

        # two boards
        self.bugBoard = BugBoard.BugBoard(self, pieceWidth, pieceHeight)

        self.bugBoard.setBFEN(self.initBFEN)
        self.bugBoard.draw()

        # status thingies
        self.playerInfoA = Tkinter.Label(self, text="JackJohnson [00:00]", bg="white", fg="black")
        self.playerInfob = Tkinter.Label(self, text="BillBenson [00:00]", bg="black", fg="white")
        self.playerInfoa = Tkinter.Label(self, text="JerryJaundice [00:00]", bg="black", fg="white")
        self.playerInfoB = Tkinter.Label(self, text="KellyKapowsky [00:00]", bg="white", fg="black")
    
        # buttons go into frame
        self.btnFrame = Tkinter.Frame(self)
        self.btnBackward = Tkinter.Button(self.btnFrame, text="<", command=self.btnBackwardCb)
        self.btnForward = Tkinter.Button(self.btnFrame, text=">", command=self.btnForwardCb)

        self.playerInfoa.grid(row=0, column=0, sticky=Tkinter.E + Tkinter.W)
        self.playerInfoB.grid(row=0, column=1, sticky=Tkinter.E + Tkinter.W)
        self.bugBoard.grid(row=1, column=0, columnspan=2)
        self.playerInfoA.grid(row=2, column=0, sticky=Tkinter.E + Tkinter.W)
        self.playerInfob.grid(row=2, column=1, sticky=Tkinter.E + Tkinter.W)

        self.btnBackward.pack(side=Tkinter.LEFT)
        self.btnForward.pack(side=Tkinter.LEFT)
        self.btnFrame.grid(row=3, columnspan=2)

    def loadBpgn(self, path):
        p = self.bpgnParser = BpgnParser.Parser(path)

        self.playerInfoA.config(text= (p.tags['WhiteA'] + ' [%s]' % p.tags['WhiteAElo']))
        self.playerInfoa.config(text= (p.tags['BlackA'] + ' [%s]' % p.tags['BlackAElo']))
        self.playerInfoB.config(text= (p.tags['WhiteB'] + ' [%s]' % p.tags['WhiteBElo']))
        self.playerInfob.config(text= (p.tags['BlackB'] + ' [%s]' % p.tags['BlackBElo']))

        self.moveNumberToBFEN = {0: self.initBFEN}
        self.moveNumber = 0

    def btnBackwardCb(self):
        if self.moveNumber <= 0:
            print "at beginning"
        else:
            self.moveNumber -= 1;
            priorState = self.moveNumberToBFEN[self.moveNumber]
            self.bugBoard.setBFEN(priorState)
            self.bugBoard.draw()

    def btnForwardCb(self):
        if self.moveNumber >= len(self.bpgnParser.moves):
            print "no more moves"
        else:
            self.moveNumber += 1

            if self.moveNumber in self.moveNumberToBFEN:
                self.bugBoard.setBFEN(self.moveNumberToBFEN[self.moveNumber])
            else:
                move = self.bpgnParser.moves[self.moveNumber-1]
                self.bugBoard.execMoveSan(move) 
                self.moveNumberToBFEN[self.moveNumber] = self.bugBoard.getBFEN()
                #print "move[%d] = %s" % (self.moveNumber, self.moveNumberToBFEN[self.moveNumber])

            self.bugBoard.draw()

if __name__ == "__main__":
    # root window
    root = Tkinter.Tk()
    root.wm_title("BpgnViewer")
    root.configure(background = 'black')

    cb = BpgnViewer(root)
    cb.grid()

    cb.loadBpgn(sys.argv[1])

    # run
    root.mainloop() 
