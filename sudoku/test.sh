#!/bin/bash

python sudoku.py play -l "$(gsort -R ${1:-puzzles/*.txt} | head -n1)"
