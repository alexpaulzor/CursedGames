#!/usr/bin/env python

import curses
import click

import sys
import time
from sudokuboard import SudokuBoardSolver, SudokuBoardGenerator, N, N_2, N_4
from display import SudokuDisplay
import threading


@click.group()
def cli():
    pass


@cli.command()
@click.option('-l', '--load', type=str)
@click.option('-x', '--x-regions', is_flag=True)
@click.option('-m', '--meta-regions', is_flag=True)
@click.option('-v', '--verbose', is_flag=True)
def play(load, x_regions, meta_regions, verbose):
    s = SudokuDisplay(x_regions, meta_regions)
    if load:
        s.board.load_game(str(load))

    try:
        curses.wrapper(s.newgame)
    # except Exception as e:
    #     print repr(e)
    finally:
        print "\n".join(s.board._log)
        print "initial: " + str(s.board.original_state)
        print "final: " + s.board.current_state()
        if s.board.is_solved():
            print "You won!"
        else:
            print "Unsolved ({} remaining)".format(
                len(list(s.board.unsolved_squares())))
        print "({} clues, {} steps)".format(s.board.clues, s.steps)

def log(msg, replace=False):
    print msg

@cli.command()
@click.option('-x', '--x-regions', is_flag=True)
@click.option('-m', '--meta-regions', is_flag=True)
@click.option('-v', '--verbose', is_flag=True)
def generate(x_regions, meta_regions, verbose):
    board = SudokuBoardGenerator(x_regions, meta_regions)
    last_status_clock = time.clock()
    for msg in board.generate_iter():
        if 'gen' in msg or time.clock() - last_status_clock > 1:
            last_status_clock = time.clock()
            for lmsg in board._log:
                print lmsg
            board._log = []
            print msg



@cli.command()
@click.option('-l', '--load', type=str)
@click.option('-x', '--x-regions', is_flag=True)
@click.option('-m', '--meta-regions', is_flag=True)
@click.option('-v', '--verbose', is_flag=True)
@click.option('-B', '--disable-bruteforce', is_flag=True)
def solve(load, x_regions, meta_regions, verbose, disable_bruteforce):
    board = SudokuBoardSolver(x_regions, meta_regions)
    board.load_game(str(load))
    console_solve(board, verbose=verbose,
                  allow_bruteforce=not disable_bruteforce)


def console_solve(board, verbose=True, allow_bruteforce=False):
    prev_state = None
    while board.current_state() != prev_state:
        prev_state = board.current_state()
        for msg in board.solve_step_iter(prev_state, verbose=True):
            print msg
    if not board.is_solved() and allow_bruteforce:
        print "Bruteforcing..."
        last_status_clock = time.clock()
        for msg in board.solve_iter():
            if time.clock() - last_status_clock > 1:
                last_status_clock = time.clock()
                print msg


if __name__ == "__main__":
    cli()
