
%{
#include <stdio.h>
#include "lexer.h"
#include "stdlib.h"
#include "stack.h"
#define PF printf
#define PIDENT(ident_num) for(int i = 0; i < ident_num; ++i) { \
	PF("  "); \
}
%}

%define api.pure
%locations
%lex-param {yyscan_t scanner}
%parse-param {yyscan_t scanner}
%parse-param {struct node* stack}
%parse-param {unsigned char newline_flag}
%union {
	char* ident;
	long num;
}

%token ASSIGN RSPAREN RPAREN XML_LPAREN XML_RPAREN NEWLINE
%token <ident> CLOSE_TAG
%token <ident> OPEN_TAG
%token <ident> ATTR_VALUE
%token <ident> ATTR_KEY
%token <ident> COMMENTS
%token <num> NUMBER

%{
int yylex(YYSTYPE * yylval_param, YYLTYPE * yylloc_param , yyscan_t scanner);
void yyerror(YYLTYPE *yylloc, yyscan_t scanner, struct node* stack, unsigned char newline_flag, const char *msg);
%}

%%
root:
	OPEN_TAG {
		if (! st_is_empty(stack)) {
			if (newline_flag) {
				PIDENT(st_peek(stack)->ident_num);
			} else {
				PF(" ");
			}
		}
		PF($1);
		free($1);
	} nl attrs root__
| XML_LPAREN { PF("<?xml"); } nl attrs XML_RPAREN { PF("?>"); } nl root
| COMMENTS { PF($1); free($1); } nl root;
root__:
	RPAREN {
		if (! st_is_empty(stack) && newline_flag) {
			PIDENT(st_peek(stack)->ident_num);
		}
		PF(">");
	} nl content root_
| RSPAREN {
		PF("/>");
		if (! st_is_empty(stack)) {
			NODE_DATA element;
			stack = st_pop(stack, &element);
		}
	} nl;
root_:
	CLOSE_TAG {
		if (! st_is_empty(stack) && newline_flag) {
			PIDENT(st_peek(stack)->ident_num);
		}
		PF($1);
		free($1);
	} nl attrs RPAREN {
	PF(">");
	if (! st_is_empty(stack)) {
		/* PF("POP"); */
		NODE_DATA element;
		stack = st_pop(stack, &element);
	}} nl;
content:
	NUMBER {
		if (! st_is_empty(stack) && newline_flag) {
			PIDENT(st_peek(stack)->ident_num);
		}
		PF("%ld", $1);
		} nl
| ATTR_KEY {
	if (! st_is_empty(stack) && newline_flag) {
		PIDENT(st_peek(stack)->ident_num);
	}
	PF($1);
	free($1);
} nl
| roots;
roots: {
	if (!st_is_empty(stack)) {
		unsigned int cur =  st_peek(stack)->ident_num;
		NODE_DATA element;
		element.ident_num = cur + 1;
		stack = st_push(stack, element);
	}
}
root roots
| %empty ;


attrs:
	{ if(!newline_flag) PF(" "); } attr attrs_
| %empty ;
attrs_:
	{ if(!newline_flag) PF(" "); } attr attrs_
| %empty { if (!newline_flag) PF(" "); } ;
attr:
	ATTR_KEY {
		if (! st_is_empty(stack) && newline_flag) {
			PIDENT(st_peek(stack)->ident_num);
		}
		PF($1);
		free($1);
		} nl ASSIGN {
			if (! st_is_empty(stack) && newline_flag) {
				PIDENT(st_peek(stack)->ident_num);
			}
			PF("=");
		} nl attr_;
attr_:
	ATTR_VALUE {
		if (! st_is_empty(stack) && newline_flag) {
			PIDENT(st_peek(stack)->ident_num);
		}
		PF($1);
		free($1);
	} nl;
nl:
	NEWLINE {
		newline_flag = 1;
		PF("\n");
	} nl_
| %empty {
	newline_flag = 0;
};
nl_:
	NEWLINE {
		PF("\n");
	} nl_
| %empty;
%%

char* read_file(char* file_name) {
  char *buffer = NULL;
  size_t size = 0;

  /* Open your_file in read-only mode */
  FILE *fp = fopen(file_name, "r");

  /* Get the buffer size */
  fseek(fp, 0, SEEK_END); /* Go to end of file */
  size = ftell(fp); /* How many bytes did we pass ? */

  /* Set position of stream to the beginning */
  rewind(fp);

  /* Allocate the buffer (no need to initialize it with calloc) */
  buffer = malloc((size + 1) * sizeof(*buffer)); /* size + 1 byte for the \0 */

  /* Read the file into the buffer */
  fread(buffer, size, 1, fp); /* Read 1 chunk of size bytes from fp into buffer */

  /* NULL-terminate the buffer */
  buffer[size] = '\0';
  return buffer;
}

int main(int argc, char* argv[])
{
	yyscan_t scanner;
	struct Extra extra;
	if (argc != 2) {
		printf("Need 1 argument, found: %d\n", argc - 1);
		return -1;
	}
	char* program_filepath = argv[1];
  char* program = read_file(program_filepath);
	init_scanner(program, &scanner, &extra);
	struct node * st;
	st_init(&st);
	NODE_DATA element;
	element.ident_num = 0;
	st = st_push(st, element);
	st = st_push(st, element);
	unsigned char newline_flag = 1;
	yyparse(scanner, st, newline_flag);
	destroy_scanner(scanner);
	free(program);
	st_free(st);
	return 0;
}
