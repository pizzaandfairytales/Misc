// Obfuscated Counter Generator
// Caleb Bernard
// Outputs a C++ program with a heavily obfuscated for loop!
#include <iostream>
#include <ctime>
int main()
{
	int l = 100; // Change this to get new number of loops!
	
	srand(time(NULL));
	int s = rand() % 65534 + 1;
	int a = s;
	for (int b=0;b<l;b++){a=(a>>1)|((((a>>0)^(a>>2)^(a>>3)^(a>>5))&1)<<0xF);}
	std::cout << "// Alpaca Counts to "<<l<<"\n#include <iostream>\nint main()\n{\n   int num = 0;\n";
	std::cout << "for (int a=0x"<<std::hex<<s<<";a!=0x"<<a<<";a=(a>>1)|((((a>>0)^(a>>2)^(a>>3)^(a>>5))&1)<<0xF)) {\n";
	std::cout << "      num++;\n   }\n   std::cout << num << '\\n';\n   return 0;\n}";
	return 0;
}
