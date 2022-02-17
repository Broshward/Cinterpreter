#include <stdio.h>
#include "test.h"
#define FOO TEST
typedef unsigned char foo1, foo2, foo3 ;
typedef char foo4, foo5, foo6;
typedef char foo7;
 
typedef struct {
	int r;
	char b;
	foo1 s;
} first;

typedef struct {
	int qwe;
	int ewq;
	struct AAAAA{
		int pop;
		int top;
		} rrr;
	char str;
} rew;

struct ABC{
	int a;
	int b;
	char c;
} sss,ss={1,2,'1'};

union ABCD{
	int a;
	int b;
	char c;
} sa;

enum aaa {
	s,d,f
};

enum qqq {
	a,b,c,aa=789,bb,cc
};


void test_func_type_declare()
{
	struct you {
		int rem;
		char age;
	};
	struct you you1;
	you1.rem=65536;
}

int main()
{
	int was=65536;
	foo1 foo = '1';
	struct ABC qw;
	struct AAAAA zaq;
	printf("size of AAAAA %d\n", sizeof(sss));
	//printf("%c, %d",foo,foo);
	enum qqq ewq;
	ewq=f;
	printf("enum %d,%d,%d",a,b,ewq);
}
