#pragma once

#include <FL/Fl_Text_Editor.H>

class Fl_Text_Display_Log : public Fl_Text_Display {
    private:
        Fl_Text_Buffer *m_textBuf;
        Fl_Text_Buffer *m_styleBuf;

        char m_curStyleIdx;

    public:
        Fl_Text_Display_Log(int x, int y, int w, int h);

        void setColor(int);
        void clear(void);
        void append(const char *);

};

