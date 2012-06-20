#!/usr/bin/python

import re
import sys
import Tkinter

import Common
import ChessBoard
import CrazyBoard
import BugBoard
import BpgnParser

class BpgnViewer(Tkinter.Frame):
    def __init__(self, parent, pieceWidth=48, pieceHeight=48):
        Tkinter.Frame.__init__(self, parent)

        self.parent = parent
       
        self.boardMap = {}

        self.bpgnParser = None
        self.moveNumber = 0

        # two boards
        self.bugBoard = BugBoard.BugBoard(self, pieceWidth, pieceHeight)

        self.bugBoard.setBugFEN(Common.initBugFEN)

        # status thingies
        self.playerTimeAValue = 0
        self.playerTimeaValue = 0
        self.playerTimeBValue = 0
        self.playerTimebValue = 0

        self.playerInfoA = Tkinter.Label(self, text="", bg="white", fg="black")
        self.playerTimeA = Tkinter.Label(self, text="", bg="green", fg="black")
        self.playerInfob = Tkinter.Label(self, text="", bg="black", fg="white")
        self.playerTimeb = Tkinter.Label(self, text="", bg="green", fg="black")
        self.playerInfoa = Tkinter.Label(self, text="", bg="black", fg="white")
        self.playerTimea = Tkinter.Label(self, text="", bg="green", fg="black")
        self.playerInfoB = Tkinter.Label(self, text="", bg="white", fg="black")
        self.playerTimeB = Tkinter.Label(self, text="", bg="green", fg="black")
    
        # buttons go into frame
        self.btnFrame = Tkinter.Frame(self)
        self.btnStart = Tkinter.Button(self.btnFrame, text="|<", command=self.btnBackwardCb)
        self.btnBackward = Tkinter.Button(self.btnFrame, text="<", command=self.btnBackwardCb)
        self.btnForward = Tkinter.Button(self.btnFrame, text=">", command=self.btnForwardCb)
        self.btnEnd = Tkinter.Button(self.btnFrame, text=">|", command=self.btnForwardCb)

        self.playerInfoa.grid(row=0, column=1, sticky=Tkinter.E + Tkinter.W)
        self.playerTimea.grid(row=0, column=0)
        self.playerInfoB.grid(row=0, column=2, sticky=Tkinter.E + Tkinter.W)
        self.playerTimeB.grid(row=0, column=3)
        self.bugBoard.grid(row=1, column=0, columnspan=4)
        self.playerInfoA.grid(row=2, column=1, sticky=Tkinter.E + Tkinter.W)
        self.playerTimeA.grid(row=2, column=0)
        self.playerInfob.grid(row=2, column=2, sticky=Tkinter.E + Tkinter.W)
        self.playerTimeb.grid(row=2, column=3)

        self.btnStart.pack(side=Tkinter.LEFT)
        self.btnBackward.pack(side=Tkinter.LEFT)
        self.btnForward.pack(side=Tkinter.LEFT)
        self.btnEnd.pack(side=Tkinter.LEFT)
        self.btnFrame.grid(row=3, columnspan=4)

    def loadBpgn(self, path):
        match = self.match = BpgnParser.MatchIteratorFile(path).next()
        print match
        match.populateStates()


        self.playerInfoA.config(text= (match.tags['WhiteA'] + ' [%s]' % match.tags['WhiteAElo']))
        self.playerInfoa.config(text= (match.tags['BlackA'] + ' [%s]' % match.tags['BlackAElo']))
        self.playerInfoB.config(text= (match.tags['WhiteB'] + ' [%s]' % match.tags['WhiteBElo']))
        self.playerInfob.config(text= (match.tags['BlackB'] + ' [%s]' % match.tags['BlackBElo']))

        m = re.match(r'^(\d+)\+(\d+)$', match.tags['TimeControl'])
        initTime = float(m.group(1))

        self.playerTimeAValue = self.playerTimeaValue = \
            self.playerTimeBValue = self.playerTimebValue = initTime

        self.playerTimeA.config(text=('%s' % initTime))
        self.playerTimea.config(text=('%s' % initTime))
        self.playerTimeB.config(text=('%s' % initTime))
        self.playerTimeb.config(text=('%s' % initTime))

        self.moveNumber = 0

    def processMoveTime(self, move):
        m = re.match(r'^\d+([AaBb]).*{(.*)}$', move)
        player = m.group(1)
        time = float(m.group(2))

        playerToTimeValue = { \
            'a' : self.playerTimeaValue, 'A' : self.playerTimeAValue, \
            'b' : self.playerTimebValue, 'B' : self.playerTimeBValue \
        }

        playerToTimeLabel = { \
            'a' : self.playerTimea, 'A' : self.playerTimeA, \
            'b' : self.playerTimeb, 'B' : self.playerTimeB \
        }

        playerToRivalLabel = { \
            'a' : self.playerTimeA, 'A' : self.playerTimea, \
            'b' : self.playerTimeB, 'B' : self.playerTimeb \
        }

        playerToRivalTime = { \
            'a' : self.playerTimeAValue, 'A' : self.playerTimeaValue, \
            'b' : self.playerTimeBValue, 'B' : self.playerTimebValue \
        }

        if player=='a':
            self.playerTimeaValue = time
        if player=='A':
            self.playerTimeAValue = time
        if player=='b':
            self.playerTimebValue = time
        if player=='B':
            self.playerTimeBValue = time

        if time < playerToRivalTime[player]:
            playerToTimeLabel[player].config(background="red")
            playerToRivalLabel[player].config(background="green")
        else:
            playerToTimeLabel[player].config(background="green")
            playerToRivalLabel[player].config(background="red")

        playerToTimeLabel[player].config(text=('%s' % time))

    def showStateAfterMove(self):
        self.processMoveTime(self.match.moves[self.moveNumber])
        self.bugBoard.setBugFEN(self.match.states[self.moveNumber])
        self.bugBoard.draw()

    def btnBackwardCb(self):
        if self.moveNumber <= 0:
            print "at beginning"
        else:
            self.moveNumber -= 1;

        self.showStateAfterMove()

    def btnForwardCb(self):
        if self.moveNumber >= len(self.match.moves)-1:
            print "no more moves"
        else:
            self.moveNumber += 1

        self.showStateAfterMove()

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
