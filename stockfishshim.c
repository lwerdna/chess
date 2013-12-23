/*
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
*/

/* includes */
#include <stdio.h>
#include <unistd.h>
#include <string.h>

#include <sys/types.h>

#define PATH_STOCKFISH "/usr/games/stockfish"

/* macros */
#define STOCKFISH_WRITE_BLOCK(a,b,c) stockfish_read_until(a,b,c, "stockfish: ")
#define STOCKFISH_READ_LINE(a,b,c) stockfish_read_until(a,b,c,"\n")

int stockfish_read_until(int fd, char *buff, int cap, char *terminator)
{
    int i, n;
    int rc = -1;

    memset(buff, '\0', cap);

    /* read one character at a time until terminator found */
    for(i=0; i<(cap-1); ++i) {
        n = read(fd, buff+i, 1);

        if(n != 1) {
            goto cleanup;
        }
    
        /* is terminating string found? */
        if(strstr(buff, terminator)) {
            rc = i+1;
            goto cleanup;
        }
    }

    cleanup:
    return rc;
}

int stockfish_write(int fd, char *buff)
{
    printf("sending stockfish: \"%s\"\n", buff);
    write(fd, buff, strlen(buff));
    write(fd, "\n", strlen("\n"));
    return 0;
}

int main(int ac, char **av)
{
    int rc = -1;
    int i;
    ssize_t n;
    char colorchar = ' ';
    pid_t childpid;
    char buff[4096];
    char fen[512];

    // Both argv and envp must be terminated by a NULL pointer.
    char *args_stockfish[] = { PATH_STOCKFISH, NULL };
    char *search_move;

    /* these fd's used to send commands down to stockfish */
    int fds_down[2];
    /* these fd's used to read output from stockfish (he writes up to us) */
    int fds_up[2];

    /* parse args */
    if(ac < 3) {
        printf("syntax: %s <move|\"all\"> <fen>\n", av[0]);
        goto cleanup;
    }
    
    search_move = av[1];

    fen[0] = '\0';
    for(i=2; i<ac; ++i) {
        strcat(fen, av[i]);
        strcat(fen, " ");
    }
    fen[strlen(fen)-1] = '\0';
    //printf("using FEN: %s\n", fen);

    /* create pipes */
    pipe(fds_down);
    pipe(fds_up);

    /* fork */
    childpid = fork();
    if(childpid == -1) {
        printf("ERROR: fork()\n");
        goto cleanup;
    }

    /* child activity */
    if(childpid == 0) {
        /* close writer from down pipes (we read from parent) */
        close(fds_down[1]); 
        /* close reader from up pipes (we write to parent) */
        close(fds_up[0]);

        /* duplicate the down rx pipe onto stdin */
        i = dup2(fds_down[0], STDIN_FILENO);
        if(i >= 0) {
            printf("dup2() on STDIN returned: %d\n", i);
        } 
        else {
            perror("dup2()");
            goto cleanup;
        }

        /* NO PRINTS WORK AFTER STDOUT_FILENO IS DONE */

        /* duplicate the up tx pipe onto stdout */
        i = dup2(fds_up[1], STDOUT_FILENO);
        if(i >= 0) {
            printf("dup2() on STDOUT returned: %d\n", i);
        } 
        else {
            perror("dup2()");
            goto cleanup;
        }

        /* now execute stockfish, having it inherit streams */
        execv("/usr/games/stockfish", args_stockfish);

        printf("if I made it this far, stockfish isn't running, fuck!\n");
    }
    /* parent activity */
    else {
        printf("spawned child process: %d\n", childpid);

        /* close reader from down pipes (we write to child) */
        close(fds_down[0]); 
        /* close writer from up pipes (we read from child) */
        close(fds_up[1]);

        /* consume stockfish's initial blurb */
        STOCKFISH_READ_LINE(fds_up[0], buff, sizeof(buff));
        printf("%s\n", buff);

        stockfish_write(fds_down[1], "uci");

        if(strcmp(search_move, "all") == 0) {
            stockfish_write(fds_down[1], "setoption name MultiPV value 3");
        }

        sprintf(buff, "position fen %s", fen);
        stockfish_write(fds_down[1], buff);

        sprintf(buff, "go movetime 2000");
        if(strcmp(search_move, "all") != 0) {
            sprintf(buff, "go movetime 2000 searchmoves %s", search_move);
        }

        stockfish_write(fds_down[1], buff);
        
        while(1) {
            STOCKFISH_READ_LINE(fds_up[0], buff, sizeof(buff));
            
            printf("%s\n", buff);

            if(strstr(buff, "bestmove")) {
                printf("done! breaking!\n");
                break;
            }
        }

        printf("done\n");
    }

    cleanup:
    return rc;
}
