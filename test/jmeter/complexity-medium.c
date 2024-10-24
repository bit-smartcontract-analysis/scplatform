
#include "std_testcase.h"

static char* staticString = "Hello";


static char * helper()
{
    if(rand()%2 == 0)
    {
        return NULL;
    }
    else
    {
        return staticString;
    }
}


void fun1()
{
    if(helper == NULL)
    {
        printLine("Got a NULL");
    }
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
