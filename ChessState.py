#!/usr/bin/python

# Copyright 2012-2016 Andrew Lamoureux
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
import pdb
import copy
import Common
import ChessMove

class ChessState:
    def __init__(self, fen = ''):

        if fen:
            self.fromFEN(fen)

    def fromFEN(self, fen):
        # board map is like:
        # bm['activePlayer'] : 'w'
        # bm['castleAvail'] : 'KQkq'
        # bm['enPassTarget'] : 'e3'
        # bm['halfMoveClock'] : 0
        # bm['fullMoveNum'] : 2
        # bm['a8'] = 'r'
        # bm['b8'] = 'n'
        # ...
        self.squares = {}
    
        # split off the piece placement data
        [places, self.activePlayer, self.castleAvail, self.enPassTarget, \
            self.halfMoveClock, self.fullMoveNum] = re.split(' ', fen)
   
        self.halfMoveClock = int(self.halfMoveClock)
        self.fullMoveNum = int(self.fullMoveNum)

        sqrSan = iter(Common.squaresSan)
    
        for c in places:
            # map normal pieces
            if c in 'PRQKNBprqknb':
                self.squares[sqrSan.next()] = c
            # map blank squares
            elif c in '12345678':
                for j in range(int(c)):
                    self.squares[sqrSan.next()] = ' '
            # rank separator
            elif c == '/':
                pass
            # ???
            else:
                raise Exception('unknown character \'%s\' in fen' % c)
    
    def toFEN(self):
        rankStrs = []
    
        for rank in Common.ranksSan:
            rankStr = ''
            for sq in rank:
                m = self.squares[sq]
                if m == ' ':
                    if rankStr and rankStr[-1] in '12345678':
                        rankStr = rankStr[:-1] + str(int(rankStr[-1]) + 1)
                    else:
                        rankStr += '1'
                else:
                    rankStr += m
    
            # add to list of ranks
            rankStrs.append(rankStr)
    
        # return it all
        result = ''
        result += '/'.join(rankStrs)
        result += ' ' + self.activePlayer
        if self.castleAvail:
            result += ' ' + self.castleAvail
        else:
            result += ' -'
        result += ' ' + self.enPassTarget
        result += ' ' + str(self.halfMoveClock)
        result += ' ' + str(self.fullMoveNum)
        return result
    
    def occupancy(self):
        result = []
        
        # is it a dictionary?
        for sqrCode in Common.squaresSan:
            if self.squares[sqrCode] != ' ':
                result.append(1)
            else:
                result.append(0)
    
        return result        
    
    #--------------------------------------------------------------------------
    # NEXT STATE COMPUTATION
    #--------------------------------------------------------------------------
    def transition(self, move):

        newBoardState = copy.deepcopy(self)
    
        m = re.match(Common.regexSanChess, move.san)
        if not m:
            raise Exception("cannot parse move: %s" % move)
            
        if self.halfMoveClock >= 50:
            raise Exception("cannot process further moves! halfmove clock expired (it's %d)!" % self.halfMoveClock)

        # deal with either castle
        if m.group('kCastle') or m.group('qCastle'):
            if self.isInCheck():
                raise Exception("illegal castle! currently in check!")

        # BUG TODO: check that squares in-between are empty and not attacked

        srcSquare = None

        # deal with king castling
        #
        if m.group('kCastle'):
            move.flags['CASTLE'] = 1

            if newBoardState.activePlayer == 'w':
                if newBoardState.squares['e1'] != 'K' or newBoardState.squares['h1'] != 'R':
                    raise Exception("illegal kingside castle! (square not correct)")
    
                if not 'K' in newBoardState.castleAvail:
                    raise Exception("illegal kingside castle! (availability gone)")


                newBoardState.squares['h1'] = ' '
                newBoardState.squares['e1'] = ' '
                newBoardState.squares['g1'] = 'K'
                newBoardState.squares['f1'] = 'R'
    
            else:
                if newBoardState.squares['e8'] != 'k' or newBoardState.squares['h8'] != 'r':
                    raise Exception("illegal kingside castle!")
    
                if not 'k' in newBoardState.castleAvail:
                    raise Exception("illegal kingside castle! (availability gone)")
    
                newBoardState.squares['h8'] = ' '
                newBoardState.squares['e8'] = ' '
                newBoardState.squares['g8'] = 'k'
                newBoardState.squares['f8'] = 'r'
                
        # deal with queen castling
        #
        elif m.group('qCastle'):
            move.flags['CASTLE'] = 1
    
            if newBoardState.activePlayer == 'w':
                if newBoardState['e1'] != 'K' or newBoardState['a1'] != 'R':
                    raise Exception("illegal queenside castle!")
    
                if not 'Q' in newBoardState.castleAvail:
                    raise Exception("illegal kingside castle! (availability gone)")
    
                newBoardState.squares['a1'] = ' '
                newBoardState.squares['e1'] = ' '
                newBoardState.squares['c1'] = 'K'
                newBoardState.squares['d1'] = 'R'

            else:
                if newBoardState.squares['e8'] != 'k' or newBoardState.squares['a8'] != 'r':
                    raise Exception("illegal queenside castle!")
    
                if not 'q' in newBoardState.castleAvail:
                    raise Exception("illegal kingside castle! (availability gone)")
    
                newBoardState.squares['a8'] = ' '
                newBoardState.squares['e8'] = ' '
                newBoardState.squares['c8'] = 'k'
                newBoardState.squares['d8'] = 'r'
    
        # deal with non-castling moves
        #
        else:
            srcPiece = m.group('srcPiece') or 'P'
            srcHint = m.group('srcHint')
            action = m.group('action')
            dstSquare = m.group('dstSquare')
            promote = m.group('promote')
            check = m.group('check')
    
            #print "original move: -%s-" % move
            #print "srcPiece: ", srcPiece
            #print "srcHint: ", srcHint
            #print "dstSquare: ", dstSquare
    
            # resolve the srcSquare
            if srcHint and re.match(r'^[a-h][1-8]$', srcHint):
                # given a full hint, source square is resolved
                srcSquare = srcHint
            else:
                # where could piece have come from?
                srcSquares = []
                if action == 'x':
                    if newBoardState.squares[dstSquare] == ' ':
                        if srcPiece != 'P' or dstSquare != newBoardState.enPassTarget:
                            raise Exception("capture onto empty square?")
    
                    srcSquares = newBoardState.getAttackingSquares(dstSquare, srcPiece)
                else:
                    srcSquares = newBoardState.getMoveSourceSquares(dstSquare, srcPiece)
    
                # filter based on the hint
                if srcHint and re.match(r'^[1-8]$', srcHint):
                    # given a rank hint, consider only source squres in this rank
                    srcSquares = filter(lambda x: x[1] == srcHint, srcSquares)
                elif srcHint and re.match(r'^[a-h]$', srcHint):
                    # given a file hint, consider only source squares in that file
                    srcSquares = filter(lambda x: x[0] == srcHint, srcSquares)
               
                # (rare) filter moves that would result in check
                if len(srcSquares) > 1:
                    srcSquares = []
    
                    for sqr in srcSquares:
                        # create hypothetical board with piece removed
                        tempState = copy.deepcopy(newBoardState)
    
                        # with piece moved
                        if dstSquare:
                            tempState.squares[dstSquare] = tempState.squares[sqr]
                        tempStates.squares[sqr] = ' '
    
                        # if hypothetical board does not produce a king check
                        if not tempState.isInCheck():
                            srcSquares.append(sqr)
                
                if len(srcSquares) < 1:
                    raise Exception("could not find source square for move %s" % move)
    
                # hopefully we're left with one square by now
                if len(srcSquares) > 1:
                    raise Exception(("ambiguous source square for move %s " + \
                        "(could be any of %s)") % (move, str(srcSquares)))
                   
                srcSquare = srcSquares[0]
    
            # at this point we've resolved the often confusing SAN into an unambiguous canonical
            # source/dst square - example: e4 into "e2e4"
           
            move.canonical = srcSquare + dstSquare
    
            # now actually
            # modify the state
     
            # en-passant piece removal
            if srcPiece in 'pP' and newBoardState.squares[dstSquare] == ' ' and dstSquare == newBoardState.enPassTarget:
                if dstSquare[1]=='6':
                    newBoardState.squares[dstSquare[0]+'5'] = ' '
                elif dstSquare[1]=='3':
                    newBoardState.squares[dstSquare[0]+'4'] = ' '
                else:
                    raise Exception("destination square %s should be on rank 3 or 6" % \
                        dstSquare)

                move.flags['CAPTURE'] = 1
    
            # en-passant next state calculation
            newBoardState.enPassTarget = '-'
            if srcPiece in 'pP':
                if srcSquare[0]==dstSquare[0]:
                    if srcSquare[1]=='2' and dstSquare[1]=='4':
                        newBoardState.enPassTarget = srcSquare[0] + '3'
                    elif srcSquare[1]=='7' and dstSquare[1]=='5':
                        newBoardState.enPassTarget = srcSquare[0] + '6'

            # mark capturing
            if newBoardState.squares[dstSquare] != ' ':
                move.flags['CAPTURE'] = 1

            # finalize movement
            newBoardState.squares[dstSquare] = newBoardState.squares[srcSquare]
            newBoardState.squares[srcSquare] = ' '

            # did it promote?
            if promote:
                newBoardState.squares[dstSquare] = Common.casePieceByPlayer(promote[1], newBoardState.activePlayer)
                move.canonical += Common.casePieceByPlayer(promote[1], newBoardState.activePlayer)

        # if the active player (the one who just moved) is in check, it's illegal
        if newBoardState.isInCheck():
            raise Exception("with state \"%s\" move \"%s\" results in self-check!" % (self.toFEN(), move.san))

        # active player loses castle rights if he castled, or moved king
        if m.group('qCastle') or m.group('kCastle') or self.squares[srcSquare] in 'kK':
            if self.activePlayer == 'w':
                newBoardState.castleAvail = re.sub('K', '', newBoardState.castleAvail)
                newBoardState.castleAvail = re.sub('Q', '', newBoardState.castleAvail)
            else:
                newBoardState.castleAvail = re.sub('k', '', newBoardState.castleAvail)
                newBoardState.castleAvail = re.sub('q', '', newBoardState.castleAvail)

      
        # halfmove clock reset after captures or pawn moves, incremented otherwise
        if ('CAPTURE' in move.flags) or (srcSquare and self.squares[srcSquare] in 'pP'):
            newBoardState.halfMoveClock = 0
        else:
            newBoardState.halfMoveClock += 1

        # swap whose turn it is
        if newBoardState.activePlayer == 'w':
            newBoardState.activePlayer = 'b'
        else:
            newBoardState.activePlayer = 'w'
            # fullmove clock increments after black's turn
            newBoardState.fullMoveNum += 1;
    
        # mark if this checks
        if newBoardState.isInCheck():
            move.flags['CHECKS'] = 1
        
        # return the move properties and the new board state
        return newBoardState
    
    #--------------------------------------------------------------------------
    # SAN STUFF
    #--------------------------------------------------------------------------
    # given 'b4' and [-1,-1] (move left one, down one), return a3
    # (it's Cartesian)
    def sanSquareShift(self, square, movement):
        x = {'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6, 'g':7, 'h':8}[square[0]]
        y = int(square[1])
    
        x += movement[0]
        y += movement[1]
    
        if x<1 or x>8 or y<1 or y>8:
            return None
    
        return {1:'a', 2:'b', 3:'c', 4:'d', 5:'e', 6:'f', 7:'g', 8:'h'}[x] + str(y)
       
    def sanSquareShifts(self, square, movements):
        return map(lambda x: self.sanSquareShift(square, x), movements)
    
    def sanIsSameRank(self, a, b):
        return a[1] == b[1]
    
    def sanIsSameFile(self, a, b):
        return a[0] == b[0]
    
    #--------------------------------------------------------------------------
    # SQUARE LOGIC
    #--------------------------------------------------------------------------
    
    # given a square and piece type, return the possible source squares from
    # which this piece could move from
    def getMoveSourceSquares(self, destSquare, pieceType):
        answers = []
    
        # these "searchLines" across the chessboard define a line of search that
        # could be blocked by interposing pieces
        searchLinesPawnB = []
        if destSquare in ['a5','b5','c5','d5','e5','f5','g5','h5']:
            searchLinesPawnB.append([[0,1],[0,2]])
        else:
            searchLinesPawnB.append([[0,1]])
    
        searchLinesPawnW = []
        if destSquare in ['a4','b4','c4','d4','e4','f4','g4','h4']:
            searchLinesPawnW.append([[0,-1],[0,-2]])
        else:
            searchLinesPawnW.append([[0,-1]])
    
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
                        'Pb': searchLinesPawnB, 'Pw':searchLinesPawnW, \
                        'Rb': searchLinesRook, 'Rw':searchLinesRook, \
                        'Nb': searchLinesKnight, 'Nw':searchLinesKnight, \
                        'Qb': searchLinesQueen, 'Qw':searchLinesQueen, \
                        'Bb': searchLinesBishop, 'Bw':searchLinesBishop, \
                        'Kb': searchLinesKing, 'Kw':searchLinesKing }
       
        # case of piecetype shouldn't matter
        pieceType = pieceType.upper()
    
        matchPiece = pieceType
        if self.activePlayer == 'w':
            #pdb.set_trace()
            matchPiece = matchPiece.upper()
        else:
            matchPiece = matchPiece.lower()
    
        for searchLine in pieceToSearchLines[pieceType + self.activePlayer]:
            for sq in filter(lambda x: x, self.sanSquareShifts(destSquare, searchLine)):
                #print "a sq from self.sanSquareShifts: " + sq + " (has square %s ==? %s)" % (boardMap[sq], matchPiece)
    
                # we purposely take just the first character here (workaround for, say, 'Q~')
                # (for chess there is only one character anyways)
                p = self.squares[sq][0]
                # empty square? keep along the searchLine
                if p == ' ':
                    continue
                # found it?
                if p == matchPiece:
                    answers.append(sq)
                # found or not, square is occupied and blocks attacking bishop
                break
    
        return answers
    
    def getAttackingSquares(self, destSquare, pieceType):
        l = []
    
        # pawn is only piece that attacks differently than it moves
        if pieceType.upper() == 'P':
            if self.activePlayer == 'b':
                l = self.sanSquareShifts(destSquare, [[-1,1], [1,1]])
            else:
                l = self.sanSquareShifts(destSquare, [[1,-1], [-1,-1]])
    
            # filter squares that actually contain that player
            l = filter(lambda x: x, l)
            l = filter(lambda x: self.squares[x] == Common.casePieceByPlayer(pieceType, self.activePlayer), l)
    
        else:
            l = self.getMoveSourceSquares(destSquare, pieceType)
            l = filter(lambda x: x, l)
    
        return l
    
    def getLegalMoves(self):
        moves = []
        moves_ = []
    
        # logic:
        # for every empty square DESTINATION, see if move possible
        # for every opponent occupied square DESTINATION, see if attack possible
    
        for sqrDest in Common.squaresSan:
            moveTempl = ChessMove.ChessMove()
            moveTempl.player = self.activePlayer
            moveTempl.moveNum = int(self.fullMoveNum)/2
    
            if self[sqrDest] == ' ':
                #print "trying to go to square %s" % sqrDest
                for pieceType in 'rnbpqk':
                    for sqrSource in self.getMoveSourceSquares(sqrDest, pieceType):
                        move = copy.deepcopy(moveTempl)
                        move.san = '%s%s' % (pieceType, sqrDest)
                        move.canonical = '%s%s' % (sqrSource, sqrDest)
                        #print "(move) adding: %s" % str(move.canonical)
                        moves_.append(move)
    
            elif Common.coloredPieceToPlayer(self[sqrDest]) == Common.togglePlayer(self['activePlayer']):
                #print "trying to attack square %s" % sqrDest
                for pieceType in 'rnbpqk':
                    for sqrSource in self.getAttackingSquares(sqrDest, pieceType):
                        move = copy.deepcopy(moveTempl)
                        move.san = '%s%s' % (pieceType, sqrDest)
                        move.canonical = '%s%s' % (sqrSource, sqrDest)
                        #print "%s is a capture!" % (move.canonical)
                        move.flags['CAPTURE'] = 1
                        #print "(attack) adding: %s" % str(move)
                        moves_.append(move)
    
        # filter out moves that result in self-check
        for move in moves_:
            m = re.match(r'^([a-h][1-8])([a-h][1-8])$', move.canonical)
    
            [sqrSource, sqrDest] = [m.group(1), m.group(2)]
    
            tempState = copy.deepCopy(boardMap)
            tempState[m.group(2)] = tempState[m.group(1)]
            tempState[m.group(1)] = ' '
    
            # if hypothetical board does not produce a king check
            if not tempState.isInCheck():
                moves.append(move)
    
        return moves
    
    def isInCheck(self):
        us = self.activePlayer
        them = Common.togglePlayer(us)

        #print "checking if " + us + " is in check"
        coloredKing = Common.casePieceByPlayer('k', us)
    
        # find king square
        sqrKing = ''
        for sqr, piece in self.squares.iteritems():
            if piece == coloredKing:
                sqrKing = sqr
                break
    
        if not sqrKing:
            raise Exception("could not find the -%s- king -%s-!" % (us, coloredKing))
    
        # for all types of pieces, see if there are any attacking squares:
        for piece in 'QKRBNP':
            # found! in check!
            #print "opp is: %s" % opp
            #print "piece is: %s" % piece
            #print "sqrKing is: %s" % sqrKing

            # temporarily switch active player to see if they can attack us
            self.activePlayer = them
            attackSquares = self.getAttackingSquares(sqrKing, piece)
            self.activePlayer = us

            if attackSquares:
                return True
    
        # none found? not in check
        return False
          
    #--------------------------------------------------------------------------
    # INTERNALS
    #--------------------------------------------------------------------------
    def copy(self):
        return copy.deepcopy(self)

    def __getitem__(self, what):
        if what == 'activePlayer':
            return self.activePlayer
        if what == 'castleAvail':
            return self.castleAvail
        if what == 'enPassTarget':
            return self.enPassTarget
        if what == 'halfMoveClock':
            return self.halfMoveClock
        if what == 'fullMoveNum':
            return self.fullMoveNUm

        if re.match(Common.regexSquare, what):
            return self.squares[what]

        raise ValueError("invalid request to BoardState: " + what)

    def __str__(self):
        result = ''

        result += '+---+---+---+---+---+---+---+---+\n'

        for rank in '87654321':
            result += '|'
            for file_ in 'abcdefgh':
                result += ' %s |' % self.squares[file_ + rank]
            result += '\n+---+---+---+---+---+---+---+---+\n'

        result += 'FEN: %s\n' % self.toFEN()
        result += 'activePlayer: %s\n' % self.activePlayer
        result += 'castleAvail: %s\n' % self.castleAvail
        result += 'enPassTarget: %s\n' % self.enPassTarget
        result += 'halfMoveClock: %s\n' % self.halfMoveClock
        result += 'fullMoveNum: %s\n' % self.fullMoveNum

        return result

#--------------------------------------------------------------------------
# MAIN()
#--------------------------------------------------------------------------

if __name__ == '__main__':
    state = ChessState()

    print "TESTING FIRST MOVE!"
    state.fromFEN('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0')
    print state
    state = state.transition('e4')
    print state
    print state.toOccupancyArray()

    print "TESTING CASTLE!"
    state.fromFEN('r1bqk2r/1ppp1ppp/1p2np2/8/3PP3/2P2N2/PP3PPP/R2QK2R b KQkq - 0 0')
    print state
    state = state.transition('O-O')
    print state
    print state.toOccupancyArray()

    
