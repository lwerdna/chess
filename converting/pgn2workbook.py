#!/usr/bin/python

# easy human-adjustable settings:
MARGIN_INCHES = .25
HEIGHT_HEADER_INCHES = 0
HEIGHT_FOOTER_INCHES = 0 
INTER_DIAGRAM_SPACING_INCHES = 0

ARRANGEMENT = '2x1'

import re

from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.pdfgen import canvas

from RlTools import RlChessDiagram

###############################################################################
# main
###############################################################################

pdfmetrics.registerFont(TTFont('ChessAlpha2', 'Alpha.ttf'))
pdfmetrics.registerFont(TTFont('KGPrimaryPenmanshipLined', 'KGPrimaryPenmanshipLined.ttf'))
pdfmetrics.registerFont(TTFont('Heroes', 'Tiny Heroes.ttf'))
pdfmetrics.registerFont(TTFont('Comic', 'Action Comics.ttf'))

c = canvas.Canvas('workbook.pdf', pagesize=letter)

fenStart = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

unitsPerInch = inch
inchesPerUnit = 1.0 / unitsPerInch

pageWidth = 8.5 * unitsPerInch # 612 in testing
pageHeight = 11.0 * unitsPerInch # 792 in testing

margin = MARGIN_INCHES * unitsPerInch
diagSpacing = INTER_DIAGRAM_SPACING_INCHES * unitsPerInch

diagAreaWidth = pageWidth - 2*margin
diagAreaHeight = pageHeight - 2*margin - (HEIGHT_HEADER_INCHES + HEIGHT_FOOTER_INCHES) * unitsPerInch

# calculate heading to maximize page use


# based on the arrangement, calculate the maximum width, height
diagsPerPage = 0
diagLocations = []
diagMaxWidth = 0
diagMaxHeight = 0
diagram = None

if ARRANGEMENT == '1x1':
    # width is page width minus margins
    diagMaxWidth = diagAreaWidth
    diagMaxHeight = diagAreaHeight
    diagram = RlChessDiagram(c, diagMaxWidth, diagMaxHeight)

    # center the diagram in the diagArea
    x = (diagAreaWidth - diagram.width)/2
    y = (diagAreaHeight - diagram.height)/2

    diagLocations.append([x,y])

elif ARRANGEMENT == '2x1':
    # width is page width minus margins
    diagMaxWidth = diagAreaWidth
    diagMaxHeight = (diagAreaHeight - diagSpacing)/2
    diagram = RlChessDiagram(c, diagMaxWidth, diagMaxHeight)
   
    # deltaX = (diagAreaWidth - diagram.width)/2 # to center it
    deltaX = 0 
    deltaY = (diagAreaHeight - 2*diagram.height)/3

    x = deltaX 
    y = deltaY

    diagLocations.append([x,y])
    diagLocations.append([x,y + diagram.height + deltaY])

elif ARRANGEMENT == '2x2':
    # width is page width minus margins minus inter diagram spacing
    diagMaxWidth = (diagAreaWidth - diagSpacing) / 2
    diagMaxHeight = (diagAreaHeight - diagSpacing) / 2
    diagram = RlChessDiagram(c, diagMaxWidth, diagMaxHeight)

    deltaX = (diagAreaWidth - 2*diagram.width)/3
    deltaY = (diagAreaHeight - 2*diagram.height)/3

    x = deltaX
    y = deltaY 

    diagLocations.append([x,y])
    diagLocations.append([x + diagram.width + deltaX, y])
    diagLocations.append([x, y + diagram.height + deltaY])
    diagLocations.append([x + diagram.width + deltaX, y + diagram.height + deltaY])
  
elif ARRANGEMENT == '3x2':
    # width is page width minus margins minus inter diagram spacing
    diagMaxWidth = (diagAreaWidth - diagSpacing) / 2
    diagMaxHeight = (diagAreaHeight - 2*diagSpacing) / 3
    diagram = RlChessDiagram(c, diagMaxWidth, diagMaxHeight)

    deltaX = (diagAreaWidth - 2*diagram.width)/3
    deltaY = (diagAreaHeight - 3*diagram.height)/4

    x = deltaX
    y = deltaY 

    diagLocations.append([x + 0*diagram.width + 0*deltaX, y + 0*diagram.height + 0*deltaY])
    diagLocations.append([x + 1*diagram.width + 1*deltaX, y + 0*diagram.height + 0*deltaY])

    diagLocations.append([x + 0*diagram.width + 0*deltaX, y + 1*diagram.height + 1*deltaY])
    diagLocations.append([x + 1*diagram.width + 1*deltaX, y + 1*diagram.height + 1*deltaY])

    diagLocations.append([x + 0*diagram.width + 0*deltaX, y + 2*diagram.height + 2*deltaY])
    diagLocations.append([x + 1*diagram.width + 1*deltaX, y + 2*diagram.height + 2*deltaY])


elif ARRANGEMENT == '3x3':
    # width is page width minus margins minus inter diagram spacing
    diagMaxWidth = (diagAreaWidth - 2*diagSpacing) / 3
    diagMaxHeight = (diagAreaHeight - 2*diagSpacing) / 3
    diagram = RlChessDiagram(c, diagMaxWidth, diagMaxHeight)

    deltaX = (diagAreaWidth - 3*diagram.width)/4
    deltaY = (diagAreaHeight - 3*diagram.height)/4

    x = deltaX
    y = deltaY 

    diagLocations.append([x + 0*diagram.width + 0*deltaX, y + 0*diagram.height + 0*deltaY])
    diagLocations.append([x + 1*diagram.width + 1*deltaX, y + 0*diagram.height + 0*deltaY])
    diagLocations.append([x + 2*diagram.width + 2*deltaX, y + 0*diagram.height + 0*deltaY])

    diagLocations.append([x + 0*diagram.width + 0*deltaX, y + 1*diagram.height + 1*deltaY])
    diagLocations.append([x + 1*diagram.width + 1*deltaX, y + 1*diagram.height + 1*deltaY])
    diagLocations.append([x + 2*diagram.width + 2*deltaX, y + 1*diagram.height + 1*deltaY])

    diagLocations.append([x + 0*diagram.width + 0*deltaX, y + 2*diagram.height + 2*deltaY])
    diagLocations.append([x + 1*diagram.width + 1*deltaX, y + 2*diagram.height + 2*deltaY])
    diagLocations.append([x + 2*diagram.width + 2*deltaX, y + 2*diagram.height + 2*deltaY])

import random

HERO_SIZE = 64
DESCRIPTION_SIZE = 16
TOMOVE_SIZE = 8
ANSWER_SIZE = 100

fp = open("puzzles.csv", 'r')
lines = fp.readlines()
fp.close()

# get descriptions (eg: 600 -> "mate in 1")
descr_i = []
descr_text = []
for (line_num, line) in enumerate(lines):
    m = re.match(r'INSERT INTO contents VALUES\(\d+,(\d+),\'(.*?)\'\);', line)
    if m:
        descr_i.append(int(m.group(1)))
        descr_text.append(m.group(2))
       
for i in range(len(descr_i)):
    print "games [%d, ?] are: %s" % (descr_i[i], descr_text[i])

# get FENS:
fenBuffer = []
descrBuffer = []

game_num = 0

    inFiles = sys.argv[1:-1]
    outFile = sys.argv[-1]
    if not inFiles:
        raise Exception("no input files given")
    cards = parseCards(inFiles)
    if not cards:
        raise Exception("no cards parsed")
    while len(cards) % 8:
        cards.append(None)

for card in cards:
    fenBuffer += card['fen']
    descr += '

    # do we have two diagrams yet to draw?
    if len(fenBuffer) == 2:
        #c.setFillColorRGB(.3,.3,.3)
        c.setFillColorRGB(0,0,0)
        # for each of the two diagrams...
        for i in range(2):
            fen = fenBuffer[i]
            descr = descrBuffer[i]

            x, y = (diagLocations[i][0], diagLocations[i][1])
            print "drawing diagram at (%d, %d) in diagram area" % (x, y)
        
            x += margin
            y += margin + HEIGHT_FOOTER_INCHES * unitsPerInch - 20
        
            print "drawing diagram at (%d, %d) in page area" % (x, y)
            diagram.drawBoard(x, y, fen)
        
            # locate top right of diagram and draw hero 
            x += diagram.width - 16
            y += diagram.height - HERO_SIZE - 16
            heroChar = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[random.randint(0,25)]
            c.setFont('Heroes', HERO_SIZE)
            c.drawString(x, y, heroChar)
        
            # locate below hero and draw problem description
            descrLookup = { \
                'Mate in 1': 'MATE-IN-1', \
                'Gain a rook': 'WIN A ROOK', \
                'Gain a knight': 'WIN A KNIGHT', \
                'Gain a bishop': 'WIN A BISHOP', \
                'Gain a queen': 'WIN A QUEEN', \
                'Draw': 'DRAW', \
                'Mate in 2 by means of a double check': 'MATE-IN-2'
            }
            problemDescription = descrLookup[descr]
            y -= DESCRIPTION_SIZE + 48
            c.setFont('Comic', DESCRIPTION_SIZE)
            c.drawString(x, y, problemDescription)
        
            # locate below and draw whose turn it is
            toks = fen.split() 
            if len(toks) != 6 or toks[1] not in 'bw':
                raise Exception("couldn't locate player to move in FEN: %s" % fen)
            playerToMoveLookup = { \
                'b': 'BLACK TO MOVE',
                'w': 'WHITE TO MOVE'
            }
            playerToMove = playerToMoveLookup[toks[1]] 
            y -= 32
            c.setFont('Comic', TOMOVE_SIZE)
            c.drawString(x, y, playerToMove)
        
            # locate below
            y -= ANSWER_SIZE + 8
            c.setFont('KGPrimaryPenmanshipLined', ANSWER_SIZE)
            c.drawString(x, y, '       ')

        # clear diagram buffer
        fenBuffer = []
        descrBuffer = []
    
        # new page!
        c.showPage()


c.save()
