for p in `cat puzzles/easy.txt`; do time ./sudoku.py $p -s 2>&1 | tee -a puzzles/solvetimes/$p.log; done
