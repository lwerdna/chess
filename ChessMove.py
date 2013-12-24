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

class ChessMove:
    def __init__(self, player_='', moveNum_='', san_='', canonical_='', comments_=None, time_=None, flags_=None):
        self.player = player_       # ['w','b', 'W', 'B'] in chess, ['a','A','b','B'] in bug
        self.moveNum = moveNum_     # 1,2,3,...
        self.san = san_             # bxh3
        self.canonical = canonical_ # c7h3
        self.comments = comments_   # [53.057, 'adds pressure to kingside'] (input is like "{53.057}")
        self.time = time_           # 118.953
        self.variations = []

        # see "Default Parameter Values in Python" http://effbot.org/zone/default-values.htm
        # for why to do this...
        if comments_ is None:
            self.comments = {}
        else:
            self.comments = comments_         # 'TIME_FORFEIT', 'CAPTURE', 'PROMOTE', etc.

        if flags_ is None:
            self.flags = {}
        else:
            self.flags = flags_         # 'TIME_FORFEIT', 'CAPTURE', 'PROMOTE', etc.

    def addComment(self, comment):
        # time comment?
        if re.match(r'\d+\.\d+', comment):
            self.time = float(comment)

        # forfeit on time comment? (these are repeated in bughouse-db results)
        elif re.search('forfeits on time', comment):
            self.flags['TIME_FORFEIT'] = 1

        # add to list
        self.comments.append(comment)

    def fromSan(self, san, boardMap):
        pass 

    def strSmall(self):
        answer = ''

        # chess
        if self.player in ['w', 'b', 'W', 'B']:
            if self.player in ['w', 'W']:
                answer = str(self.moveNum) + '.' + self.san
            else:
                answer = str(self.moveNum) + '... ' + self.san
        # other (bug, crazy)
        else:
            answer = str(self.moveNum) + self.player + '.' + self.san
    
        return answer

    def __str__(self):
        answer = self.strSmall()

        for c in self.comments:
            if c:
                answer += ' {%s}' % c

        if self.variations:
            answer += " "
            answer += " ".join(self.variations)

        return answer



