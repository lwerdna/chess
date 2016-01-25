#!/usr/bin/python

# easy human-adjustable settings:
MARGIN_INCHES = .25
HEIGHT_HEADER_INCHES = 0
HEIGHT_FOOTER_INCHES = 0 
INTER_DIAGRAM_SPACING_INCHES = 0
TEXT_HEIGHT = 12
FONT_SIZE = 12

import re
import sys

from CardParser import parseCards

from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import simpleSplit

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.pdfgen import canvas

class RlChessDiagram:
    def __init__(self, canvas, maxWidth, maxHeight):
        # we draw the left border character (which includes the rank number), 
        # eight squares, and then the right border character
        self.widthInChessChars = 1+8+1

        # we drop the top border character, the 8 squares in a file,
        # and the bottom border character (which includes the file name)
        self.heightInChessChars = 1+8+1

        self.maxWidth = maxWidth
        self.maxHeight = maxHeight
        self.canvas = canvas

        self.fontSize = 1 
        testSize = 2
        while 1:
            canvas.setFont('Alpha2', testSize)

            if self.widthInChessChars * canvas.stringWidth(' ') > maxWidth:
                break
            if testSize * self.heightInChessChars > maxHeight:
                break

            self.fontSize = testSize
            #print "new font size is: %d" % self.fontSize
            testSize += 1

        # calculate max font size
        canvas.setFont('Alpha2', self.fontSize)
        self.width = canvas.stringWidth("'") * self.widthInChessChars
        self.height = self.fontSize * self.heightInChessChars

    # input:
    #   piece is a character representing the piece [pbnrqkPBNRQK]
    #   square is a character representing the square [ld]
    # output:
    #   the character in the alpha font
    def pieceToChar(self, piece, square):
        rv = None

        # blank squares (no piece)
        if not piece:
            rv = {'l':"'", 'd':'#'}[square]
        else: 
            # do normal map b,n,r,q,k,p
            lookupL = [u'\u00e0', u'\u00c0', u'\u00e2', u'\u00c2', u'\u00e4', u'\u00c4', u'\u00e6', u'\u00c6', u'\u00e8', u'\u00c8', u'\u00ea', u'\u00ca']
            lookupD = [u'\u00e1', u'\u00c1', u'\u00e3', u'\u00c3', u'\u00e5', u'\u00c5', u'\u00e7', u'\u00c7', u'\u00e9', u'\u00c9', u'\u00eb', u'\u00cb']
            pieceToIdx = {'b':0, 'B':1, 'n':2, 'N':3, 'r':4, 'R':5, 'q':6, 'Q':7, 'k':8, 'K':9, 'p':10, 'P':11}

            if square == 'l':
                rv = lookupL[pieceToIdx[piece]]
            else:
                rv = lookupD[pieceToIdx[piece]]

        #
        #print "given piece=%s square=%s returning %s" % (piece, square, repr(rv))
        return rv
    
    # input:
    #   file_: character representing file [abcdefgh]
    #   rank: integer file [12345678]
    # output:
    #   character representing square's color [ld]
    def squareColor(self, file_, rank):
        fileInt = {'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6, 'g':7, 'h':8}[file_]
    
        diff = abs(fileInt - rank)
    
        if diff % 2:
            return 'l'
        else:
            return 'd'
    
    # input:
    #   coordinates of board (of bottom left corner)
    #   fen string
    # notes:
    #   assumes that "Alpha2" is registered font 
    def drawBoard(self, xInit, yInit, fen):
        [places, activePlayer, castleAvail, enPassTarget, \
            halfMoveClock, fullMoveNum] = re.split(' ', fen)
    
        self.canvas.setFont('Alpha2', self.fontSize)
        charWidth = self.canvas.stringWidth('\'')
        charHeight = self.fontSize
    
        rank = 8
        file_ = 'a'

        # start a little higher, since we draw top-down for ease with order of fen encoding
        x = xInit
        y = yInit + self.heightInChessChars * self.fontSize
    
        # print top board border
        #print "drew top border at: (%d, %d)" % (x, y)
        self.canvas.drawString(x, y, u'\u00f9\u00fa\u00fa\u00fa\u00fa\u00fa\u00fa\u00fa\u00fa\u00fb')
        y -= charHeight

        # print left boarder
        rankToChar = [u'\u00d1', u'\u00d2', u'\u00d3', u'\u00d4', u'\u00d5', u'\u00d6', u'\u00d7', u'\u00d8']
        self.canvas.drawString(x, y, rankToChar[rank-1])
        x += charWidth
    
        for c in places:
            # map normal pieces
            if c in 'PRQKNBprqknb':
                self.canvas.drawString(x, y, \
                    self.pieceToChar(c, self.squareColor(file_, rank)))
                x += charWidth
                file_ = {'a':'b', 'b':'c', 'c':'d', 'd':'e', 'e':'f', 'f':'g', 'g':'h', 'h':'a'}[file_]
            # map blank squares
            elif c in '12345678':
                for j in range(int(c)):
                    self.canvas.drawString(x, y, \
                        self.pieceToChar(None, self.squareColor(file_, rank)))
                    x += charWidth
                    file_ = {'a':'b', 'b':'c', 'c':'d', 'd':'e', 'e':'f', 'f':'g', 'g':'h', 'h':'a'}[file_]
            # rank separator
            elif c == '/':
                # right border character
                self.canvas.drawString(x, y, u'\u00cc')

                # next line
                x = xInit
                y -= charHeight
    
                file = 'a'
                rank -= 1
    
                # print left border
                self.canvas.drawString(x, y, rankToChar[rank-1])
                x += charWidth
                
    
        # print last right border
        self.canvas.drawString(x, y, u'\u00cc')
        x = xInit
        y -= charHeight
        # print bottom border
        #borderBot = ''.join([chr(x) for x in range(232, 240)])
        borderBot = u'\u00d9\u00f1\u00f2\u00f3\u00f4\u00f5\u00f6\u00f7\u00f8\u00db'
        self.canvas.drawString(x, y, borderBot)

    def __str__(self):
        s = 'RlChessDiagram:'

        s += '  chess character dimensions: (%d, %d)\n' % \
            (self.widthInChessChars, self.heightInChessChars)

        s += '  max dimensions given at construction: (%d, %d)\n' % \
            (self.maxWidth, self.maxHeight)

        s += '  dimensions: (%d, %d)\n' % \
            (self.width, self.height)

        s += '  font size: %d\n' % self.fontSize

        return s

# convention: x and y are top left!
def writeWithWrap(canvas, text, x, y, maxWidth):
    canvas.setFont('FreeSans', FONT_SIZE)
    
    # slice the lines
    lines = []
    end = 0

    while text:
        # travel right until width is exceeded
        i = 0
        while 1: 
            if canvas.stringWidth(text[0:i]) > maxWidth:
                break
    
            i += 1
            if i >= len(text):
                end = 1
                break
    
        # then travel left until the next space
        while not end:
            if text[i] == ' ' and canvas.stringWidth(text[0:i]) <= maxWidth:
                break
    
            i -= 1
            if i <= 0:
                raise Exception("word too long!")
    
        # then cut it
        lines.append(text[0:i])
    
        # next
        text = text[i+1:]

    # now go backwards, printing the lines bottom up
    y -= TEXT_HEIGHT

    for line in lines:
        #print "putting line \"%s\" at (%d,%d)" % (line, x, y)
        canvas.drawString(x, y, line) 
        y -= TEXT_HEIGHT

###############################################################################
# main
###############################################################################

outFile = 'cards.pdf'

#
# setup, measurements
#
pdfmetrics.registerFont(TTFont('Alpha2', './resources/ChessAlpha2.ttf'))
pdfmetrics.registerFont(TTFont('FreeSans', './resources/FreeSans.ttf'))

c = canvas.Canvas(outFile, pagesize=letter)

unitsPerInch = inch
inchesPerUnit = 1.0 / unitsPerInch

pageWidth = 8.5 * unitsPerInch # 612 in testing
pageHeight = 11.0 * unitsPerInch # 792 in testing

margin = MARGIN_INCHES * unitsPerInch

printAreaWidth = pageWidth - 2*margin
printAreaHeight = pageHeight - 2*margin
#c.rect(margin + 0, margin + 0, printAreaWidth, printAreaHeight)

cardWidth = printAreaWidth / 2
cardHeight = printAreaHeight / 4

#
# calculate the position of the cards
#
cardLocs = []

# arranged like this so that cards in neighboring indices are opposite each other
# (left-to-right) on the page
for y in range(4):
    for x in range(2):
        cX = margin + cardWidth * x
        cY = margin + cardHeight * y

        cardLocs.append([cX, cY]);

#
# parse the cards, round up till 8
#
fNames = sys.argv[1:]
if not fNames:
    raise Exception("no input files given")
cards = parseCards(fNames)
if not cards:
    raise Exception("no cards parsed")
while len(cards) % 8:
    cards.append(None)

#
# draw the cards
#
diagram = RlChessDiagram(c, cardWidth, cardHeight)
questionWidth = cardWidth - diagram.width

while cards:
    # question side
    for i in range(8): 
        if not cards[i]:
            continue
       
        (fen, question, answer) = (cards[i]['fen'], cards[i]['question'], cards[i]['answer'])
        activePlayer = re.split(' ', fen)[1]
        (x,y) = (cardLocs[i][0], cardLocs[i][1])

        # draw diagram box
        c.rect(x, y, cardWidth, cardHeight)

        # draw chessboard
        diagram.drawBoard(x, y, fen)

        # draw question
        if activePlayer == 'w':
            question += ' (white to move)'
        elif activePlayer == 'b':
            question += ' (black to move)'
        writeWithWrap(c, question, x + diagram.width - 8, y + cardHeight - 4, questionWidth) 

    # new page!
    c.showPage()

    # answer side
    for i in range(8):
        if not cards[i]:
            continue

        # locate the answer opposite (left-to-right) on the side of the paper
        j = None
        if i % 2:
            j = i-1
        else:
            j = i+1
        (x,y) = (cardLocs[j][0], cardLocs[j][1])

        c.rect(x, y, cardWidth, cardHeight)
        writeWithWrap(c, answer, x + 4, y + cardHeight - 4, cardWidth - 8) 

    # continue
    cards = cards[8:]

    if cards:
        c.showPage()


c.save()

print "wrote %s" % outFile
