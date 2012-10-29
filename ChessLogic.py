import re
import Common

#--------------------------------------------------------------------------
# FEN <-> INTERNAL (PYTHON DICTIONARY) REPRESENTATION
#--------------------------------------------------------------------------
def fenToBoardMap(fen):
    mapping = {}

    # split off the piece placement data
    [places, mapping['activePlayer'], mapping['castleAvail'], mapping['enPassTarget'], \
        mapping['halfMoveClock'], mapping['fullMoveNum']] = re.split(' ', fen)

    squares = iter(Common.squaresSan)

    for c in places:
        # map normal pieces
        if c in 'PRQKNBprqknb':
            mapping[squares.next()] = c
        # map blank squares
        elif c in '12345678':
            for j in range(int(c)):
                mapping[squares.next()] = ' '
        # rank separator
        elif c == '/':
            pass
        # ???
        else:
            raise Exception('unknown character \'%s\' in fen' % c)

    return mapping

def boardMapToFen(mapping):
    rankStrs = []

    for rank in Common.ranksSan:
        rankStr = ''
        for sq in rank:
            m = mapping[sq]
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
    return ' '.join(['/'.join(rankStrs), mapping['activePlayer'], \
        mapping['castleAvail'], mapping['enPassTarget'], \
        mapping['halfMoveClock'], mapping['fullMoveNum']])

#--------------------------------------------------------------------------
# NEXT STATE COMPUTATION
#--------------------------------------------------------------------------
def nextState(fen, move):
    bm = fenToBoardMap(fen)
    nextStateInternal(bm, move)
    return boardMapToFen(bm)

def nextStateInternal(bm, move):
    bm = bm.copy()

    m = re.match(Common.regexSan, move)
    if not m:
        raise Exception("cannot parse move: %s" % move)

    if m.group('kCastle'):
        if bm['activePlayer'] == 'w':
            if bm['e1'] != 'K' or bm['h1'] != 'R':
                raise Exception("illegal kingside castle! (square not correct)")

            if not 'K' in bm['castleAvail']:
                raise Exception("illegal kingside castle! (availability gone)")

            bm['h1'] = ' '
            bm['e1'] = ' '
            bm['g1'] = 'K'
            bm['f1'] = 'R'
       
            bm['castleAvail'] = re.sub('K', '', bm['castleAvail'])

        else:
            if bm['e8'] != 'k' or bm['h8'] != 'r':
                raise Exception("illegal kingside castle!")

            if not 'k' in bm['castleAvail']:
                raise Exception("illegal kingside castle! (availability gone)")

            bm['h8'] = ' '
            bm['e8'] = ' '
            bm['g8'] = 'k'
            bm['f8'] = 'r'
            
            bm['castleAvail'] = re.sub('k', '', bm['castleAvail'])
            

    elif m.group('qCastle'):
        if bm['activePlayer'] == 'w':
            if bm['e1'] != 'K' or bm['a1'] != 'R':
                raise Exception("illegal queenside castle!")

            if not 'Q' in bm['castleAvail']:
                raise Exception("illegal kingside castle! (availability gone)")

            bm['a1'] = ' '
            bm['e1'] = ' '
            bm['c1'] = 'K'
            bm['d1'] = 'R'
        else:
            if bm['e8'] != 'k' or bm['a8'] != 'r':
                raise Exception("illegal queenside castle!")

            if not 'q' in bm['castleAvail']:
                raise Exception("illegal kingside castle! (availability gone)")

            bm['a8'] = ' '
            bm['e8'] = ' '
            bm['c8'] = 'k'
            bm['d8'] = 'r'

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
        srcSquare = ''
        if srcHint and re.match(r'^[a-h][1-8]$', srcHint):
            # given a full hint, source square is resolved
            srcSquare = srcHint
        else:
            # where could piece have come from?
            srcSquares = []
            if action == 'x':
                if bm[dstSquare] == ' ':
                    if srcPiece != 'P' or dstSquare != bm['enPassTarget']:
                        raise Exception("capture onto empty square?")

                srcSquares = getAttackSourceSquares(bm, dstSquare, srcPiece, bm['activePlayer'])
            else:
                srcSquares = getMoveSourceSquares(bm, dstSquare, srcPiece, bm['activePlayer'])

            # filter based on the hint
            if srcHint and re.match(r'^[1-8]$', srcHint):
                # given a rank hint, consider only source squres in this rank
                srcSquares = filter(lambda x: x[1] == srcHint, srcSquares)
            elif srcHint and re.match(r'^[a-h]$', srcHint):
                # given a file hint, consider only source squares in that file
                srcSquares = filter(lambda x: x[0] == srcHint, srcSquares)
           
            # (rare) filter moves that would result in check
            if len(srcSquares) > 1:
                temp = srcSquares
                srcSquares = []

                for sqr in temp:
                    # create hypothetical board with piece removed
                    bm2 = bm.copy()

                    # with piece moved
                    if dstSquare:
                        bm2[dstSquare] = bm2[sqr]
                    bm2[sqr] = ' '

                    # if hypothetical board does not produce a king check
                    if not isInCheckInternal(bm2, bm['activePlayer']):
                        srcSquares.append(sqr)
            
            if len(srcSquares) < 1:
                raise Exception("could not find source square for move %s" % move)

            # hopefully we're left with one square by now
            if len(srcSquares) > 1:
                raise Exception(("ambiguous source square for move %s " + \
                    "(could be any of %s)") % (move, str(srcSquares)))
               
            srcSquare = srcSquares[0]
        
        # modify the state
 
        # en-passant piece removal
        if srcPiece in 'pP' and bm[dstSquare] == ' ' and dstSquare == bm['enPassTarget']:
            if dstSquare[1]=='6':
                bm[dstSquare[0]+'5'] = ' '
            elif dstSquare[1]=='3':
                bm[dstSquare[0]+'4'] = ' '
            else:
                raise Exception("destination square %s should be on rank 3 or 6" % \
                    dstSquare)

        # en-passant next state calculation
        bm['enPassTarget'] = '-'
        if srcPiece in 'pP':
            if srcSquare[0]==dstSquare[0]:
                if srcSquare[1]=='2' and dstSquare[1]=='4':
                    bm['enPassTarget'] = srcSquare[0] + '3'
                elif srcSquare[1]=='7' and dstSquare[1]=='5':
                    bm['enPassTarget'] = srcSquare[0] + '6'

        # normal movement
        bm[dstSquare] = bm[srcSquare]
        bm[srcSquare] = ' '

        # did it promote?
        if promote:
            bm[dstSquare] = Common.casePieceByPlayer(promote[1], bm['activePlayer'])

    # swap whose turn it is
    bm['activePlayer'] = {'b':'w', 'w':'b'}[bm['activePlayer']]
    
    return bm

#--------------------------------------------------------------------------
# SAN STUFF
#--------------------------------------------------------------------------
# given 'b4' and [-1,-1] (move left one, up one), return a5
def sanSquareShift(square, movement):
    x = {'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6, 'g':7, 'h':8}[square[0]]
    y = int(square[1])

    x += movement[0]
    y += movement[1]

    if x<1 or x>8 or y<1 or y>8:
        return None

    return {1:'a', 2:'b', 3:'c', 4:'d', 5:'e', 6:'f', 7:'g', 8:'h'}[x] + str(y)
   
def sanSquareShifts(square, movements):
    return map(lambda x: sanSquareShift(square, x), movements)

def sanIsSameRank(a, b):
    return a[1] == b[1]

def sanIsSameFile(a, b):
    return a[0] == b[0]

#--------------------------------------------------------------------------
# SQUARE LOGIC
#--------------------------------------------------------------------------

# given a square and piece type, return the possible source squares from
# which this piece could move from
def getMoveSourceSquares(boardMap, destSquare, pieceType, player):
    answers = []

    # these "searchLines" across the chessboard define a line of search that
    # could be blocked by interposing pieces
    searchLinesPawnB = [[[0,1],[0,2]]]
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
                    'Pb': searchLinesPawnB, 'Pw':searchLinesPawnW, \
                    'Rb': searchLinesRook, 'Rw':searchLinesRook, \
                    'Nb': searchLinesKnight, 'Nw':searchLinesKnight, \
                    'Qb': searchLinesQueen, 'Qw':searchLinesQueen, \
                    'Bb': searchLinesBishop, 'Bw':searchLinesBishop, \
                    'Kb': searchLinesKing, 'Kw':searchLinesKing }

    matchPiece = pieceType
    if player == 'w':
        matchPiece = matchPiece.upper()
    else:
        matchPiece = matchPiece.lower()

    for searchLine in pieceToSearchLines[pieceType + player]:
        for sq in filter(lambda x: x, sanSquareShifts(destSquare, searchLine)):
            #print "a sq from sanSquareShifts: " + sq + " (has square %s ==? %s)" % (boardMap[sq], matchPiece)

            # we purposely take just the first character here (workaround for, say, 'Q~')
            # (for chess there is only one character anyways)
            p = boardMap[sq][0]
            # empty square? keep along the searchLine
            if p == ' ':
                continue
            # found it?
            if p == matchPiece:
                answers.append(sq)
            # found or not, square is occupied and blocks attacking bishop
            break

    return answers

def getAttackSourceSquares(boardMap, destSquare, pieceType, player):
    l = []

    # pawn is only piece that attacks differently than it moves
    if pieceType == 'P':
        if player == 'b':
            l = sanSquareShifts(destSquare, [[-1,1], [1,1]])
        else:
            l = sanSquareShifts(destSquare, [[1,-1], [-1,-1]])
    else:
        l = getMoveSourceSquares(boardMap, destSquare, pieceType, player)

    return filter(lambda x: x, l)

def isInCheck(fenState, player):
    return isInCheckInternal(fenToBoardMap(fenState), player)

def isInCheckInternal(boardMap, player):
    coloredKing = Common.casePieceByPlayer('k', player)

    # find king square
    sqrKing = ''
    for sqr, p in boardMap.iteritems():
        if p == coloredKing:
            sqrKing = sqr
            break

    if not sqrKing:
        raise Exception("could not find the -%s- king -%s-!" % player, coloredKing)

    # get code for opponent
    opp = Common.togglePlayer(player)

    # for all types of pieces, see if there are any attacking squares:
    for piece in ['Q','K','R','B','N']:
        # found! in check!
        attackSquares = getAttackSourceSquares(boardMap, sqrKing, piece, opp)
        if attackSquares:
            #print "yes, these guys can attack king: ", attackSquares
            return True

    # none found? not in check
    return False
        
