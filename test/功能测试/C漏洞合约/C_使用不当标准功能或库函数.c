
#include "std_testcase.h"

#include <iostream>

using namespace std;

#define CHAR_BUFFER_SIZE 10

namespace basic_01
{

void fun1()
{
    {
        char charBuffer[CHAR_BUFFER_SIZE];
        cin >> charBuffer;
        charBuffer[CHAR_BUFFER_SIZE-1] = '\0';
        printLine(charBuffer);
    }
}


#ifdef INCLUDEMAIN

using namespace basic_01; 
int main(int argc, char * argv[])
{
    /* seed randomness */
    srand( (unsigned)time(NULL) );
    fun1();
    return 0;
}

#endif
