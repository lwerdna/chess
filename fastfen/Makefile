CFLAGS = -std=c++11 -I/usr/local/lib
FLAGS_DEBUG = -g -O0
FLAGS_FLTK = $(shell fltk-config --use-images --cxxflags )
LD_FLTK = $(shell fltk-config --use-images --ldstaticflags)
LD_FLAGS = -L/usr/local/lib
LINK = $(CXX)

all: FastFen

# GUI objects
#
ChessView.o: ChessView.cxx ChessView.h
	g++ $(CFLAGS) $(FLAGS_FLTK) $(FLAGS_DEBUG) -c ChessView.cxx

FastFenGui.o: FastFenGui.cxx FastFenGui.h
	g++ $(CFLAGS) $(FLAGS_FLTK) $(FLAGS_DEBUG) -c FastFenGui.cxx

Fl_Text_Display_Log.o: Fl_Text_Display_Log.cxx Fl_Text_Display_Log.h
	g++ $(CFLAGS) $(FLAGS_FLTK) $(FLAGS_DEBUG) -c Fl_Text_Display_Log.cxx

# LOGIC objects
#
FastFenLogic.o: FastFenLogic.cxx FastFenLogic.h
	g++ $(CFLAGS) $(FLAGS_FLTK) $(FLAGS_DEBUG) -c FastFenLogic.cxx

# LINK
#
FastFen: FastFenGui.o FastFenLogic.o ChessView.o Fl_Text_Display_Log.o Makefile
	$(LINK) FastFenGui.o FastFenLogic.o ChessView.o Fl_Text_Display_Log.o -o fastfen $(LD_FLAGS) $(LD_FLTK) -lautils

# OTHER targets
#
clean: $(TARGET) $(OBJS)
	rm -f *.o 2> /dev/null
	rm -f $(TARGET) 2> /dev/null
	rm fastfen 2> /dev/null

install:
	install ./fastfen /usr/local/bin

