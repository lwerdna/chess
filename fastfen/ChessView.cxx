#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <map>
#include <string>
#include <vector>
#include <algorithm>
using namespace std;

#include <FL/Fl.H>
#include <FL/Fl_Input.H>
#include <FL/Fl_Box.H>

#include <FL/Fl_Window.H>
#include <FL/Fl_Toggle_Button.H>
#include <FL/Fl_Menu_Button.H>
#include <FL/Fl_Box.H>
#include <FL/Fl_Input.H>

#include <FL/fl_draw.H>

extern "C" {
#include <autils/output.h>
}

#include "chessView.h"

#include "graphics.h"

#define SQUARE_DIMENSION 64

ChessView::ChessView(int x_, int y_, int w, int h, const char *label): 
    Fl_Widget(x_, y_, w, h, label)
{
	fenSet("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
}

void ChessView::setCallback(ChessView_callback cb)
{
    callback = cb;
}

void ChessView::clrCallback(void)
{
    callback = NULL;
}

/*****************************************************************************/
/* drawing helpers */
/*****************************************************************************/
void ChessView::pixCoordToRankFile(int xPix, int yPix, int& rank, int& file)
{
	int xx = xPix - x();
	int yy = yPix - y();
	rank = yy / SQUARE_DIMENSION;
	file = xx / SQUARE_DIMENSION;
}

/*****************************************************************************/
/* draw */
/*****************************************************************************/
void ChessView::draw(void)
{
	int anchorX = x();
	int anchorY = y();

	/* map piece characters to images for DARK squares */
	map<char,const char **> p2imgDark = {
		{'R',rld__}, {'r',rdd__},
		{'N',nld__}, {'n',ndd__},
		{'B',bld__}, {'b',bdd__},
		{'Q',qld__}, {'q',qdd__},
		{'K',kld__}, {'k',kdd__},
		{'P',pld__}, {'p',pdd__},
		{' ',dsq__}
	};

	/* map piece characters to images for LIGHT squares */
	map<char,const char **> p2imgLight = {
		{'R',rll__}, {'r',rdl__},
		{'N',nll__}, {'n',ndl__},
		{'B',bll__}, {'b',bdl__},
		{'Q',qll__}, {'q',qdl__},
		{'K',kll__}, {'k',kdl__},
		{'P',pll__}, {'p',pdl__},
		{' ',lsq__}
	};

	/* active map */
	map<char,const char **> lookup;

	/* draw pieces */
	for(int rank=0; rank<8; ++rank) {
		for(int file=0; file<8; ++file) {

			if(rank==file || (rank>file && !((rank-file)%2)) || (file>rank && !((file-rank)%2)))
				lookup = p2imgLight;
			else
				lookup = p2imgDark;

			const char **pixmapData = lookup[boardArray[rank][file]];
			
			fl_draw_pixmap(pixmapData, anchorX+file*SQUARE_DIMENSION, anchorY+rank*SQUARE_DIMENSION);
		}
	}
    
	/* draw selection */
	fl_draw_box(FL_BORDER_FRAME, anchorX+selFile*SQUARE_DIMENSION, 
	  anchorY+selRank*SQUARE_DIMENSION, SQUARE_DIMENSION, SQUARE_DIMENSION, 
	  fl_rgb_color(255, 0, 0));
}

void ChessView::fenGet(string &result)
{
	result = "";

	for(int rank=0; rank<8; ++rank) {
		for(int file=0; file<8; ++file) {
			//printf("boardArray[%d][%d] is %c\n", rank, file, boardArray[rank][file]);
			if(boardArray[rank][file] == ' ') {
				int start = file;
				while(file<8) {
					if(boardArray[rank][file]!=' ') break;
					file++;
				}
				char buf[4];
				sprintf(buf, "%d", file-start);
				result += buf;
				file--;
			}
			else {
				result += boardArray[rank][file];
			}
			//printf("result is now: %s\n", result.c_str());
		}

		if(rank != 7) result += '/';
	}

	/* and the remaining stuff */
	result += ' ';
	result += remainder;
}

void ChessView::fenSet(const char *fen)
{
	int rank=0, file=0;
	bool breakLoop = false;

	map<char,int> char2val = {
		{'0',0}, {'1',1}, {'2',2}, {'3',3},
		{'4',4}, {'5',5}, {'6',6}, {'7',7},
		{'8',8}, {'9',9}
	};

	/* initialize board map to blanks */
	for(int rank=0; rank<8; ++rank) {
		for(int file=0; file<8; ++file) { 
			boardArray[rank][file] = ' ';
		}
	}

	for(int i=0; i<strlen(fen) && !breakLoop; ++i) {
		int advance = 0;
		char advanceWith;
		
		switch(fen[i]) {
			case 'r': case 'n': case 'b':
			case 'q': case 'k': case 'p':
			case 'R': case 'N': case 'B':
			case 'Q': case 'K': case 'P':
				advance = 1;
				advanceWith = fen[i];
				break;
			case '0': case '1': case '2': case '3':
			case '4': case '5': case '6': case '7':
			case '8': case '9':
				advance = char2val[fen[i]];
				advanceWith = ' ';
				break;
			case '/':
				if(rank < 7) {
					rank += 1;
					file = 0;
				}
				else {
					printf("ERROR: too many rows given\n");
				}
				break;
			case ' ':
				remainder = string(fen+i+1);
				breakLoop = true;
				break;
			default:
				printf("ERROR: unrecognized character %c", fen[i]);
				while(0);	
		}

		for(int j=0; j<advance; ++j) {
			if(file<8) {
				//printf("setting (rank,file)=(%d,%d) to %c\n", rank, file, advanceWith);
				boardArray[rank][file] = advanceWith;
				file += 1;
			}
			else {
				// ERROR "too many columns given"
			}
		}
	}

//	printf("Resulting board array:\n");
//	printf("----------------------\n");
//	for(int rank=0; rank<8; ++rank) {
//		for(int file=0; file<8; ++file) { 
//			printf("%c ", boardArray[rank][file]);
//		}
//		printf("\n");
//	}
}

int ChessView::handle(int event)
{
    int i,j,rc = 0; /* 0 if not used or understood, 1 if event was used and can be deleted */

	int keyCode = Fl::event_key();

    if(event == FL_FOCUS) {
        /* To receive FL_KEYBOARD events you must also respond to the FL_FOCUS
            and FL_UNFOCUS events by returning 1. */
		printf("got focus!\n");
		rc = 1;
	}
	else
	if(event == FL_UNFOCUS) {
        printf("I'm UNfocused!\n");
        rc = 0;
    }
    else
    if(event == FL_KEYDOWN) {
		printf("keydown!\n");
        switch(keyCode) {
            case FL_Up:
				if(selRank>0) selRank--; rc=1; break;
            case FL_Left:
				if(selFile>0) selFile--; rc=1; break;
            case FL_Right:
				if(selFile<7) selFile++; rc=1; break;
            case FL_Down:
				if(selRank<7) selRank++; rc=1; break;
			case FL_Escape:
				for(i=0; i<8; ++i)
					for(j=0; j<8; ++j)
						boardArray[i][j] = ' ';
				rc = 1;
				break;
			default:
				if(Fl::event_length()==1) {
					const char *text = Fl::event_text();
					switch(text[0]) {
						case 'r': case 'n': case 'b':
						case 'q': case 'k': case 'p':
						case 'R': case 'N': case 'B':
						case 'Q': case 'K': case 'P':
						case ' ':
							boardArray[selRank][selFile] = text[0];
							rc = 1;
					}
				}
        }
		/* new selection? new piece? redraw */
		if(rc) {
			redraw();
			callback();
		}
    }
    else
	if(event == FL_RELEASE || event == FL_RELEASE) {
		int mouseX = Fl::event_x() - x();
		int mouseY = Fl::event_y() - y();
		ChessView::pixCoordToRankFile(mouseX, mouseY, selRank, selFile);
		//printf("translated click (%d,%d) to (rank,file)=(%d,%d)\n",
		//	mouseX, mouseY, selRank, selFile);
		// with possible selection change, redraw()
		redraw();
		callback();
	}
    return rc;
}



