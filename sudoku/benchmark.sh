#!/bin/bash

for p in $(cat puzzles/top95.txt); do
    (date; time ./sudoku.py solve -v -l $p) 2>&1 | tee -a puzzles/solvetimes/$p.log
    sleep 0.1
done
