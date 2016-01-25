#!/usr/bin/python

# got: "The manual of chess combinations - Volume I" by S. Ivashenko ( CDB )
# from: these from http://pbchess.vlasovsoft.net/en/contents.html
#
# used sqlitebrowser to export a .csv file (puzzles.csv)
#
# used this to make a .pgn

fp = open("puzzles.csv", 'r')
lines = fp.readlines()
fp.close()

import re

template = ''
template += '[Event "%s"]\n'
template += '[Site "s"]\n'
template += '[Date "1-1-2000"]\n'
template += '[Round "r"]\n'
template += '[White "%s"]\n'
template += '[Black "%s"]\n'
template += '[FEN "%s"]\n'
template += '[Result "%s"]\n'
template += '\n'
template += '%s\n'
template += '\n'

game_num = 1
        
fp = open('puzzles.pgn', 'w')

# get descriptions
descr_i = []
descr_text = []
for (line_num, line) in enumerate(lines):
    m = re.match(r'INSERT INTO contents VALUES\(\d+,(\d+),\'(.*?)\'\);', line)
    if m:
        descr_i.append(int(m.group(1)))
        descr_text.append(m.group(2))
       
for i in range(len(descr_i)):
    print "games [%d, ?] are: %s" % (descr_i[i], descr_text[i])

# get PGN's
for (line_num, line) in enumerate(lines):
    m = re.match(r'INSERT INTO games VALUES\(\d,\'.*?\',\'\',\'\',\'\',\'\',\'\',\'(.*?)\',\d+,\d+,\'(.*?)\'\);', line)
    if m:
        fen = m.group(1)
        solution = m.group(2)

        # replace the slash promotion notation with equals notation
        # eg: "d8/N#" -> "d8=N#"
        solution = re.sub(r'\/N', '=N', solution)
        solution = re.sub(r'\/B', '=B', solution)
        solution = re.sub(r'\/R', '=R', solution)
        solution = re.sub(r'\/Q', '=Q', solution)

        # get the description
        descr = ''
        for i in range(len(descr_i)):
            if game_num >= descr_i[i]:
                # if this is the last, or it's below the next list entry
                if i == len(descr_i)-1 or game_num < descr_i[i+1]:
                    descr = descr_text[i]
                    break;

        result = solution.split()[-1]

        # store the puzzle information in the player names 'cause often they appear
        # first in the games list (eg: my current version of SCID)
        white_text = "Puzzle %04d" % game_num
        black_text = descr
        event_text = white_text + ': ' + black_text 
        
        print "%s fen:%s" % (event_text, fen)

        fp.write(template % (event_text, white_text, black_text, fen, result, solution))
        game_num += 1
     
fp.close()

