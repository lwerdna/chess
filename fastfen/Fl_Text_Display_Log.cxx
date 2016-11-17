/* Fl_Text_Display with line oriented output and simple color control */

#include <FL/Fl.H>
#include <FL/x.H> // for fl_open_callback
#include <FL/Fl_Group.H>
#include <FL/Fl_Double_Window.H>
#include <FL/fl_ask.H>
#include <FL/Fl_Native_File_Chooser.H>
#include <FL/Fl_Menu_Bar.H>
#include <FL/Fl_Input.H>
#include <FL/Fl_Button.H>
#include <FL/Fl_Return_Button.H>
#include <FL/Fl_Text_Buffer.H>
#include <FL/Fl_Text_Display.H>
#include <FL/filename.H>

#include "Fl_Text_Display_Log.h"

/*****************************************************************************/
/* syntax stuff (can exist outside the class, takes only char *'s) */
/*****************************************************************************/
#define TS 14 // default editor textsize

static
Fl_Text_Display::Style_Table_Entry
zzz[] = {    // Style table
    { FL_WHITE,      FL_COURIER, TS }, // A
    { FL_BLACK,      FL_COURIER, TS }, // B
    { FL_RED, FL_COURIER, TS }, // C
    { FL_GREEN, FL_COURIER, TS }, // D 
    { FL_YELLOW,       FL_COURIER, TS }, // E
    { FL_BLUE,   FL_COURIER, TS }, // F
    { FL_MAGENTA,   FL_COURIER, TS }, // G
    { FL_CYAN,       FL_COURIER, TS }, // H
};

/*****************************************************************************/
/* class stuff */
/*****************************************************************************/

Fl_Text_Display_Log::Fl_Text_Display_Log(int x, int y, int w, int h):
  Fl_Text_Display(x, y, w, h) {

    m_styleBuf = new Fl_Text_Buffer();
    m_textBuf = new Fl_Text_Buffer();

    m_curStyleIdx = 'A';

    color(fl_rgb_color(0,0,0));

    Fl_Text_Display::buffer(m_textBuf);
    Fl_Text_Display::highlight_data(m_styleBuf, zzz, 3, 'Z', NULL, NULL);
}

void Fl_Text_Display_Log::setColor(int color)
{
    switch(color) {
        case FL_WHITE: m_curStyleIdx = 'A'; break;
        case FL_BLACK: m_curStyleIdx = 'B'; break;
        case FL_RED: m_curStyleIdx = 'C'; break;
        case FL_GREEN: m_curStyleIdx = 'D'; break;
        case FL_YELLOW: m_curStyleIdx = 'E'; break;
        case FL_BLUE: m_curStyleIdx = 'F'; break;
        case FL_MAGENTA: m_curStyleIdx = 'G'; break;
        case FL_CYAN: m_curStyleIdx = 'H'; break;
        default: printf("ERROR: unknown color: %d\n", color);
    }
}

void Fl_Text_Display_Log::clear()
{
    m_textBuf->text(""); 
    m_styleBuf->text(""); 
}

void Fl_Text_Display_Log::append(const char *line)
{
    int n = strlen(line);
    char *styleString = (char *)malloc(n + 1);
    if(!styleString) {
        printf("ERROR: malloc()\n");
        goto cleanup;
    }
    memset(styleString, m_curStyleIdx, n);
    styleString[n] = '\0';

    //printf("appending string: -%s-\n", line);
    //printf(" appending style: -%s-\n", styleString);

    m_textBuf->append(line);
    m_styleBuf->append(styleString);

    //printf("NEW STRING: %s\n", m_textBuf->text());
    //printf(" NEW STYLE: %s\n", m_styleBuf->text());

    cleanup:
    free(styleString);
    styleString = NULL;
    return;
}

