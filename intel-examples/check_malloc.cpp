#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>

#ifndef _TM
#error TM not enabled
#endif


int main(int argc, char** argv)
{
    printf("%s\n", argv[0]);
    if (argc <= 1)
        exit(1);
    int size = atoi(argv[1]);
    char cmd[100];
    //sprintf(cmd, "cat /proc/%d/status | grep VmSize", getpid());
    void* p;
    __tm_atomic {
        //system(cmd);
        p = malloc(size);
        //system(cmd);
        __tm_retry;
    }
}


