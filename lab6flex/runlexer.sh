#!/usr/bin/env bash

set -e

flex lexer.l
gcc -Wall lex.yy.c
./a.out test.txt
