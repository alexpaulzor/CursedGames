#!/bin/bash

python sudoku.py "$(gsort -R ${1:-puzzles/easy.txt} | head -n1)"
