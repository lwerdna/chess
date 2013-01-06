#include <stdio.h>
#include <unistd.h>
#include <string.h>

#include <sys/types.h>

/* how many seconds to search for mate */
#define TIME_LIMIT 8

int sjeng_read_chunk(int fd, char *buff, int cap)
{
    int i, n;
    int rc = -1;

    memset(buff, '\0', cap);

    for(i=0; i<(cap-1); ++i) {
        n = read(fd, buff+i, 1);

        if(n != 1) {
            goto cleanup;
        }
    
        if(strstr(buff, "Sjeng: ")) {
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

int main(int ac, char **av)
{
    int rc = -1;
    int i;
    ssize_t n;
    char colorchar = ' ';
    char holdings_white[64];
    char holdings_black[64];
    pid_t childpid;
    char *variant, *fen;
    char buff[4096];
    char *args_sjeng[] = { (char *)0 };

    /* these fd's used to send commands down to sjeng */
    int fds_down[2];
    /* these fd's used to read output from sjeng (he writes up to us) */
    int fds_up[2];

    /* parse args */
    if(ac < 3) {
        printf("syntax: %s <variant> <fen>\n", av[0]);
        goto cleanup;
    }
    
    variant = av[1];
    fen = av[2];
  
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
            printf("ERROR: fen string\n");
            goto cleanup;
        }

        /* find last slash (holdings) */
        for(i=i_first_space-1; i>0; --i) {
            if(fen[i] == '/') {
                i_last_slash = i;
                break;
            }
        }
        if(i_first_space == 0) {
            printf("ERROR: fen string\n");
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
        /* close reader from down pipes (we write to child) */
        close(fds_down[0]); 
        /* close writer from up pipes (we read from child) */
        close(fds_up[1]);

        /* consume sjeng's initial blurb */
        i = sjeng_read_chunk(fds_up[0], buff, sizeof(buff));
        if(i < 0) {
            goto cleanup;
        }

        /* set the variant */
        sprintf(buff, "variant %s", variant);
        sjeng_write(fds_down[1], buff);
        if(sjeng_read_chunk(fds_up[0], buff, sizeof(buff)) < 0)
            goto cleanup;

        sprintf(buff, "setboard %s", fen);
        sjeng_write(fds_down[1], buff);
        if(sjeng_read_chunk(fds_up[0], buff, sizeof(buff)) < 0)
            goto cleanup;
 
        sprintf(buff, "holding [%s] [%s]", holdings_white, holdings_black);
        sjeng_write(fds_down[1], buff);
        if(sjeng_read_chunk(fds_up[0], buff, sizeof(buff)) < 0)
            goto cleanup;

        sprintf(buff, "%s", colorchar == 'w' ? "white" : "black");
        sjeng_write(fds_down[1], buff);
        if(sjeng_read_chunk(fds_up[0], buff, sizeof(buff)) < 0)
            goto cleanup;

        sprintf(buff, "st %d", TIME_LIMIT);
        sjeng_write(fds_down[1], buff);
        if(sjeng_read_chunk(fds_up[0], buff, sizeof(buff)) < 0)
            goto cleanup;

        sjeng_write(fds_down[1], "go");
        if(sjeng_read_chunk(fds_up[0], buff, sizeof(buff)) < 0)
            goto cleanup;

        printf("result of go:\n");
        printf("%s", buff);

        sjeng_write(fds_down[1], "exit");
        if(sjeng_read_chunk(fds_up[0], buff, sizeof(buff)) < 0)
            goto cleanup;

        printf("waiting for child to close...\n");
        waitpid(childpid, 0, 0);
        printf("done\n");
    }


    cleanup:
    return rc;
}
