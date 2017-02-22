#!/usr/bin/python

# easy human-adjustable settings:
MARGIN_INCHES = .25
HEIGHT_HEADER_INCHES = 0
HEIGHT_FOOTER_INCHES = 0 
INTER_DIAGRAM_SPACING_INCHES = .25
LAYOUT = '2x3'
DEBUG_LINES = False

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
#print repr(c.getAvailableFonts())
#['Courier', 'Courier-Bold', 'Courier-BoldOblique', 'Courier-Oblique', \
# 'Helvetica', 'Helvetica-Bold', 'Helvetica-BoldOblique', 'Helvetica-Oblique', \
# 'Symbol', 'Times-Bold', 'Times-BoldItalic', 'Times-Italic', 'Times-Roman', ' \
# ZapfDingbats']

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
inputFname = sys.argv[1]
print "path to pgn: %s" % inputFname

# collect positions from pgn
#

# quiz is list of (FEN, description) tuples
quizes=[]

# treat it like a pgn?
if re.match(r'^.*\.pgn$', inputFname):
	fpPgn = open(inputFname)
	while 1:
		game = chess.pgn.read_game(fpPgn)
		if not game: break
		if not 'FEN' in game.headers:
			print game
			raise Exception('missing FEN before file offset %d' % fpPgn.tell())

		description = 'quiz %d' % (len(quizes)+1)
		if 'Description' in game.headers:
			description = game.headers['Description']
			
		quizes.append( (game.headers['FEN'], description) )
	fpPgn.close()
# else just newlines
else:
	fp = open(inputFname)
	positions = fp.readlines()
	positions = filter(lambda x: x and not x.isspace(), positions)
	fp.close()
	for (quizNum,position) in enumerate(positions):
		quizes.append( (position, ('quiz %d'%(quizNum+1))) )

#random.shuffle(quizes)

# draw positions
#
if DEBUG_LINES:
	c.setStrokeColorRGB(0xFF,0,0)
	c.rect(margin, margin, diagAreaWidth, diagAreaHeight)

while quizes:
	for [x,y] in diagLocations:
		#c.setFillColorRGB(.3,.3,.3)
		c.setFillColorRGB(0,0,0)

		if not quizes: break
		(fen,descr) = quizes[0]
		quizes = quizes[1:]

		x += margin
		y += margin

		if DEBUG_LINES:
			print "drawing diagram at (%d, %d) in page area" % (x, y)
			c.setStrokeColorRGB(0xFF,0,0)
			c.rect(x,y,diagWidthActual, diagHeightActual)
		
		diagram.drawBoard(x, y, fen, descr)

	# new page!
	c.showPage()

c.save()
