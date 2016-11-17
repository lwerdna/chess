#!/usr/bin/env python

import sys

import chess
import chess.pgn
import chess.uci

assert(sys.argv[1:])
pgn = open(sys.argv[1])

engine = chess.uci.popen_engine("stockfish")
engine.uci()

gameNum=1
while 1:
	game = chess.pgn.read_game(pgn)
	if not game: break

	node = game
	while not node.is_end():
		print "after move: %s" % node.move
		print node.board()

		engine.position(node.board())
		(moveBest, movePonder) = engine.go(movetime=3000, ponder=False)
		print moveBest
		print dir(moveBest)

		node = node.variation(0)

	gameNum += 1
	break
