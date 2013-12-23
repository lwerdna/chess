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
#include <signal.h>

#include <sys/types.h>
    
/* globals */
int g_analyze = 0;

/* macros */
#define SJENG_READ_BLOCK(a,b,c) sjeng_read_until(a,b,c,"Sjeng: ")
#define SJENG_READ_LINE(a,b,c) sjeng_read_until(a,b,c,"\n")

int sjeng_read_until(int fd, char *buff, int cap, char *terminator)
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

int sjeng_write(int fd, char *buff)
{
    printf("sending sjeng: \"%s\"\n", buff);
    write(fd, buff, strlen(buff));
    write(fd, "\n", strlen("\n"));
    return 0;
}

void handler_SIGALRM(int sig)
{
    printf("SIGALRM detected!\n");
    g_analyze = 0;
}

int main(int ac, char **av)
{
    int rc = -1;
    int i;
    ssize_t n;
    char colorchar = ' ';
    char holdings_white[64];
    char holdings_black[64];
    pid_t childpid;
    char *variant, *fen, *timelimit;
    char buff[4096];
    char *args_sjeng[] = { (char *)0 };

    /* these fd's used to send commands down to sjeng */
    int fds_down[2];
    /* these fd's used to read output from sjeng (he writes up to us) */
    int fds_up[2];

    /* parse args */
    if(ac < 4) {
        printf("syntax: %s <variant> <time limit> <fen>\n", av[0]);
        goto cleanup;
    }
    
    variant = av[1];
    timelimit = av[2];
    fen = av[3];
  
    {
        int n_fen;
        int i_first_space = 0;
        int i_last_slash = 0;
        n_fen = strlen(fen);

        /* first first space */
        for(i=0; i<n_fen; ++i) {
            if(fen[i] == ' ') {
                i_first_space = i;
                break;
            }
        }
        if(i_first_space == 0) {
            printf("ERROR: fen string (couldn't locate first space in \"%s\")\n", fen);
            goto cleanup;
        }

        /* find last slash (holdings) */
        for(i=i_first_space-1; i>0; --i) {
            if(fen[i] == '/') {
                i_last_slash = i;
                break;
            }
        }
        if(i_last_slash == 0) {
            printf("ERROR: fen string (couldn't find last slash in \"%s\")\n", fen);
            goto cleanup;
        }

        /* find color */
        colorchar = fen[i_first_space + 1];
        
        /* parse holdings */
        memset(holdings_white, '\0', sizeof(holdings_white));
        memset(holdings_black, '\0', sizeof(holdings_black));

        fen[i_first_space] = '\0';
        fen[i_last_slash] = '\0';

        for(i=i_last_slash + 1; i<i_first_space; ++i) {
            if(fen[i] == 'R' || fen[i] == 'P' ||
                fen[i] == 'N' || fen[i] == 'B' ||
                fen[i] == 'Q' || fen[i] == 'K') 
            {
                sprintf(buff, "%c", fen[i]);
                strcat(holdings_white, buff);
            }
            else if(fen[i] == 'r' || fen[i] == 'p' ||
                fen[i] == 'n' || fen[i] == 'b' ||
                fen[i] == 'q' || fen[i] == 'k') {
                sprintf(buff, "%c", fen[i]);
                strcat(holdings_black, buff);
            }
        }
    }

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

        /* now execute sjeng, having it inherit streams */
        execv("/usr/bin/sjeng", args_sjeng);

        printf("if I made it this far, sjeng isn't running, fuck!\n");
    }
    /* parent activity */
    else {
        int stat_loc;
        struct sigaction act;

        printf("spawned child process: %d\n", childpid);

/*
        act.sa_handler = handler_SIGALRM;
        sigemptyset(&act.sa_mask);
        sigaction(SIGALRM, &act, 0);
*/
        /* close reader from down pipes (we write to child) */
        close(fds_down[0]); 
        /* close writer from up pipes (we read from child) */
        close(fds_up[1]);
        printf("yo dawn\n");

        /* consume sjeng's initial blurb */
        i = SJENG_READ_BLOCK(fds_up[0], buff, sizeof(buff));
        if(i < 0) {
            goto cleanup;
        }
        printf("yo dawn\n");

        /* set the variant */
        sprintf(buff, "variant %s", variant);
        sjeng_write(fds_down[1], buff);
        if(SJENG_READ_BLOCK(fds_up[0], buff, sizeof(buff)) < 0)
            goto cleanup;

        sprintf(buff, "setboard %s", fen);
        sjeng_write(fds_down[1], buff);
        if(SJENG_READ_BLOCK(fds_up[0], buff, sizeof(buff)) < 0)
            goto cleanup;
 
        sprintf(buff, "holding [%s] [%s]", holdings_white, holdings_black);
        sjeng_write(fds_down[1], buff);
        if(SJENG_READ_BLOCK(fds_up[0], buff, sizeof(buff)) < 0)
            goto cleanup;

        sprintf(buff, "%s", colorchar == 'w' ? "white" : "black");
        sjeng_write(fds_down[1], buff);
        if(SJENG_READ_BLOCK(fds_up[0], buff, sizeof(buff)) < 0)
            goto cleanup;

        /* for "go" this has an effect ... for "analyze" it doesn't */
        /*
        sprintf(buff, "st %s", timelimit);
        sjeng_write(fds_down[1], buff);
        if(SJENG_READ_BLOCK(fds_up[0], buff, sizeof(buff)) < 0)
            goto cleanup;
        */

        /* set up timeout */
        printf("alarm(%s)\n", timelimit);
        alarm(atoi(timelimit));
        g_analyze = 1;

        sjeng_write(fds_down[1], "analyze");

        while(1) {
            //printf("reading sjeng line...\n");
            i = SJENG_READ_LINE(fds_up[0], buff, sizeof(buff));

            if(i<=0) {
                break;
            }

            printf("%s", buff);

            if(strstr(buff, "Used time : ")) {
                printf("analyze is finished! breaking!\n");
                SJENG_READ_BLOCK(fds_up[0], buff, sizeof(buff));

                /* after analyze, an "exit" is met with nothing...
                    yes, you must send it twice, try it manually... */
                sjeng_write(fds_down[1], "exit\nexit");
                SJENG_READ_BLOCK(fds_up[0], buff, sizeof(buff));
                
                break;
            }

            if(!g_analyze) {
                printf("time limit reached, killing, breaking from analyze loop...\n");
                kill(childpid, SIGTERM);
                break;
            }
        }

        waitpid(childpid, 0, 0);

        /*
        if(SJENG_READ_BLOCK(fds_up[0], buff, sizeof(buff)) < 0)
            goto cleanup;

        printf("result of analyze:\n");
        printf("%s", buff);

        sjeng_write(fds_down[1], "exit");
        if(SJENG_READ_BLOCK(fds_up[0], buff, sizeof(buff)) < 0)
            goto cleanup;

        printf("waiting for child to close...\n");
        waitpid(childpid, 0, 0);
        */

        printf("done\n");
    }

    cleanup:
    return rc;
}
