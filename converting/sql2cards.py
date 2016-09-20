#!/usr/bin/python

# got: "The manual of chess combinations - Volume I" by S. Ivashenko ( CDB )
# from: these from http://pbchess.vlasovsoft.net/en/contents.html
#
# used sqlitebrowser to export a .csv file (puzzles.csv)
#
# used this to make a .cards

import os
import sys

import re

if len(sys.argv) < 3:
    raise Exception("provide in file and out file")

(inFile, outFile) = sys.argv[1:3]

fp = open(inFile, 'r')
lines = fp.readlines()
fp.close()

game_num = 1
        
fp = open(outFile, 'w')

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

        # out to file
        fp.write("%s\n" % fen);
        fp.write("puzzle %d: %s\n" % (game_num, descr));
        fp.write("%s\n"% solution)
        fp.write("\n")

        game_num += 1
     
fp.close()

