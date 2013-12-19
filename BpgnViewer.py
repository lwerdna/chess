#!/usr/bin/python

# Copyright 2012, 2013 Andrew Lamoureux
#
# This file is a part of FunChess
#
# FunChess is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
        self.moveIndex = 0

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

        self.playerInfoA.config(text= (match.tags['WhiteA'] + ' [%s]' % match.tags['WhiteAElo']))
        self.playerInfoa.config(text= (match.tags['BlackA'] + ' [%s]' % match.tags['BlackAElo']))
        self.playerInfoB.config(text= (match.tags['WhiteB'] + ' [%s]' % match.tags['WhiteBElo']))
        self.playerInfob.config(text= (match.tags['BlackB'] + ' [%s]' % match.tags['BlackBElo']))

        self.setInitialTimes()

        self.moveIndex = -1
        self.stateIndex = 0
        self.bugBoard.setBugFEN(self.match.states[self.stateIndex])

        self.bugBoard.draw()

    def setInitialTimes(self):
        m = re.match(r'^(\d+)\+(\d+)$', self.match.tags['TimeControl'])
        initTime = float(m.group(1))

        self.playerTimeAValue = self.playerTimeaValue = \
            self.playerTimeBValue = self.playerTimebValue = initTime

        self.playerTimeA.config(text=('%s' % initTime))
        self.playerTimea.config(text=('%s' % initTime))
        self.playerTimeB.config(text=('%s' % initTime))
        self.playerTimeb.config(text=('%s' % initTime))

    def processMoveTime(self, player, time):
        time = float(time)
        #print "time is: ", time

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
        if self.moveIndex < 0:
            self.setInitialTimes()
        else:
            self.processMoveTime(self.match.moves[self.moveIndex].player, \
                                self.match.moves[self.moveIndex].comments[0])
            
        self.bugBoard.setBugFEN(self.match.states[self.moveIndex+1])

        self.bugBoard.draw()

    def btnBackwardCb(self):
        if self.moveIndex < 0:
            print "at beginning"
        else:
            self.moveIndex -= 1
            self.stateIndex -= 1

        self.showStateAfterMove()

    def btnForwardCb(self):
        # the x'th move transitions state x to x+1
        if self.moveIndex >= len(self.match.moves)-1:
            print "on last move"
        else:
            self.moveIndex += 1
            self.stateIndex += 1

        self.match.populateState(self.moveIndex)

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
