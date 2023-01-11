#include <stdlib.h>

#define AMOUNT_OF_TEST 1

int test_control_dependency_1(int a, int b, int c, int n) {
	a = ((b + a) * n) >> c;
	if(((a * c) - b) >= (n/(c * b) % c) ){
		a = (a >> n) * b;
		c = (a / b) >> c;
	}
	c = ((a  + b) * (n >> c));
	return c;
}


int main(void){
	int a, b, c;
	a = rand()%10;
	b = rand()%10;
	c = rand()%10;

	int i = 0;
	i = rand()%10;
	test_control_dependency_1(a, b, c, i);
}

