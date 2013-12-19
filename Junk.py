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

# a BugMatch is considered a graph:
# - nodes are state snapshots of the board
# - edges/transitions are the moves (encoded in the movetext's san)
#

class BugState:
    def __init__(self):

        # we add to the standard FEN encoding of pieces (p,b,n,r,q,k,P,B,N,R,Q,K)
        # by having a unique id for each piece -
        # this is so that search criteria can be made on holding pieces
        # eg "five moves lead to checkmate, no new drops were used"
        self.encToNormal = { \
            # board A, [a8...h8, a7...h7]
            'a':'r', 'b':'n', 'c':'b', 'd':'q', 'e':'k', 'f':'b', 'g':'n', 'h':'r', \
            'i':'p', 'j':'p', 'k':'p', 'l':'p', 'm':'p', 'n':'p', 'o':'p', 'p':'p', \
            # board A, [a2...h2, a1...h1]
            'q':'P', 'r':'P', 's':'P', 't':'P', 'u':'P', 'v':'P', 'w':'P', 'x':'P', \
            'y':'R', 'z':'N', 'A':'B', 'B':'Q', 'C':'K', 'D':'B', 'E':'N', 'F':'R', \
            # board B, [a8...h8, a7...h7]
            'G':'r', 'H':'n', 'I':'b', 'J':'q', 'K':'k', 'L':'b', 'M':'n', 'N':'r',  \
            'O':'p', 'P':'p', 'Q':'p', 'R':'p', 'S':'p', 'T':'p', 'U':'p', 'V':'p',  \
            # board A, [a2...h2, a1...h1]
            'W':'P', 'X':'P', 'Y':'P', 'Z':'P', '1':'P', '2':'P', '3':'P', '4':'P',  \
            '5':'R', '6':'N', '7':'B', '8':'Q', '9':'K', '0':'B', '!':'N', '@':'R' \
        }

        self.boardA = 'abcdefghijklmnop' + \
                      '                ' + \
                      '                ' + \
                      'qrstuvwxyzABCDEF'
        self.boardAh = ''

        self.boardB = 'GHIJKLMNOPQRSTUV' + \
                      '                ' + \
                      '                ' + \
                      'WXYZ1234567890!@'
        self.boardBh = ''

    # given a move in SAN, return the next state
    def transition(san):
    def getMoveSourceSquares(self, destSquare, piece):
        answers = []

        # these "searchLines" across the chessboard define a line of search that
        # could be blocked by interposing pieces
        searchLinesPawnB = [[[0,1]],[[0,2]]]
        searchLinesPawnW = [[[0,-1],[0,-2]]]

        searchLinesKing = [ \
            [[1,0]], \
            [[1,-1]], \
            [[0,-1]], \
            [[-1,-1]], \
            [[-1,0]], \
            [[-1,1]], \
            [[0,1]], \
            [[1,1]] \
        ]

        searchLinesKnight = [ \
            [[-2,1]], \
            [[-1,2]], \
            [[1,2]], \
            [[2,1]], \
            [[1,-2]], \
            [[2,-1]], \
            [[-1,-2]], \
            [[-2,-1]] \
        ]

        searchLinesRook = [ \
            [[-1,0],[-2,0],[-3,0],[-4,0],[-5,0],[-6,0],[-7,0]], \
            [[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0]], \
            [[0,1],[0,2],[0,3],[0,4],[0,5],[0,6],[0,7]], \
            [[0,-1],[0,-2],[0,-3],[0,-4],[0,-5],[0,-6],[0,-7]] \
        ]

        searchLinesBishop = [ \
            [[-1,-1],[-2,-2],[-3,-3],[-4,-4],[-5,-5],[-6,-6],[-7,-7]], \
            [[1,-1],[2,-2],[3,-3],[4,-4],[5,-5],[6,-6],[7,-7]], \
            [[-1,1],[-2,2],[-3,3],[-4,4],[-5,5],[-6,6],[-7,7]], \
            [[1,1],[2,2],[3,3],[4,4],[5,5],[6,6],[7,7]] \
        ]

        searchLinesQueen = searchLinesRook + searchLinesBishop

        pieceToSearchLines = { \
                        'p': searchLinesPawnB, 'P':searchLinesPawnW, \
                        'r': searchLinesRook, 'R':searchLinesRook, \
                        'n': searchLinesKnight, 'N':searchLinesKnight, \
                        'q': searchLinesQueen, 'Q':searchLinesQueen, \
                        'b': searchLinesBishop, 'B':searchLinesBishop, \
                        'k': searchLinesKing, 'K':searchLinesKing }

        for searchLine in pieceToSearchLines[piece]:
            for sq in filter(lambda x: x, self.sanSquareShifts(destSquare, searchLine)):
                #print "a sq from sanSquareShifts: " + sq

                p = self.sanGetPieceAt(sq)
                # empty square? keep along the searchLine
                if p == ' ':
                    continue
                # found it?
                if p == piece:
                    answers.append(sq)
                # found or not, square is occupied and blocks attacking bishop
                break

        return answers

    def getAttackSourceSquares(self, destSquare, piece):
        l = []

        if piece == 'p':
            l = self.sanSquareShifts(destSquare, [[-1,1], [1,1]])
        elif piece == 'P':
            l = self.sanSquareShifts(destSquare, [[1,-1], [-1,-1]])
        else:
            l = self.getMoveSourceSquares(destSquare, piece)

        return filter(lambda x: x, l)

    def execMoveSan(self, move):
        if move == 'O-O':
            if self.whoseTurn == 'w':
                self.sanSetPieceAt('h1', ' ')
                self.sanSetPieceAt('e1', ' ')
                self.sanSetPieceAt('g1', 'K')
                self.sanSetPieceAt('f1', 'R')
            else:
                self.sanSetPieceAt('h8', ' ')
                self.sanSetPieceAt('e8', ' ')
                self.sanSetPieceAt('g8', 'k')
                self.sanSetPieceAt('f8', 'r')
        elif move == 'O-O-O':
            if self.whoseTurn == 'w':
                self.sanSetPieceAt('a1', ' ')
                self.sanSetPieceAt('e1', ' ')
                self.sanSetPieceAt('c1', 'K')
                self.sanSetPieceAt('d1', 'R')
            else:
                self.sanSetPieceAt('a8', ' ')
                self.sanSetPieceAt('e8', ' ')
                self.sanSetPieceAt('c8', 'k')
                self.sanSetPieceAt('d8', 'r')
        else:
            regex = r'(?P<srcPiece>[PNBRQKpnbrqk])?' + \
                    r'(?P<srcHint>[a-h1-8]{1,2})?' + \
                    r'(?P<action>x)?' + \
                    r'(?P<dstSquare>[a-h][1-8])' + \
                    r'(?P<promote>=[PNBRQKpnbrqk])?' + \
                    r'(?P<check>[\+#])?'
    
            m = re.match(regex, move)
            if not m:
                raise Exception("cannot parse move: %s" % move)
    
            srcPiece = m.group('srcPiece') or {'w':'P', 'b':'p'}[self.whoseTurn]
            srcHint = m.group('srcHint')
            action = m.group('action')
            dstSquare = m.group('dstSquare')
            promote = m.group('promote')
            check = m.group('check')
    
            # resolve the srcSquare
            srcSquare = ''
            if srcHint and re.match(r'^[a-h][1-8]$', srcHint):
                # given a full hint, source square is resolved
                srcSquare = srcHint
            else:
                # where could piece have come from?
                srcSquares = []
                if action == 'x':
                    srcSquares = self.getAttackSourceSquares(dstSquare, srcPiece)
                else:
                    srcSquares = self.getMoveSourceSquares(dstSquare, srcPiece)
    
                if srcHint and re.match(r'^[1-8]$', srcHint):
                    # given a rank hint, consider only source squres in this rank
                    srcSquares = filter(lambda x: x[1] == srcHint, srcSquares)
                elif srcHint and re.match(r'^[a-h]$', srcHint):
                    # given a file hint, consider only source squares in that file
                    srcSquares = filter(lambda x: x[0] == srcHint, srcSquares)
    
                # hopefully we're left with one square by now
                if len(srcSquares) < 1:
                    raise Exception("could not find source square for move %s" % move)
                elif len(srcSquares) > 1:
                    raise Exception("ambiguous source square for move %s " + \
                        "(could be any of %s)" % (move, str(srcSquares)))
                   
                srcSquare = srcSquares[0]
       
            # modify the state
            self.sanSetPieceAt(srcSquare, ' ')
            self.sanSetPieceAt(dstSquare, srcPiece)

        # swap whose turn it is
        self.toggleTurn()


    def __str__(self):
        return '%s %s\n%s %s' % (self.boardA, self.boardAh, \
            self.boardB, self.boardBh)
        

class BugMatch:
    def __init__(self):
        self.tags = {}

        # these parallel each other
        # states[0] is the initial BugState
        #  edges[0] is the transition that transforms states[0] into states[1]
        self.edges = []
        self.states = []

    def setMoves(self, moves):
        self.edges = moves

    def calcStates(self):
        # the list of transitions is enough to define any game (as it does in 
        # BPGN) however, we may want to explicitly make a representation of
        # every state so that we can analyze move i without calculating on move
        # j<i
        
