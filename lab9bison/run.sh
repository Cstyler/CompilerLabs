#!/usr/bin/env bash

lex lexer.l
yacc -d parser.y -Wall -v
gcc -o xml_formatter *.c -Wall
rm -f lex.yy.c y.tab.c y.tab.h
echo "Run ./xml_formatter 'filename' for test"
