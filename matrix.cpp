#include <iostream>
#include <stdbool.h>


// Matrix rotations:
/*
	matrices with an odd number of rows & cols will have a stable center.
	We can probably avoid rotating it with a integer division trick.

	For each point, there are four corresponding points in its 'swap group'.
	A swap group can be dealt with in 3 swaps, and then all those points are
	in their resting place.
					012
					345
					678
	Here [0,2,8,6] is a swap group, and [1,5,7,3] is the other.
	For the first group, swap 2-0, 2-6, 2-8 and each of them is happy.
	I think we can expect (size - 1)^2 swap groups, unless size is odd. (size - 2)^2?

*/
class matrix2d{
private:
	int size;
	int **matrix;
public:
	matrix2d(int s){
		size = s;
		matrix = new int*[s];
		for (int x = 0; x < s; x++){
			matrix[x] = new int[s];
		}
	}
	int get(int x, int y){
		return matrix[x][y];
	}
	void set(int x, int y, int val){
		matrix[x][y] = val;
	}
	int getSize(){
		return size;
	}
	// rotate right
	void rotate(){
		int start = 0;
		for (int x = size; x > 1; x -= 2){
			int a = start;
			int b = start;
			int c = x - 1;
			int d = x - 1;
			int temp;
			for (int y = 0; y < x - 1; y++){
				temp = matrix[a][b];
				matrix[a][b] = matrix[b][c];
				matrix[b][c] = temp;
				temp = matrix[d][a];
				matrix[d][a] = matrix[a][b];
				matrix[a][b] = temp;
				temp = matrix[c][d];
				matrix[c][d] = matrix[d][a];
				matrix[d][a] = temp;
				b++;
				d--;
			}
			start += 1;
		}
	}
	void print(){
		for (int y = 0; y < size; y++){
			for (int z = 0; z < size; z++){
				std::cout << matrix[y][z] << ' ';
			}
			std::cout << '\n';
		}
	}
};

int main(){
	int x = 0;
	int size = 5;
	matrix2d matrix = matrix2d(size);
	for (int y = 0; y < size; y++){
		for (int z = 0; z < size; z++){
			matrix.set(y,z,x++);
		}
	}
	matrix.print();
	matrix.rotate();
	matrix.print();
	return 0;
}
