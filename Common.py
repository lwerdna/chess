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


# note that only in FEN (chess or crazy or bug) are upper/lower letters used
initChessFEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0'
initCrazyFEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR/ w KQkq - 0 0'
initBugFEN = initCrazyFEN + ' | ' + initCrazyFEN

# SAN - [s]tandard [a]lgebraic [n]otation
# notes: 
# - queen castle detection must come first (king castle is substring)
#   in actual SAN movetext, all pieces are in caps

regexSquare = r'[abcdefgh][12345678]'

regexResults = r'(0-0|0-1|1-0|1/2-1/2|\*)'

regexSanChess = \
   r'^(?:' + \
   r'(?P<qCastle>O-O-O)|' + \
   r'(?P<kCastle>O-O)|' + \
   r'(?P<srcPiece>[PNBRQK])?' + \
   r'(?P<srcHint>[a-h1-8]{1,2})?' + \
   r'(?P<action>[x])?' + \
   r'(?P<dstSquare>[a-h][1-8])' + \
   r'(?P<promote>=[PNBRQK])?' + \
   r')' + \
   r'(?P<check>[\+#])?'

regexSanCrazy = \
   r'^(?:' + \
   r'(?P<qCastle>O-O-O)|' + \
   r'(?P<kCastle>O-O)|' + \
   r'(?P<srcPiece>[PNBRQK])?' + \
   r'(?P<srcHint>[a-h1-8]{1,2})?' + \
   r'(?P<action>[x@])?' + \
   r'(?P<dstSquare>[a-h][1-8])' + \
   r'(?P<promote>=[PNBRQK])?' + \
   r')' + \
   r'(?P<check>[\+#])?'

squaresSan = [ \
        'a8','b8','c8','d8','e8','f8','g8','h8', \
        'a7','b7','c7','d7','e7','f7','g7','h7', \
        'a6','b6','c6','d6','e6','f6','g6','h6', \
        'a5','b5','c5','d5','e5','f5','g5','h5', \
        'a4','b4','c4','d4','e4','f4','g4','h4', \
        'a3','b3','c3','d3','e3','f3','g3','h3', \
        'a2','b2','c2','d2','e2','f2','g2','h2', \
        'a1','b1','c1','d1','e1','f1','g1','h1' \
]

ranksSan = [ \
        ['a8','b8','c8','d8','e8','f8','g8','h8'], \
        ['a7','b7','c7','d7','e7','f7','g7','h7'], \
        ['a6','b6','c6','d6','e6','f6','g6','h6'], \
        ['a5','b5','c5','d5','e5','f5','g5','h5'], \
        ['a4','b4','c4','d4','e4','f4','g4','h4'], \
        ['a3','b3','c3','d3','e3','f3','g3','h3'], \
        ['a2','b2','c2','d2','e2','f2','g2','h2'], \
        ['a1','b1','c1','d1','e1','f1','g1','h1'] \
]

squareToIdx = { \
        'a8':0,'b8':1,'c8':2,'d8':3,'e8':4,'f8':5,'g8':6,'h8':7, \
        'a7':8,'b7':9,'c7':10,'d7':11,'e7':12,'f7':13,'g7':14,'h7':15, \
        'a6':16,'b6':17,'c6':18,'d6':19,'e6':20,'f6':21,'g6':22,'h6':23, \
        'a5':24,'b5':25,'c5':26,'d5':27,'e5':28,'f5':29,'g5':30,'h5':31, \
        'a4':32,'b4':33,'c4':34,'d4':35,'e4':36,'f4':32,'g4':33,'h4':34, \
        'a3':40,'b3':41,'c3':42,'d3':43,'e3':44,'f3':45,'g3':46,'h3':47, \
        'a2':48,'b2':49,'c2':50,'d2':51,'e2':52,'f2':53,'g2':54,'h2':55, \
        'a1':56,'b1':57,'c1':58,'d1':59,'e1':60,'f1':61,'g1':62,'h1':63 \
    }

idxToSquare = { \
        0:'a8',1:'b8','c8':2,3:'d8',4:'e8',5:'f8',6:'g8',7:'h8', \
        8:'a7',9:'b7',10:'c7',11:'d7',12:'e7',13:'f7',14:'g7',15:'h7', \
        16:'a6',17:'b6',18:'c6',19:'d6',20:'e6',21:'f6',22:'g6',23:'h6', \
        24:'a5',25:'b5',26:'c5',27:'d5',28:'e5',29:'f5',30:'g5',31:'h5', \
        32:'a4',33:'b4',34:'c4',35:'d4',36:'e4',32:'f4',33:'g4',34:'h4', \
        40:'a3',41:'b3',42:'c3',43:'d3',44:'e3',45:'f3',46:'g3',47:'h3', \
        48:'a2',49:'b2',50:'c2',51:'d2',52:'e2',53:'f2',54:'g2',55:'h2', \
        56:'a1',57:'b1',58:'c1',59:'d1',60:'e1',61:'f1',62:'g1',63:'h1' \
    }

pieceChangeColorMap = {'p':'P', 'P':'p', \
                       'r':'R', 'R':'r', \
                       'b':'B', 'B':'b', \
                       'n':'N', 'N':'n', \
                       'q':'Q', 'Q':'q'}

def casePieceByPlayer(piece, player):
    if player == 'w':
        return piece.upper()
    elif player == 'b':
        return piece.lower()
    else:
        raise Exception("unknown player: -%s-" % player)

def toggleCase(piece):
    temp = piece.upper()

    if piece == temp:
        return piece.lower()
        
    return temp

def togglePlayer(player):
    if player == 'w':
        return 'b'
    elif player == 'b':
        return 'w'
    raise Exception('uknown player code -%s-' % player)

def coloredPieceToPlayer(piece):
    if piece == piece.upper():
        return 'w'
    else:
        return 'b'
