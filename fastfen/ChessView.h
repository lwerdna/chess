#pragma once

#include <map>
#include <string>
#include <vector>
using namespace std;

#include <FL/Fl_Widget.H>

typedef void (*ChessView_callback)(int type, void *data);

class ChessView : public Fl_Widget {
    public:
    ChessView(int X, int Y, int W, int H, const char *label=0);
  
    void setCallback(ChessView_callback cb);
    void clrCallback(void);

	/* draw function */
	void draw(void);

	/* event handler */
	int handle(int event);

    /* callback */
    ChessView_callback callback=NULL;
};
