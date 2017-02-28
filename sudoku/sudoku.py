#!/usr/bin/env python

import curses
import click

import sys
import time
from sudokuboard import SudokuBoardSolver, N, N_2, N_4, UnsolvableError
from sudokugenerator import SudokuBoardGenerator
from display import SudokuDisplay
import threading


@click.group()
def cli():
    pass


@cli.command()
@click.argument('puzzle', type=str, required=False)
@click.option('-x', '--x-regions', is_flag=True)
@click.option('-m', '--meta-regions', is_flag=True)
@click.option('-v', '--verbose', is_flag=True)
@click.option('-g', '--generate', is_flag=True)
def play(puzzle, x_regions, meta_regions, verbose, generate):
    if generate:
        puzzle = _generate(x_regions, meta_regions, verbose)
    s = SudokuDisplay(x_regions, meta_regions)
    if puzzle:
        s.board.load_game(str(puzzle))

    try:
        curses.wrapper(s.newgame)
    except Exception as e:
        print repr(e)
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
    _generate(x_regions, meta_regions, verbose)

def _generate(x_regions, meta_regions, verbose):
    board = SudokuBoardGenerator(x_regions, meta_regions)
    last_status_clock = time.clock()
    for msg in board.generate_iter(verbose=verbose):
        if verbose or 'gen' in msg or time.clock() - last_status_clock > 1:
            last_status_clock = time.clock()
            for lmsg in board._log:
                print lmsg
            board._log = []
            print msg
    result = board.current_state(givens_only=True)
    print "Generated: " + result
    return result



@cli.command()
@click.argument('puzzle', type=str, required=False)
@click.option('-x', '--x-regions', is_flag=True)
@click.option('-m', '--meta-regions', is_flag=True)
@click.option('-v', '--verbose', is_flag=True)
def solve(puzzle, x_regions, meta_regions, verbose):
    board = SudokuBoardSolver(x_regions, meta_regions)
    if puzzle:
        board.load_game(str(puzzle))
    console_solve(board, verbose=verbose)

@cli.command()
@click.argument('puzzle', type=str, required=False)
@click.option('-x', '--x-regions', is_flag=True)
@click.option('-m', '--meta-regions', is_flag=True)
@click.option('-v', '--verbose', is_flag=True)
def bruteforce(puzzle, x_regions, meta_regions, verbose):
    board = SudokuBoardSolver(x_regions, meta_regions)
    if puzzle:
        board.load_game(str(puzzle))
    # try:
    #     console_solve(board, verbose=verbose)
    # except UnsolvableError:
    #     print "Unsolvable by intuition. Bruteforcing..."
    last_status_clock = time.clock()
    for msg in board.bruteforce_iter():
        if verbose or time.clock() - last_status_clock > 1:
            last_status_clock = time.clock()
            print msg
    if board.is_solved():
        print "Solved! " + board.current_state(include_possibles=False)
    else:
        print "Could not solve " + board.current_state()


def console_solve(board, verbose=True):
    # prev_state = None
    # while board.current_state() != prev_state:
    #     prev_state = board.current_state()
    #     for msg in board.solve_step_iter(prev_state, verbose=True):
    #         print msg
    # if not board.is_solved() and allow_bruteforce:
    #     print "Bruteforcing..."
    last_status_clock = time.clock()
    for msg in board.solve_iter(verbose=verbose):
        if verbose or time.clock() - last_status_clock > 1:
            last_status_clock = time.clock()
            print msg
    if board.is_solved():
        print "Solved! " + board.current_state(include_possibles=False)
    else:
        print "Could not solve " + board.current_state()

if __name__ == "__main__":
    cli()
