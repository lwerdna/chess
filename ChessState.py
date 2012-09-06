#!/usr/bin/python

class ChessState:
    def __init__(self, fen):
        # FEN string representing the state
        self.fen = fen

        # more convenient state representation that we keep
        self.state = []
        self.activePlayer = '' # [wb]
        self.castleAvail = '' # -?K?Q?k?q?
        self.enPassantTarget = '' # (-|([a-h][36]))
        self.halfMoveClock = '' # \d+
        self.fullMoveNum = '' # \d+

    def expandFen(self):
        # just replace all digits with with 1
        fen = self.

    def getFEN(self):
        self.fen = ''

        for i,p in enumerate(self.state):
            if p == ' ':
                self.fen += '1'
            else:
                self.fen += p

            if (i+1) % 8 == 0 and i != len(self.state)-1:
                self.fen += '/'

        self.fen = self.fen + ' ' + ' '.join( \
            [self.activePlayer, self.castleAvail, self.enPassantTarget, \
                self.halfMoveClock, self.fullMoveNum])

        return self.fen

    def setFEN(self, fen):
        # fen consists of 6 fields separated by whitespace
        [places, self.activePlayer, self.castleAvail, self.enPassantTarget, \
            self.halfMoveClock, self.fullMoveNum] = re.split(' ', fen)

        # FIELD 1
        # starts rank 8 (top, 8), goes down to rank 1 (bottom, 1)
        # starts file 1 (left, a), goes over to file 8 (right, h)
        rankPlaces = re.split('/', places)
        if len(rankPlaces) != 8:
            raise "FEN did not contain 8 ranks!"

        # expand the ranks to 64 string
        full64 = []
        for rank in rankPlaces:
            for sym in rank:
                if re.match(r'^\d$', sym):
                    full64 += ' '*int(sym)
                else:
                    full64 += sym
        
        if len(full64) != 64:
            raise "FEN did not contain 64 data!"

        # ok load that into the state
        self.state = list(full64)
 

    def nextState(self, move):
        if move == 'O-O':
            if self.activePlayer == 'w':
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
            if self.activePlayer == 'w':
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
    
            srcPiece = m.group('srcPiece') or {'w':'P', 'b':'p'}[self.activePlayer]
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
 

    #--------------------------------------------------------------------------
    # board access stuff
    #--------------------------------------------------------------------------
    def sanToStateIndex(self, square):
        return 8 * (8-int(square[1])) + \
            {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7}[square[0]] \

    # given 'a4', return the piece at a4
    def sanGetPieceAt(self, square):
        return self.state[self.sanToStateIndex(square)]

    def sanSetPieceAt(self, square, p):
        self.state[self.sanToStateIndex(square)] = p

    # given 'b4' and [-1,-1] (move left one, up one), return a5
    def sanSquareShift(self, square, movement):
        x = {'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6, 'g':7, 'h':8}[square[0]]
        y = int(square[1])

        x += movement[0]
        y += movement[1]

        if x<1 or x>8 or y<1 or y>8:
            return None

        return {1:'a', 2:'b', 3:'c', 4:'d', 5:'e', 6:'f', 7:'g', 8:'h'}[x] + \
            str(y)
   
    def sanSquareShifts(self, square, movements):
        return map(lambda x: self.sanSquareShift(square, x), movements)

    def sanIsSameRank(self, a, b):
        return a[1] == b[1]

    def sanIsSameFile(self, a, b):
        return a[0] == b[0]

    #--------------------------------------------------------------------------
    # PGN movetext parsing
    #--------------------------------------------------------------------------
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


