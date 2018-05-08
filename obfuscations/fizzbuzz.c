// Caleb Bernard 2018
#include <stdio.h>
main(int a){
	unsigned char b = 'I', c = 'i', d = !a;
	for (int e = '+.'; e != 'H<'; e = e >> 1 | ((e >> 0 ^ e >> 2 ^ e >> 3 ^ e >> 5) & 1) << 0xF) {
		if (!d && c == 'i') c = c << 1 | c >> 7, d ^= 1;
		else if (d && c == 'i') d ^= 1;
		d ? c = c << 1 | c >> 7 : a;
		if (c & 1) printf("%d\n", a);
		else if (b == 'R') printf("FizzBuzz\n"), b = b << 2 | b >> 6;
        else (b = b << 1 | b >> 7) & 1 ? printf("Buzz\n") : printf("Fizz\n");
		!d ? c = c >> 1 | c << 7 : a;
        a ^= a&~-~a|~a&-~a;
	}
}
