%option noyywrap bison-bridge bison-locations

%{
#include "stdio.h"
#include "stdlib.h"
enum TokenType {
  END_OF_PROGRAM,
  IDENT,
  NUMBER,
  DECREMENT,
  LT,
  LE
};
char *tag_names[] = {
  "END_OF_PROGRAM", "IDENT", "NUMBER", "DECREMENT", "LT", "LE"
};

struct Position {
  int line, pos, index;
};

void print_pos(struct Position* p) {
  printf("(%d, %d)", p->line, p->pos);
};

struct Fragment {
  struct Position starting, following;
};

typedef struct Fragment YYLTYPE;

void print_frag(struct Fragment *f) {
  print_pos(&f->starting);
  printf("-");
  print_pos(&f->following);
};


union Token {
  char *ident;
  long num;
};

typedef union Token YYSTYPE;

struct Position cur;

#define YY_USER_ACTION { \
  yylloc->starting = cur; \
  for(int i = 0; i < yyleng; i++) { \
    cur.index++; \
    if (yytext[i] == '\n') { \
      cur.pos = 1; \
      cur.line++; \
    } else \
      cur.pos++; \
  } \
  yylloc->following = cur; \
}

void init_scanner(char* program) {
  cur.pos = 1;
  cur.index = 0;
  cur.line = 1;
  yy_scan_string(program);
}

void err(char* msg) {
  printf("Error ");
  print_pos(&cur);
  printf(": %s\n", msg);
}
%}

LETTER [a-zA-Z]
VOWEL [aeiou]
IDENT {VOWEL}{LETTER}*
DIGIT [0-9]
NUMBER -?{DIGIT}+
%%

[\n\t ]+

\-\- return DECREMENT;
\<\= return LE;
\< return LT;

{IDENT} {
  yylval->ident = yytext;
  return IDENT;
}
{NUMBER} {
  yylval->num = atoi(yytext);
  return NUMBER;
}

. {
  char dest[50];
  strcpy(dest, "unexpected character: ");
  strcat(dest, yytext);
  err(dest);
}
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

int main(int argc, char *argv[])
{
  int tag;
  YYSTYPE value;
  YYLTYPE coords;
  char* program_filepath = argv[1];
  char* program = read_file(program_filepath);
  init_scanner(program);
  do {
    tag = yylex(&value, &coords);
    if (tag != 0) {
      printf("%s ", tag_names[tag]);
      print_frag(&coords);
      printf(": ");
      if (tag == IDENT) {
        printf("%s", value.ident);
      } else if (tag == NUMBER) {
        printf("%d", value.num);
      }
      printf("\n");
    }
  } while (tag != 0);
  return 0;
}
