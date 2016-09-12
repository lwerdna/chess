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

ChessView::ChessView(int x_, int y_, int w, int h, const char *label): 
    Fl_Widget(x_, y_, w, h, label)
{
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


/*****************************************************************************/
/* draw */
/*****************************************************************************/
void ChessView::draw(void)
{
    fl_draw_box(FL_FLAT_BOX, x(), y(), w(), h(), fl_rgb_color(255, 0, 0));
	fl_draw_pixmap(bdd__, 0, 0);
}

int ChessView::handle(int event)
{
    int x, y;
    int rc = 0; /* 0 if not used or understood, 1 if event was used and can be deleted */

	int keyCode = Fl::event_key();

    if(event == FL_FOCUS || event == FL_UNFOCUS) {
        /* To receive FL_KEYBOARD events you must also respond to the FL_FOCUS
            and FL_UNFOCUS events by returning 1. */
        //printf("I'm focused!\n");
        rc = 1;
    }
    else
    if(event == FL_KEYDOWN) {

        switch(keyCode) {
            case FL_Shift_L:
            case FL_Shift_R:
                redraw();
                break;

        }
    }
    else
    if(event == FL_KEYUP) {
        int keyCode = Fl::event_key();

        switch(keyCode) {
            case FL_Shift_L:
            case FL_Shift_R:
                break;
        }
    }

    return rc;
}



