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

# ChessMatch is collection of {ChessState, ChessMove}

# a ChessMatch is considered a graph:
# - nodes are state snapshots of the board
# - edges/transitions are the moves (encoded in the movetext's san)
#

class ChessMatch:
    def __init__(self):
        self.tags = {}

        # these parallel each other
        # states[0] is the initial ChessState
        #  edges[0] is the transition that transforms states[0] into states[1]
        # ...and so on (states[i] is taken to states[i+1] due to edges[i])
        self.edges = []
        self.states = []

    def setMoves(self, moves):
        self.edges = moves

    def calcStates(self):
        # the list of transitions is enough to define any game (as it does in 
        # BPGN) however, we may want to explicitly make a representation of
        # every state so that we can analyze move i without calculating on move
        # j<i
        
