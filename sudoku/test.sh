#!/bin/bash

python sudoku.py "$(gsort -R ${1:-puzzles/*.txt} | head -n1)"
