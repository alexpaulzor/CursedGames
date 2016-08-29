#!/bin/bash

python sudoku.py "$(gsort -R ${1:-puzzles/hard.txt} | head -n1)"
