#include<stdio.h>
// declaring the function
void printFibo(int );

int main()
{
    printf("\n\n\t\tStudytonight - Best place to learn\n\n\n");
    int k, n;
    long int i = 0, j = 1;
    printf("Enter the length of the Fibonacci series: ");
    scanf("%d", &n);
    printf("\n\nfirst %d terms of Fibonacci series are:\n\n\n",n);
    printf("%d ", 1);
    printFibo(n);
    printf("\n\n\t\t\tCoding is Fun !\n\n\n");
    return 0;
}

void printFibo(int aj)
{
    static long int first = 0, second = 1, sum;
    if(aj > 1)
    {
        sum = first + second;
        first = second;
        second = sum;
        printf("%ld ", sum);
        printFibo(aj-1);    // recursive call
    }
    else
    {
        // after the elements, for line break
        printf("\n\n\n");
    }
}
