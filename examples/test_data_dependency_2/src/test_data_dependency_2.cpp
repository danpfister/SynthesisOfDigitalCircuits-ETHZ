#include <stdlib.h>

#define AMOUNT_OF_TEST 1

int test_data_dependency_2(int a, int b, int c, int n) {
	a = (b*a)%c;
	a = a ^ c;
	b = a * n;
	c = (b + c) * n;
	return c;
}


int main(void){
	int a, b, c;
	a = rand()%10;
	b = rand()%10;
	c = rand()%10;

	int i = 0;
	i = rand()%10;
	test_data_dependency_2(a, b, c, i);
}

