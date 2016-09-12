/* c stdlib includes */
#include <time.h>
#include <stdio.h>

/* c++ includes */
#include <map>
#include <string>
#include <vector>
using namespace std;

#include "FastFenGui.h"

/* fltk includes */
#include <FL/Fl.H>
#include <FL/Fl_Text_Buffer.H>
#include <FL/Fl_Text_Display.H>
#include <FL/Fl_File_Chooser.H>
#include <FL/Fl_Tree.H>
#include <FL/Fl_Tree_Item.H>

/* autils */
extern "C" {
    #include <autils/bytes.h>
}

/* forward dec's */
void tree_cb(Fl_Tree *, void *);

/* globals */
FastFenGui *gui = NULL;


/*****************************************************************************/
/* chessView CALLBACK */
/*****************************************************************************/

void chessView_cb(int type, void *data)
{

}

/*****************************************************************************/
/* GUI CALLBACK STUFF */
/*****************************************************************************/

void
onGuiFinished(FastFenGui *gui_, int argc, char **argv)
{
    printf("%s()\n", __func__);
    int rc = -1;

    gui = gui_;

    gui->chessView->setCallback(chessView_cb);

    /* if command line parameter, open that */
    if(argc > 1) {
        //file_load(argv[1]); 

        if(argc > 2) {
            //load_tags(argv[2]);
        }
    }

    rc = 0;
    //cleanup:
    return;
}

void
onIdle(void *data)
{
    
}

void
onExit(void)
{
    printf("onExit()\n");
}
