#include "std_testcase.h"


void fun1()
{
    FILE * data;
    /* Initialize data */
    data = NULL;

    data = fopen("BadSource_fopen.txt", "w+");
    if (data != NULL)
    {
             _close((int)data);
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
