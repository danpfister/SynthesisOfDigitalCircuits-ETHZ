#include <stdlib.h>

#define AMOUNT_OF_TEST 1

int test_resources_constraints_1(int a, int b, int c, int n) {
	a = (b + 50) * (100 + n) * (40 + c) * (10 + a);
	if ( a > n * 10000 ) {
		a = a / (n + c);
	}
	else {
		a = b % (a + c);
	}
	c = (a * n) ^ (c * b) ;
	return c;
}


int main(void){
	int a, b, c;
	a = rand()%10;
	b = rand()%10;
	c = rand()%10;

	int i = 0;
	i = rand()%10;
	test_resources_constraints_1(a, b, c, i);
}

