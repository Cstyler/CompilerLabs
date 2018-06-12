
%option reentrant noyywrap bison-bridge bison-locations
%option extra-type="struct Extra *"

%{

#include <stdio.h>
#include <stdlib.h>
#include "lexer.h"
#include "y.tab.h"
#define DEBUG 0
#define YY_USER_ACTION                                             \
	{                                                          \
		int i;                                             \
		struct Extra *extra = yyextra;                     \
		if (! extra->continued) {                          \
			yylloc->first_line = extra->cur_line;      \
			yylloc->first_column = extra->cur_column;  \
		}                                                  \
		extra->continued = 0;                              \
		for (i = 0; i < yyleng; i++)                       \
		{                                                  \
			if (yytext[i] == '\n')                     \
			{                                          \
				extra->cur_line++;                 \
				extra->cur_column = 1;             \
			}                                          \
			else                                       \
				extra->cur_column++;               \
			}                                          \
		                                                   \
		yylloc->last_line = extra->cur_line;               \
		yylloc->last_column = extra->cur_column;           \
	}

void yyerror(YYLTYPE *loc, yyscan_t scanner, struct node* stack, unsigned char newline_flag, const char *msg)
{
	printf("Error (%d,%d): %s\n", loc->first_line, loc->first_column, msg);
}

%}

LETTER   [a-zA-Z]
DIGIT    [0-9]
IDENT    {LETTER}({LETTER}|{DIGIT})*
NUMBER   {DIGIT}+

%%

[\t ]+

\n {
	return NEWLINE;
}

=		return ASSIGN;

\<\!\-\-.*\-\-\> {
	yylval->ident = strdup(yytext);
	if (DEBUG) {
		printf(yylval->ident);
	}
	return COMMENTS;
}

\<\/{IDENT} {
	yylval->ident = strdup(yytext);
	if (DEBUG) {
		printf(yylval->ident);
	}
	return CLOSE_TAG;
}

\<{IDENT}	{
	yylval->ident = strdup(yytext);
	if (DEBUG) {
		printf(yylval->ident);
	}
	return OPEN_TAG;
}

\/\>	{
	if (DEBUG) {
		printf(yytext);
	}
	return RSPAREN;
}
\>	{
	if (DEBUG) {
		printf(yytext);
	}
	return RPAREN;
}

\<\?xml return XML_LPAREN;
\?\> return XML_RPAREN;


{IDENT}	{
	yylval->ident = strdup(yytext);
	if (DEBUG) {
		printf(yylval->ident);
	}
	return ATTR_KEY;
}


\"[^\"\n]+\"	{
	yylval->ident = strdup(yytext);
	/* printf(yylval->ident); */
	if (DEBUG) {
		printf(yylval->ident);
	}
	return ATTR_VALUE;
}

{NUMBER} {
	yylval->num = atoi(yytext);
	if (DEBUG) {
		printf("%ld", yylval->num);
	}
	return NUMBER;
}
%%

void init_scanner(const char *program, yyscan_t *scanner, struct Extra *extra)
{
	extra->continued = 0;
	extra->cur_line = 1;
	extra->cur_column = 1;
	yylex_init(scanner);
	yylex_init_extra(extra, scanner);
	yy_scan_string(program, *scanner);
}

void destroy_scanner(yyscan_t scanner)
{
	yylex_destroy(scanner);
}
