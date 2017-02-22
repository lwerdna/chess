#!/usr/bin/python

# easy human-adjustable settings:
MARGIN_INCHES = .25
HEIGHT_HEADER_INCHES = 0
HEIGHT_FOOTER_INCHES = 0 
INTER_DIAGRAM_SPACING_INCHES = 0

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
from rltools import RlChessDiagram

# python-chess
import chess
import chess.pgn

pdfmetrics.registerFont(TTFont('ChessAlpha2', 'resources/ChessAlpha2.ttf'))
pdfmetrics.registerFont(TTFont('KGPrimaryPenmanshipLined', 'resources/KGPrimaryPenmanshipLined.ttf'))
pdfmetrics.registerFont(TTFont('Heroes', 'resources/Tiny Heroes.ttf'))
pdfmetrics.registerFont(TTFont('Comic', 'resources/Action Comics.ttf'))

c = canvas.Canvas('worksheets.pdf', pagesize=letter)

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

HERO_SIZE = 64
DESCRIPTION_SIZE = 16
TOMOVE_SIZE = 8
ANSWER_SIZE = 100

assert(len(sys.argv)==2)
pathPgn = sys.argv[1]

games=[]
fpPgn = open(pathPgn)
while 1:
	game = chess.pgn.read_game(fpPgn)
	if not game: break
	games.append(game)
fpPgn.close()

i = 0
while i < len(games):
	for k in [i,i+1]:
		if k>=len(games): continue

		#c.setFillColorRGB(.3,.3,.3)
		c.setFillColorRGB(0,0,0)

		fen = games[k].headers['FEN']

		[x, y] = diagLocations[k%2]
		print "drawing diagram at (%d, %d) in diagram area" % (x, y)
	
		x += margin
		y += margin + HEIGHT_FOOTER_INCHES * unitsPerInch - 20
	
		print "drawing diagram at (%d, %d) in page area" % (x, y)
		diagram.drawBoard(x, y, fen, "")
	
		# locate top right of diagram and draw hero 
		x += diagram.width - 16
		y += diagram.height - HERO_SIZE - 16
		heroChar = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[random.randint(0,25)]
		c.setFont('Heroes', HERO_SIZE)
		c.drawString(x, y, heroChar)
	
		# locate below hero and draw problem description
		problemDescription = games[k].headers['Description'].upper()
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
		x -= 28 
		c.setFont('KGPrimaryPenmanshipLined', ANSWER_SIZE)
		c.drawString(x, y, '	       ')

	# new page!
	c.showPage()
	i = i+2
	print "on %d/%d (%f%%)" % (i,len(games),1.0*i/len(games))

c.save()
