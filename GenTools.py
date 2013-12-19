#!/usr/bin/python

# Copyright 2012, 2013 Andrew Lamoureux
#
# This file is a part of FunChess
#
# FunChess is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#!/usr/bin/python

import re
import Common

def fenPieceToBitmapFile(p, square):
    # square is either 'd'/0 (dark) or 'l'/1 (light)

    mapping =       { 'P':'pl', 'p':'pd',
                      'B':'bl', 'b':'bd',
                      'N':'nl', 'n':'nd',
                      'R':'rl', 'r':'rd',
                      'Q':'ql', 'q':'qd',
                      'K':'kl', 'k':'kd'
                      }

    # knock off the promoted modifier
    p = re.sub('~', '', p)

    colorChar = ['d', 'l'][square]

    if p == ' ':
        return colorChar + 'sq48.gif'
    else:
        if not p in mapping:
            while 1:
                raise Exception("invalid piece! (%s)" % p)

        return mapping[p] + colorChar + '48.gif'


def holdingsTableToHtml(holdingsString, color, imgPath=''):
    html = ''
    #html += '<!-- generating holdings table for %s -->\n' %  holdingsString

    pieceChars = []
    if color == 'w':
        pieceChars = filter(lambda x: not x.islower(), list(holdingsString))
    else:
        pieceChars = filter(lambda x: x.islower(), list(holdingsString))

    html += '<table border=0 cellpadding=0 cellspacing=0>\n'
    html += '<tr><td>\n'
    for pieceChar in pieceChars:
        tmp = fenPieceToBitmapFile(pieceChar, 0)
        html += '<img src="%s%s" />' % (imgPath, tmp)
    html += '</tr></td>'
    html += '</table>\n'

    return html

def boardMapToHtml(boardMap, flipped=0, imgPath=''):
    html = ''

    pieceGetSequence = range(64)

    if(flipped):
        pieceGetSequence.reverse()
        html += holdingsTableToHtml(boardMap['holdings'], 'w', imgPath)
    else:
        html += holdingsTableToHtml(boardMap['holdings'], 'b', imgPath)

    html += '<br>\n'
    html += '<table border=0 cellpadding=0 cellspacing=0>\n'
    html += '<tr>\n'

    for i in range(64):
        # end current row, start new row
        if not (i%8):
            html += '\n</tr>\n'
            html += '<tr>\n'

        # table cell has image in it
        # get either 0,1,2,... or 63,62,61,...
        tmp = pieceGetSequence[i]
        # map 0->'a8', 63->'h1', etc.
        tmp = Common.squaresSan[tmp]
        # map 'a8' to 'r' or 'R' for example (getting piece)
        tmp = boardMap[tmp]
        # finally, map that piece to a filename
        tmp = fenPieceToBitmapFile(tmp, (i+i/8+1)%2)

        html += ' <td><img src="%s%s" /></td>\n' % (imgPath, tmp)

    html += '\n</tr>\n'
    html += '</table>\n'

    html += '<br>\n'

    if(flipped):
        pieceGetSequence.reverse()
        html += holdingsTableToHtml(boardMap['holdings'], 'b', imgPath)
    else:
        html += holdingsTableToHtml(boardMap['holdings'], 'w', imgPath)

    return html



