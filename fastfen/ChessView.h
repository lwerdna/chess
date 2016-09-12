#pragma once

#include <string>
#include <vector>
using namespace std;

#include <FL/Fl_Widget.H>

typedef void (*ChessView_callback)(void);

class ChessView : public Fl_Widget {
	bool shiftHeld = false;
	int selRank=0, selFile=0;
	string remainder; // second half of fen (after piece info)

    public:
    ChessView(int X, int Y, int W, int H, const char *label=0);
  
    void setCallback(ChessView_callback cb);
    void clrCallback(void);

	/* fen stuff */
	char boardArray[8][8];
	void fenSet(const char *fen);
	void fenGet(string& fen);

	/* draw helpers, function */
	void pixCoordToRankFile(int xPix, int yPix, int& rank, int& file);
	void draw(void);

	/* event handler */
	int handle(int event);

    /* callback */
    ChessView_callback callback=NULL;
};
