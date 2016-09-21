#!/usr/bin/python

# easy human-adjustable settings:
MARGIN_INCHES = .25
HEIGHT_HEADER_INCHES = 0
HEIGHT_FOOTER_INCHES = 0 
INTER_DIAGRAM_SPACING_INCHES = .25
LAYOUT = '2x3'

import re
import sys
import random

# reportlab stuff
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.pdfgen import canvas

# reportlab helper
import rltools

# python-chess
import chess
import chess.pgn

# reportlab setup
pdfmetrics.registerFont(TTFont('ChessAlpha2', 'resources/ChessAlpha2.ttf'))

# measuring
unitsPerInch = inch
inchesPerUnit = 1.0 / unitsPerInch
pageWidth = 8.5 * unitsPerInch
pageHeight = 11.0 * unitsPerInch
print "page area (w,h)=(%d,%d) units" % (pageWidth,pageHeight)
margin = MARGIN_INCHES * unitsPerInch
diagSpacing = INTER_DIAGRAM_SPACING_INCHES * unitsPerInch
diagAreaWidth = pageWidth - 2*margin
diagAreaHeight = pageHeight - 2*margin - (HEIGHT_HEADER_INCHES + HEIGHT_FOOTER_INCHES) * unitsPerInch
print "diag area (w,h)=(%d,%d) units" % (diagAreaWidth, diagAreaHeight)

# diagram locations, numbers
c = canvas.Canvas('worksheets.pdf', pagesize=letter)

[diagWidthActual, diagHeightActual, diagLocations] = \
	rltools.getDiagLayout(c, diagAreaWidth, diagAreaHeight, diagSpacing, LAYOUT)

print "diagram layout:"
for (i,loc) in enumerate(diagLocations):
	print "diagram %d at (%d,%d)" % (i,loc[0],loc[1])
diagsPerPage = len(diagLocations)

diagram = rltools.RlChessDiagram(c, diagWidthActual, diagHeightActual)

# parse arguments
#
assert(len(sys.argv)==2)
pathPgn = sys.argv[1]

# collect games from pgn
#
games=[]
fpPgn = open(pathPgn)
while 1:
	game = chess.pgn.read_game(fpPgn)
	if not game: break
	games.append(game)
fpPgn.close()

# draw games
#
c.setStrokeColorRGB(0xFF,0,0)
c.rect(margin, margin, diagAreaWidth, diagAreaHeight)

i = 0
while games:
	for [x,y] in diagLocations:
		#c.setFillColorRGB(.3,.3,.3)
		c.setFillColorRGB(0,0,0)

		if not games: break
		game = games[0]
		games = games[1:]
		fen = game.headers['FEN']

		x += margin
		y += margin
	
		#print "drawing diagram at (%d, %d) in page area" % (x, y)
		diagram.drawBoard(x, y, fen)

		c.setStrokeColorRGB(0xFF,0,0)
		c.rect(x,y,diagWidthActual, diagHeightActual)

	# new page!
	c.showPage()

c.save()
