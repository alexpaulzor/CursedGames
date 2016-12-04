#!/bin/bash

for p in $(cat puzzles/generated.sudoku puzzles/easy.txt puzzles/hard.txt | gsort -R); do
    (date; time ./sudoku.py $p -s) 2>&1 | tee -a puzzles/solvetimes/$p.log
    sleep 0.1
done
