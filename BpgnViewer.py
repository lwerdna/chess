#!/usr/bin/python

# a Crazy(House) board is a chessboard with a little reserve area to the side

import re
import Tkinter

import ChessBoard
import ReserveBoard
import CrazyBoard

class BpgnViewer(Tkinter.Frame):
    def __init__(self, parent, pieceWidth=48, pieceHeight=48):
        Tkinter.Frame.__init__(self, parent)

        self.parent = parent

        # two boards
        self.leftBoard = CrazyBoard.CrazyBoard(self, pieceWidth, pieceHeight)
        self.rightBoard = CrazyBoard.CrazyBoard(self, pieceWidth, pieceHeight)
        self.rightBoard.flip()
        self.rightBoard.draw()

        self.width = 2*self.leftBoard.width
        self.height = 2*self.leftBoard.height

        # status thingies
        self.a1Status = Tkinter.Label(self, text="JackJohnson [00:00]", bg="white", fg="black")
        self.a2Status = Tkinter.Label(self, text="BillBenson [00:00]", bg="black", fg="white")
        self.b1Status = Tkinter.Label(self, text="JerryJaundice [00:00]", bg="black", fg="white")
        self.b2Status = Tkinter.Label(self, text="KellyKapowsky [00:00]", bg="white", fg="black")
    
        # buttons
        self.btnBackward = Tkinter.Button(self, text="<", command=self.btnBackwardCb)
        self.btnForward = Tkinter.Button(self, text=">", command=self.btnForwardCb)

        self.b1Status.grid(row=0, column=0, sticky=Tkinter.E + Tkinter.W)
        self.b2Status.grid(row=0, column=1, sticky=Tkinter.E + Tkinter.W)
        self.leftBoard.grid(row=1, column=0)
        self.rightBoard.grid(row=1, column=1)
        self.a1Status.grid(row=2, column=0, sticky=Tkinter.E + Tkinter.W)
        self.a2Status.grid(row=2, column=1, sticky=Tkinter.E + Tkinter.W)
        self.btnBackward.grid(row=3, column=0)
        self.btnForward.grid(row=3, column=1)

    def btnBackwardCb(self):
        print "You go backward"

    def btnForwardCb(self):
        print "You go forward"
def doTest():
    # root window
    root = Tkinter.Tk()
    root.wm_title("BpgnViewer")
    root.configure(background = 'black')

    # reserve board on root
    cb = BpgnViewer(root)
    cb.grid()

    # run
    root.mainloop() 

if __name__ == "__main__":
    doTest()

