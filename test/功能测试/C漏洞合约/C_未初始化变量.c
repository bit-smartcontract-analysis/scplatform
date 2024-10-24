
#include "std_testcase.h"

#include <wchar.h>



void fun1()
{
    char * data;

    printLine(data);
}




#ifdef INCLUDEMAIN

int main(int argc, char * argv[])
{
    /* seed randomness */
    srand( (unsigned)time(NULL) );

   fun1();

    return 0;
}

#endif
