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
char * filePath = NULL;

#define MAX_FEN_SIZE 1024
void fenFromFile(char *path, string &fen)
{
	int fileSize = 0;
	char buf[MAX_FEN_SIZE];
	FILE *fp;
	fen = "";
	int i=0;

	memset(buf, '\0', MAX_FEN_SIZE);

	fp = fopen(path, "r");
	fseek(fp, 0, SEEK_END);
	fileSize = ftell(fp);
	fseek(fp, 0, SEEK_SET);
	
	if(fileSize > MAX_FEN_SIZE) {
		gui->log->append("ERROR: too large!");
		return;
	}

	if(fread(buf, 1, fileSize, fp) != fileSize) {
		gui->log->append("ERROR: fread()\n");
		return;
	}

	// strip off left side
	while(buf[i]==' ' || buf[i]=='\t')
		i += 1;
	// strip off right side
	while(buf[strlen(buf)-1]==' ' || buf[strlen(buf)-1]=='\t')
		buf[strlen(buf)-1] = '\0';
	
	// done
	fen = string(buf+i);

	cleanup:
	if(fp) {
		fclose(fp);
		fp = NULL;
	}
	return;
}

/*****************************************************************************/
/* chessView CALLBACK */
/*****************************************************************************/

void chessView_cb(void)
{
	// something happened, refresh the junk!
	string fen;
	gui->chessView->fenGet(fen);
	gui->outFenCurrent->value(fen.c_str());	

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
	
	string fen;

    /* if command line parameter, open that */
    if(argc > 1) {
		filePath = argv[1];

		gui->log->append("loading from file: ");
		gui->log->append(argv[1]);
		gui->log->append("\n");
        fenFromFile(argv[1], fen); 
		gui->chessView->fenSet(fen.c_str());
    }
	else {
		gui->log->append("no file given, loading default fen");
		gui->chessView->fenGet(fen);
	}

	gui->outFenInitial->value(fen.c_str());	
	gui->outFenCurrent->value(fen.c_str());	

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
	FILE *fp;
	string fen;
    printf("onExit()\n");

	if(!filePath) goto cleanup;

	printf("writing back to: %s\n", filePath);
	fp = fopen(filePath, "w");
	if(!fp) goto cleanup;

	gui->chessView->fenGet(fen);
	printf("got final fen: %s\n", fen.c_str());
	fprintf(fp, "%s", fen.c_str());
	fclose(fp);

	cleanup:
	return;
}
