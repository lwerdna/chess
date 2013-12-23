#!/usr/bin/python

import tkMessageBox
import sys
import os

path_log = os.environ['HOME'] + '/chess/log.txt'

def log(msg):
    fobj = open("/home/a/chess/log.txt", "a")
    fobj.write(msg + "\n")
    fobj.close()

    #tkMessageBox.showinfo("log", msg);

fobj = open(path_log, 'w')
fobj.write('')
fobj.close()

buf = ''

for a in sys.argv:
    log("arg: %s" % a)

sys.stdout.write("Stockfish  120212 64bit by Tord Romstad, Marco Costalba and Joona Kiiski\n")
sys.stdout.flush()

while 1:
    log("attempting to read...\n")
    buf += sys.stdin.read(1)

    idx = buf.find("\n")
    if idx == -1:
        log("waiting on newline, buff: %s" % repr(buf))
        continue

    foo = buf[0:idx]
    buf = buf[idx+1:]

    log("stripped off: %s" % repr(foo))
    log("remaining buff is: %s" % repr(buf))

    if foo == "uci":
        log("got \"uci\", sending <stuff captured from stockfish>")
        sys.stdout.write("id name Stockfish  120212 64bit\n")
        sys.stdout.write("id author Tord Romstad, Marco Costalba and Joona Kiiski\n")
        sys.stdout.write("\n")
        sys.stdout.write("option name Use Search Log type check default false\n")
        sys.stdout.write("option name Search Log Filename type string default SearchLog.txt\n")
        sys.stdout.write("option name Book File type string default book.bin\n")
        sys.stdout.write("option name Best Book Move type check default false\n")
        sys.stdout.write("option name Mobility (Middle Game) type spin default 100 min 0 max 200\n")
        sys.stdout.write("option name Mobility (Endgame) type spin default 100 min 0 max 200\n")
        sys.stdout.write("option name Passed Pawns (Middle Game) type spin default 100 min 0 max 200\n")
        sys.stdout.write("option name Passed Pawns (Endgame) type spin default 100 min 0 max 200\n")
        sys.stdout.write("option name Space type spin default 100 min 0 max 200\n")
        sys.stdout.write("option name Aggressiveness type spin default 100 min 0 max 200\n")
        sys.stdout.write("option name Cowardice type spin default 100 min 0 max 200\n")
        sys.stdout.write("option name Min Split Depth type spin default 4 min 4 max 7\n")
        sys.stdout.write("option name Max Threads per Split Point type spin default 5 min 4 max 8\n")
        sys.stdout.write("option name Threads type spin default 4 min 1 max 32\n")
        sys.stdout.write("option name Use Sleeping Threads type check default true\n")
        sys.stdout.write("option name Hash type spin default 32 min 4 max 8192\n")
        sys.stdout.write("option name Clear Hash type button\n")
        sys.stdout.write("option name Ponder type check default true\n")
        sys.stdout.write("option name OwnBook type check default true\n")
        sys.stdout.write("option name MultiPV type spin default 1 min 1 max 500\n")
        sys.stdout.write("option name Skill Level type spin default 20 min 0 max 20\n")
        sys.stdout.write("option name Emergency Move Horizon type spin default 40 min 0 max 50\n")
        sys.stdout.write("option name Emergency Base Time type spin default 200 min 0 max 30000\n")
        sys.stdout.write("option name Emergency Move Time type spin default 70 min 0 max 5000\n")
        sys.stdout.write("option name Minimum Thinking Time type spin default 20 min 0 max 5000\n")
        sys.stdout.write("option name UCI_Chess960 type check default false\n")
        sys.stdout.write("option name UCI_AnalyseMode type check default false\n")
        sys.stdout.write("uciok\n")

    elif foo == "isready":
        log("got \"isready\", sending \"readyok\"")
        sys.stdout.write("readyok\n")

    elif foo == '':
        log("skipping empty line...\n")
        sys.stdout.write("readyok\n")

    elif foo == 'quit' or foo == 'exit':
        log("got %s, quitting..." % repr(foo))
        break;

    elif foo == 'stop':
        log("got %s, nop'ing..." % repr(foo))
        break;

    elif foo == 'go infinite':
        log("got %s, sending some bs..." % repr(foo))
        #sys.stdout.write("info depth 1 seldepth 1 score cp 72 nodes 28 nps 903 time 31 multipv 1 pv g1f3\n")
        #sys.stdout.write("info depth 2 seldepth 2 score cp 12 nodes 160 nps 5161 time 31 multipv 1 pv g1f3 g8f6\n")
        #sys.stdout.write("info depth 3 seldepth 3 score cp 68 nodes 293 nps 9451 time 31 multipv 1 pv g1f3 g8f6 b1c3\n")
        #sys.stdout.write("info depth 4 seldepth 4 score cp 12 nodes 573 nps 18483 time 31 multipv 1 pv g1f3 g8f6 b1c3 b8c6\n")
        #sys.stdout.write("info depth 5 seldepth 5 score cp 36 nodes 1775 nps 55468 time 32 multipv 1 pv d2d4 b8c6 d4d5 c6e5 g1f3\n")
        #sys.stdout.write("info depth 6 seldepth 7 score cp 12 nodes 3253 nps 95676 time 34 multipv 1 pv d2d4 b8c6 d4d5 c6a5 g1f3 g8f6\n")
        #sys.stdout.write("info depth 7 seldepth 8 score cp 32 nodes 5994 nps 166500 time 36 multipv 1 pv d2d4 d7d5 b1c3 g8f6 c1f4 b8c6 g1f3\n")
        #sys.stdout.write("info depth 8 seldepth 10 score cp 20 nodes 20724 nps 450521 time 46 multipv 1 pv d2d4 g8f6 g1f3 d7d5 b1c3 b8c6 d1d3 d8d6 h2h3\n")
        #sys.stdout.write("info depth 9 seldepth 11 score cp 20 nodes 26307 nps 536877 time 49 multipv 1 pv d2d4 g8f6 g1f3 d7d5 b1c3 b8c6 d1d3 d8d6 h2h3\n")
        #sys.stdout.write("info depth 10 seldepth 12 score cp 28 nodes 56521 nps 831191 time 68 multipv 1 pv g1f3 g8f6 b1c3 b8c6 e2e4 d7d5 e4d5 f6d5 d2d4 c8f5 f1d3\n")
        #sys.stdout.write("info depth 11 seldepth 17 score cp 24 nodes 177132 nps 1428483 time 124 multipv 1 pv e2e4 g8f6 b1c3 d7d5 e4d5 f6d5 g1f3 b8c6 d2d4 c8f5 f1c4 d5c3 b2c3 e7e6 c1f4\n")
        #sys.stdout.write("info depth 12 seldepth 17 score cp 28 nodes 242921 nps 1557185 time 156 multipv 1 pv e2e4 g8f6 b1c3 b8c6 d2d4 d7d5 e4d5 f6d5 g1f3 c8f5 f1c4 d5c3 b2c3 e7e6 e1g1\n")
        #sys.stdout.write("info depth 13 seldepth 18 score cp 36 nodes 317692 nps 1663308 time 191 multipv 1 pv e2e4 g8f6 b1c3 b8c6 g1f3 e7e6 f1e2 f8b4 e4e5 f6g4 e1g1 g4e5 f3e5 c6e5 d2d4\n")
        #sys.stdout.write("info depth 14 seldepth 21 score cp 36 nodes 940500 nps 2182134 time 431 multipv 1 pv e2e4 b8c6 g1f3 e7e5 f1c4 f8c5 a2a3 g8f6 b2b4 c5d6 b1c3 c6d4 e1g1 e8g8 c1b2 c7c6 f3d4 e5d4\n")
        #sys.stdout.write("info depth 1 seldepth 1 score cp 72 nodes 28 nps 903 time 31 multipv 1 pv g1f3\n")

    else:
        log("got: %s" % repr(foo))
        
    sys.stdout.flush()

