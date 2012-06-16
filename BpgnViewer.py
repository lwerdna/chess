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

        self.bpgnParser = None
        self.moveIndexToBFEN = {}
        self.moveIndex = 0

        # two boards
        self.bugBoard = BugBoard.BugBoard(self, pieceWidth, pieceHeight)
        #self.bugBoard.setBFEN("r1b1k1nr/ppp1qpPp/2n5/1B1p1n1N/3P4/2P5/P1P1QPnP/R1BK2NR/PPBpp b kq - 142 164 | 2Nrkb1r/pPpbqppp/2p5/8/3N4/2P1B3/P1P1QPpP/R3K2R/Ppb w KQk - 142 163")
        self.bugBoard.draw()

        # status thingies
        self.a1Status = Tkinter.Label(self, text="JackJohnson [00:00]", bg="white", fg="black")
        self.a2Status = Tkinter.Label(self, text="BillBenson [00:00]", bg="black", fg="white")
        self.b1Status = Tkinter.Label(self, text="JerryJaundice [00:00]", bg="black", fg="white")
        self.b2Status = Tkinter.Label(self, text="KellyKapowsky [00:00]", bg="white", fg="black")
    
        # buttons go into frame
        self.btnFrame = Tkinter.Frame(self)
        self.btnBackward = Tkinter.Button(self.btnFrame, text="<", command=self.btnBackwardCb)
        self.btnForward = Tkinter.Button(self.btnFrame, text=">", command=self.btnForwardCb)

        self.b1Status.grid(row=0, column=0, sticky=Tkinter.E + Tkinter.W)
        self.b2Status.grid(row=0, column=1, sticky=Tkinter.E + Tkinter.W)
        self.bugBoard.grid(row=1, column=0, columnspan=2)
        self.a1Status.grid(row=2, column=0, sticky=Tkinter.E + Tkinter.W)
        self.a2Status.grid(row=2, column=1, sticky=Tkinter.E + Tkinter.W)

        self.btnBackward.pack(side=Tkinter.LEFT)
        self.btnForward.pack(side=Tkinter.LEFT)
        self.btnFrame.grid(row=3, columnspan=2)

    def loadBpgn(self, path):
        self.bpgnParser = BpgnParser.Parser(path)
        self.moveIndexToBFEN = {}
        self.moveIndex = 0

    def btnBackwardCb(self):
        print "You go backward"

    def btnForwardCb(self):
        print "You go forward"
        move = self.bpgnParser.moves[self.moveIndex]
        self.bugBoard.execMoveSan(move) 
        self.moveIndex += 1
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
