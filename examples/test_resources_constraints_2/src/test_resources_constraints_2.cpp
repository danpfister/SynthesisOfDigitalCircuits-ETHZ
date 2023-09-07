#include <stdlib.h>

#define AMOUNT_OF_TEST 1

int test_resources_constraints_2(int a, int b, int c, int n) {
	n += ( (a / 2)  + (b * 3)  + (c * 5)  + (n * 7) );
	b += ( (a * 11) + (b / 13) + (c * 17) + (n * 19) );
	c += ( (a * 23) + (b * 29) + (c / 31) + (n * 37) );
	a += ( (a * 41) + (b * 43) + (c * 47) + (n / 53) );
	return a;
}


int main(void){
	int a, b, c;
	a = rand()%10;
	b = rand()%10;
	c = rand()%10;

	int i = 0;
	i = rand()%10;
	test_resources_constraints_2(a, b, c, i);
}

