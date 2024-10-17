#include "std_testcase.h"

void fun1()
{
    {
        twoIntsStruct *twoIntsStructPointer = NULL;
        if ((twoIntsStructPointer != NULL) & (twoIntsStructPointer->intOne == 5))
        {
            printLine("intOne == 5");
        }
    }
}

int main(int argc, char * argv[])
{
    /* seed randomness */
    srand( (unsigned)time(NULL) );
    fun1();
    return 0;
}


