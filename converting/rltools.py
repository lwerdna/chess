#!/usr/bin/python

# ReportLab tools

import re

from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import simpleSplit

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.pdfgen import canvas

class RlChessDiagram:
	def __init__(self, canvas, maxWidth, maxHeight):
		self.topBorderStr = u'\u00f9\u00fa\u00fa\u00fa\u00fa\u00fa\u00fa\u00fa\u00fa\u00fb'

		# we draw the left border character (which includes the rank number), 
		# eight squares, and then the right border character
		self.widthInChessChars = 1+8+1

		# we draw the top border character, the 8 squares in a file,
		# and the bottom border character (which includes the file name)
		self.heightInChessChars = 1+8+1

		self.maxWidth = maxWidth
		self.maxHeight = maxHeight
		self.canvas = canvas

		# increase the font size until we surpass the limits, then decrement back
		self.fontSymSize = 1 
		while 1:
			canvas.setFont('ChessAlpha2', self.fontSymSize)
			candidateWidth = canvas.stringWidth(self.topBorderStr)

			if candidateWidth > maxWidth:
				break
			if self.fontSymSize * self.heightInChessChars > maxHeight:
				break
			self.fontSymSize += 1
		self.fontSymSize -= 1

		self.fontTextSize = self.fontSymSize - 8

		# final calculations
		canvas.setFont('ChessAlpha2', self.fontSymSize)
		self.width = self.height = canvas.stringWidth(self.topBorderStr)

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
	def drawBoard(self, xInit, yInit, fen, title):
		print "drawing fen: %s (title: %s)" % (fen, title)
		[places, activePlayer, castleAvail, enPassTarget, \
			halfMoveClock, fullMoveNum] = re.split(' ', fen)
	
		rank = 8
		file_ = 'a'

		# start a little higher, since we draw top-down for ease with order of fen encoding
		x = xInit
		y = yInit + self.heightInChessChars * self.fontSymSize

		# print title
		self.canvas.setFont('Helvetica', self.fontTextSize)
		self.canvas.drawString(x, y+2, title)
		
		# print top board border
		self.canvas.setFont('ChessAlpha2', self.fontSymSize)
		charWidth = self.canvas.stringWidth('\'')
		charHeight = self.fontSymSize
	
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

		# print whose turn to move
		self.canvas.setStrokeColorRGB(0,0,0)
		charWidth = self.width / self.widthInChessChars
		fill_ = {'b':1,'w':0}[activePlayer]
		self.canvas.circle(xInit+charWidth/2, yInit+1.3*charWidth, charWidth/4, fill=fill_)


	def __str__(self):
		s = 'RlChessDiagram:'

		s += '  chess character dimensions: (%d, %d)\n' % \
			(self.widthInChessChars, self.heightInChessChars)

		s += '  max dimensions given at construction: (%d, %d)\n' % \
			(self.maxWidth, self.maxHeight)

		s += '  dimensions: (%d, %d)\n' % \
			(self.width, self.height)

		s += '  font size: %d\n' % self.fontSymSize

		return s

# convention: x and y are top left!
def writeWithWrap(canvas, text, x, y, maxWidth, textHeight):
	
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
	y -= textHeight

	for line in lines:
		#print "putting line \"%s\" at (%d,%d)" % (line, x, y)
		canvas.drawString(x, y, line) 
		y -= textHeight

# Calculate locations and sizes of diagrams per page.
#
# given:
#   - canvas (where font will be drawn/measured)
#   - total area for diagrams
#   - desired spacing between diagrams
#   - arrangement on the page, eg 2x3, etc.
# return:
#   - diagram width/height
#   - locations of diagrams
#
def getDiagLayout(canvas, areaWidth, areaHeight, diagSpacing, arrangement):
	diagWidthMax = None
	diagHeightMax = None
	diagLocations = []

	if arrangement == '1x1':
		# +-+
		# | |
		# +-+

		# width is page width
		diagWidthMax = areaWidth
		diagHeightMax = areaHeight
		diagram = RlChessDiagram(canvas, diagWidthMax, diagHeightMax)
	
		# center the diagram in the diagArea
		x = (areaWidth - diagram.width)/2
		y = (areaHeight - diagram.height)/2
	
		diagLocations.append([x,y])
	
	elif arrangement == '1x2':
		# +-+
		# | |
		# +-+
		#
		# +-+
		# | |
		# +-+

		# width is page width
		diagWidthMax = areaWidth
		diagHeightMax = (areaHeight - diagSpacing)/2
		diagram = RlChessDiagram(canvas, diagWidthMax, diagHeightMax)
		[diagWidthActual,diagHeightActual] = [diagram.width,diagram.height]	  
 
		# deltaX = (areaWidth - diagram.width)/2 # to center it
		deltaX = (areaWidth - diagram.height)/2
		deltaY = (areaHeight - 2*diagram.height)/3
	
		x = deltaX 
		y = deltaY
	
		diagLocations.append([x,y])
		diagLocations.append([x,y + diagram.height + deltaY])
	
	elif arrangement == '2x2':
		# +-+ +-+
		# | | | |
		# +-+ +-+
		#
		# +-+ +-+
		# | | | |
		# +-+ +-+

		# width is page width minus inter diagram spacing
		diagWidthMax = (areaWidth - diagSpacing) / 2
		diagHeightMax = (areaHeight - diagSpacing) / 2
		diagram = RlChessDiagram(canvas, diagWidthMax, diagHeightMax)
		[diagWidthActual,diagHeightActual] = [diagram.width,diagram.height]	  
	
		deltaX = (areaWidth - 2*diagram.width)/3
		deltaY = (areaHeight - 2*diagram.height)/3
	
		x = deltaX
		y = deltaY 
	
		diagLocations.append([x,y])
		diagLocations.append([x + diagram.width + deltaX, y])
		diagLocations.append([x, y + diagram.height + deltaY])
		diagLocations.append([x + diagram.width + deltaX, y + diagram.height + deltaY])
	  
	elif arrangement == '2x3':
		# +-+ +-+
		# | | | |
		# +-+ +-+
		#
		# +-+ +-+
		# | | | |
		# +-+ +-+
		#
		# +-+ +-+
		# | | | |
		# +-+ +-+

		# width is page width minus inter diagram spacing
		diagWidthMax = (areaWidth - diagSpacing) / 2
		diagHeightMax = (areaHeight - 2*diagSpacing) / 3
		diagram = RlChessDiagram(canvas, diagWidthMax, diagHeightMax)
		[diagWidthActual,diagHeightActual] = [diagram.width,diagram.height]	  
	
		deltaX = (areaWidth - 2*diagram.width)/3
		deltaY = (areaHeight - 3*diagram.height)/4
	
		x = deltaX
		y = deltaY 

		diagLocations.append([x + 0*diagram.width + 0*deltaX, y + 2*diagram.height + 2*deltaY])
		diagLocations.append([x + 1*diagram.width + 1*deltaX, y + 2*diagram.height + 2*deltaY])
	
		diagLocations.append([x + 0*diagram.width + 0*deltaX, y + 1*diagram.height + 1*deltaY])
		diagLocations.append([x + 1*diagram.width + 1*deltaX, y + 1*diagram.height + 1*deltaY])
	
		diagLocations.append([x + 0*diagram.width + 0*deltaX, y + 0*diagram.height + 0*deltaY])
		diagLocations.append([x + 1*diagram.width + 1*deltaX, y + 0*diagram.height + 0*deltaY])
		
	elif arrangement == '3x3':
		# +-+ +-+ +-+
		# | | | | | |
		# +-+ +-+ +-+
		#
		# +-+ +-+ +-+
		# | | | | | |
		# +-+ +-+ +-+
		#
		# +-+ +-+ +-+
		# | | | | | |
		# +-+ +-+ +-+

		# width is page width minus inter diagram spacing
		diagWidthMax = (areaWidth - 2*diagSpacing) / 3
		diagHeightMax = (areaHeight - 2*diagSpacing) / 3
		diagram = RlChessDiagram(canvas, diagWidthMax, diagHeightMax)
		
		diagWidthActual = diagram.width
		diagHeightActual = diagram.height

		x = (areaWidth - 3*diagram.width)/4
		y = (areaHeight - 3*diagram.height)/4
		d = diagWidthActual
		
		# top row	
		diagLocations.append([x,         y])
		diagLocations.append([x+d+x,     y])
		diagLocations.append([x+d+x+d+x, y])
	
		# middle row
		diagLocations.append([x,         y+d+y])
		diagLocations.append([x+d+x,     y+d+y])
		diagLocations.append([x+d+x+d+x, y+d+y])
	
		# bottom row
		diagLocations.append([x,         y+d+y+d+y])
		diagLocations.append([x+d+x,     y+d+y+d+y])
		diagLocations.append([x+d+x+d+x, y+d+y+d+y])
	
	else:
		raise Exception("unknown arrangement: %s" % arrangement)

	return [diagWidthActual, diagHeightActual, diagLocations]

