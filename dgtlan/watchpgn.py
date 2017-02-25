#!/usr/bin/env python

# uses python-chess to animate a game with engine analysis on the canvas

import re
import pdb
import chess
import chess.uci
import chess.pgn

import time

import random
from subprocess import Popen, PIPE, STDOUT

width = 1280
height = 720


p = Popen(['acanvas'], stdin=PIPE)
p.stdin.write('resize 0 0 %d %d\n' % (width, height))

class MyInfoHandler(chess.uci.InfoHandler):
	def pre_info(self, line):
		global p

		print "line: -%s-" % line
		m = re.match(r'^depth (\d+) .* score cp (-?\d+) .* pv (.*)$', line)
		if m:
			(depth, score, pv) = m.group(1,2,3)
			depth = int(depth)
			score = .01 * int(score)
			moves = ' '.join(pv.split(' ')[0:4])
			tmp = 'depth:%d eval:%.1f line:%s...' % (depth, score, moves)
			p.stdin.write('box 85 660 1280 60 000000\n')
			p.stdin.write('font 4 18\n')
			p.stdin.write('color 00FF00\n')
			p.stdin.write('write 85 680 %s\n' % tmp)
			p.stdin.write('write 682 680 %s\n' % tmp)

		super(MyInfoHandler, self).pre_info(line)

def getBestMove(board):
	ih = MyInfoHandler()
	eng = chess.uci.popen_engine("/usr/local/bin/stockfish")
	eng.info_handlers.append(ih)
	eng.uci()
	eng.ucinewgame()
	eng.position(board)
	eng.go(movetime=1000)
	eng.quit()


f = open('example.pgn')
gameNode = chess.pgn.read_game(f)

#
# print player labels
# 
whiteLabel = ''
if 'White' in gameNode.headers:
	whiteLabel = gameNode.headers['White']
if 'WhiteElo' in gameNode.headers:
	whiteLabel += ' (%d)' % int(gameNode.headers['WhiteElo'])

blackLabel = ''
if 'Black' in gameNode.headers:
	blackLabel = gameNode.headers['Black']
if 'BlackElo' in gameNode.headers:
	blackLabel += ' (%d)' % int(gameNode.headers['BlackElo'])

p.stdin.write('font 0 40\n')
p.stdin.write('color FFFFFF\n')
p.stdin.write('write 85 90 %s\n' % whiteLabel)
p.stdin.write('write 85 650 %s\n' % whiteLabel)

p.stdin.write('font 0 40\n')
p.stdin.write('color FFFFFF\n')
p.stdin.write('write 682 90 %s\n' % whiteLabel)
p.stdin.write('write 682 650 %s\n' % whiteLabel)

i = 0;
try:	
	while 1:
		move = ''
		# if game node has parent, what was the move that got us here?
		if gameNode.parent:
			move = gameNode.san()
	
		board = gameNode.board()
	

		#print "state %d: %s (from %s, best was %s)" % (i, board.fen(), move, moveBestSan)
		p.stdin.write('chess 85 104 %s\n' % board.fen())
		p.stdin.write('chess 682 104 %s\n' % board.fen())

		moveBestUci = getBestMove(board)
		#moveBestSan = board.san(moveBestUci)
	
		if gameNode.is_end():
			break;
	
		gameNode = gameNode.variation(0)
	
except Exception as e:
	p.kill()
	sys.exit(-1)


