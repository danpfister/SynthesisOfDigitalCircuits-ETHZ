#include <stdlib.h>

int test_initiation_interval_1 (int a[], int b[], int c[]) {
	int acc = 0;
	for (int i = 0; i < 100; ++i) {
		acc += ( (a[i] % 2) * (b[i] % 3) + (c[i] % 3) * (b[i] % 5) + (a[i] % 7) );
	}
	return acc;
}

int main(void){
	int a[100], b[100], c[100];
	for (int i = 0; i < 100; ++i) {
		a[i] = rand() % 10;
		b[i] = rand() % 10;
		c[i] = rand() % 10;
	}
	test_initiation_interval_1(a, b, c);
}

