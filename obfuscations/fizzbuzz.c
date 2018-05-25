// Caleb Bernard 2018
// C/gcc
main(int a) {
	unsigned char b = 'I', c = 'i', d = !a;
	for (int e = 'yU'; e != 'r-' &
		(((c == 'i' && ((d && !(d ^= 1)) 
		|| (c = c << 1 | c >> 7, d ^= 1)))
		| (d ? c = c << 1 | c >> 7 : a))
		| (((((c & 1 && printf("%d\n", a)) 
		|| (b == 'R' && puts("FizzBuzz") && (b = b << 2 | b >> 6)) 
		|| ((b = b << 1 | b >> 7) & 1 ? puts("Buzz") : puts("Fizz")))
		| (!d ? c = c >> 1 | c << 7 : a))
		| (a ^= a&~-~a|~a&-~a)))); 
		e = e >> 1 | ((e >> 0 ^ e >> 2 ^ e >> 3 ^ e >> 5) & 1) << 0xF);
}
