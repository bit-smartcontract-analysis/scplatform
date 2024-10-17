
#include "std_testcase.h"

#include <wchar.h>


void fun1()
{
    wchar_t * data;
    data = NULL;
    {
        wchar_t myString[] = L"myString";

        data = wcsdup(myString);
        /* Use data */
        printWLine(data);
    }

  
}




#ifdef INCLUDEMAIN

int main(int argc, char * argv[])
{
    /* seed randomness */
    srand( (unsigned)time(NULL) );

    printLine("Calling bad()...");
    func1();
    printLine("Finished bad()");

    return 0;
}

#endif
