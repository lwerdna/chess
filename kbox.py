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

class KingBox(object):
    def __init__(self, initState):
        self.stateEmpty = [['.','.','.'],['.','.','.'],['.','.','.']]

        if initState:
            self.state = initState
        else:
            state = self.stateEmpty

    def __equal__(self, other):
        # equal if, equal after transformation

        others = []

        return self.state == other.state

        return False

    def flipVertical(self):
        stateNew = self.stateEmpty

        for i in range(3):
            for j in range(3):
                stateNew[i][j] = self.state[2-i][j]

        return KingBox(stateNew)

    def flipHorizontal(self):
        stateNew = self.stateEmpty

        for i in range(3):
            for j in range(3):
                stateNew[i][j] = self.state[i][2-j]

        return KingBox(stateNew)

    def flipDiagonal(self):
        stateNew = self.stateEmpty

        for i in range(3):
            for j in range(3):
                stateNew[i][j] = self.state[2-i][2-j]

        return KingBox(stateNew)

    def __str__(self):
        result = ''
        result += ''.join(self.state[0]) + '\n'
        result += ''.join(self.state[1]) + '\n'
        result += ''.join(self.state[2]) + '\n'
        return result;

if __name__ == '__main__':
    kb = KingBox([['X','X','.'], ['.','X','X'], ['.','.','.']])

    print kb
    print kb.flipVertical()
    print kb.flipHorizontal()
    print kb.flipDiagonal()

