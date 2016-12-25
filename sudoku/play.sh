#!/bin/bash

python sudoku.py play "$(gsort -R ${1:-puzzles/*.txt} | head -n1)"
