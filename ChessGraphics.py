#!/usr/bin/python

import os
import sys
import time

import ChessState

from PIL import Image, ImageDraw, ImageFont

fontPath = '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans-Bold.ttf'

MARGIN_COLOR = 0x404040
DARK_SQUARE_COLOR = '#88debb'
LIGHT_SQUARE_COLOR = '#feffed'

PIECE_PX = 64
MARGIN_X = 32
MARGIN_Y = 32
WIDTH_PX = MARGIN_X + 8*PIECE_PX + MARGIN_X
HEIGHT_PX = MARGIN_Y + 8*PIECE_PX + MARGIN_Y

def drawBoard(fen, size, outPath, perspective=None):
    myFont = ImageFont.truetype(fontPath, 25)
    charWidth = 8
    charHeight = 14
    
    # chess state
    chessState = ChessState.ChessState(fen)

    # piece image lookup
    pieceToImg = {}
    scriptDir = os.path.dirname(__file__)
    pieceToImg['p'] = Image.open(scriptDir + '/images/p.png')
    pieceToImg['b'] = Image.open(scriptDir + '/images/b.png')
    pieceToImg['n'] = Image.open(scriptDir + '/images/n.png')
    pieceToImg['r'] = Image.open(scriptDir + '/images/r.png')
    pieceToImg['q'] = Image.open(scriptDir + '/images/q.png')
    pieceToImg['k'] = Image.open(scriptDir + '/images/k.png')
    pieceToImg['P'] = Image.open(scriptDir + '/images/P.png')
    pieceToImg['B'] = Image.open(scriptDir + '/images/B.png')
    pieceToImg['N'] = Image.open(scriptDir + '/images/N.png')
    pieceToImg['R'] = Image.open(scriptDir + '/images/R.png')
    pieceToImg['Q'] = Image.open(scriptDir + '/images/Q.png')
    pieceToImg['K'] = Image.open(scriptDir + '/images/K.png')

    im = Image.new('RGB', (WIDTH_PX, HEIGHT_PX), (255, 255, 255, 0))

    # ImageDraw wraps an image, provides drawing functions
    id = ImageDraw.Draw(im)

    # draw the border/margin
    id.rectangle([0, 0, WIDTH_PX, MARGIN_Y], fill=MARGIN_COLOR)
    id.rectangle([0, 0, MARGIN_X, HEIGHT_PX], fill=MARGIN_COLOR)
    id.rectangle([MARGIN_X + 8*PIECE_PX, 0, WIDTH_PX, HEIGHT_PX], fill=MARGIN_COLOR)
    id.rectangle([0, HEIGHT_PX-MARGIN_Y, WIDTH_PX, HEIGHT_PX], fill=MARGIN_COLOR)

    # whose turn is it? draw from her perspective
    flip = 0
    if perspective:
        if perspective in 'wW':
            pass
        elif perspective in 'bB':
            flip = 1
    else:
        if chessState.activePlayer in 'bB':
            flip = 1

    print "is flip? %s" % flip

    if flip:
        for (i, sym) in enumerate('hgfedcba'):
            id.text([MARGIN_X + i * PIECE_PX + PIECE_PX/2 - charWidth, 0], sym, fill=0xFFFFFF, font=myFont)
    else:
        for (i, sym) in enumerate('abcdefgh'):
            id.text([MARGIN_X + i * PIECE_PX + PIECE_PX/2 - charWidth, HEIGHT_PX - MARGIN_Y], sym, fill=0xFFFFFF, font=myFont)

    if flip:
        for (i, sym) in enumerate('12345678'):
            id.text([WIDTH_PX - MARGIN_X/2 - charWidth, MARGIN_Y + i * PIECE_PX + charHeight], sym, fill=0xFFFFFF, font=myFont)
    else:
        for (i, sym) in enumerate('87654321'):
            id.text([MARGIN_X/2 - charWidth, MARGIN_Y + i * PIECE_PX + charHeight], sym, fill=0xFFFFFF, font=myFont)

    for ridx, rname in enumerate(list('12345678')):
        for fidx, fname in enumerate(list('abcdefgh')):

            if flip:
                color = [DARK_SQUARE_COLOR, LIGHT_SQUARE_COLOR][(ridx-fidx)%2]
            else:
                color = [LIGHT_SQUARE_COLOR, DARK_SQUARE_COLOR][(ridx-fidx)%2]
    
            id.rectangle([MARGIN_X + fidx*PIECE_PX, MARGIN_X + ridx*PIECE_PX, 
                MARGIN_Y + (fidx + 1)*PIECE_PX, MARGIN_Y + (ridx + 1)*PIECE_PX],
                fill=color)

    # draw the pieces
    chessState = ChessState.ChessState(fen)

    # top left to bottom right, same as FEN recording...
    for (y, rname) in enumerate('87654321'):
        if flip:
            y = 7 - y

        for (x, fname) in enumerate('abcdefgh'):
            sname = fname + rname

            piece = chessState[sname]

            if flip:
                x = 7 - x

            if piece != ' ':
                im.paste(pieceToImg[piece], 
                    [MARGIN_X + x*PIECE_PX, MARGIN_Y + y*PIECE_PX,
                    MARGIN_X + x*PIECE_PX + 64, MARGIN_Y + y*PIECE_PX + 64], 
                    mask=pieceToImg[piece]) 


    # 
    im = im.resize(size, Image.ANTIALIAS)
    im.save(outPath)
    #im.show()

if __name__ == '__main__':
    print "hi"

    drawBoard('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', [100,100], './test.png', 'w')

