#!/usr/bin/python
#
# use ReportLab library to generate PDF printable flash cards
#

# easy human-adjustable settings:
MARGIN_INCHES = .25
HEIGHT_HEADER_INCHES = 0
HEIGHT_FOOTER_INCHES = 0 
INTER_DIAGRAM_SPACING_INCHES = 0
TEXT_HEIGHT = 12
FONT_SIZE = 12

# python stuff
import re
import sys

# reportlab stuff
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.pdfgen import canvas

# our stuff
from CardParser import parseCards

from RlTools import RlChessDiagram, writeWithWrap

###############################################################################
# main
###############################################################################

if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise Exception("syntax: %s <inFile> <inFile> ... <inFile> <outFile>")

    inFiles = sys.argv[1:-1]
    outFile = sys.argv[-1]

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
    if not inFiles:
        raise Exception("no input files given")
    cards = parseCards(inFiles)
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
            c.setFont('FreeSans', FONT_SIZE)
            writeWithWrap(c, question, x + diagram.width - 8, y + cardHeight - 4, questionWidth, TEXT_HEIGHT) 
    
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
            c.setFont('FreeSans', FONT_SIZE)
            writeWithWrap(c, answer, x + 4, y + cardHeight - 4, cardWidth - 8, TEXT_HEIGHT) 
    
        # continue
        cards = cards[8:]
    
        if cards:
            c.showPage()
    
    
    c.save()
    
    print "wrote %s" % outFile
