#!/usr/bin/python

import curses
import time
import random
from square import Square
import sys

class mines:
	board = {}
	x = 0
	y = 0
	stdscr = None	
	retval = None
	COLORS = { '1' : 1, '2' : 2, '3' : 3, '4' : 4, '5' : 5, '6' : 6, '7' : 7, '8' : 8, 'M' : 9, 'F' : 10 }

	def __init__(self, width, height, percentage):
		nummines = int(width * height * percentage / 100.0)
		self.newboard(height, width, nummines)
		self.y = 0
		self.x = 0
		curses.wrapper(self.newgame)
		print self.retval

		

	def newgame(self, stdscr):
		curses.init_pair(9, curses.COLOR_RED, curses.COLOR_BLUE)
		curses.init_pair(10, curses.COLOR_BLUE, curses.COLOR_RED)
		curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
		curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
		curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
		curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
		curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
		curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
		curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK)
		self.stdscr = stdscr
		self.stdscr.clear()
		self.printboard()
		self.stdscr.addstr(self.y, self.x*2, '')
		self.stdscr.refresh()
		key = None
		while (key != 'q'):
			
			key = self.stdscr.getkey()
			if (key == 'KEY_LEFT' or key == 'h') and self.x > 0:
				self.x = self.x - 1
			elif (key == 'KEY_RIGHT' or key == 'l') and self.x < width - 1:		
				self.x = self.x + 1
			elif (key == 'KEY_UP' or key == 'k') and self.y > 0:
				self.y = self.y - 1
			elif (key == 'KEY_DOWN' or key == 'j') and self.y < height - 1:
				self.y = self.y + 1
			elif (key == 'a'):
				result = self.board[self.y][self.x].trigger()
				if result:
					self.lost()
					self.retval = "You lose."
					return
			elif (key == 'f'):
				self.board[self.y][self.x].toggleismarked()
			if self.haswon():
				self.retval = "You win!"
				return
				
			self.printboard()
			self.stdscr.addstr(self.y, self.x*2, '')
			self.stdscr.refresh()
		self.retval = "Goodbye"

	def lost(self):
		for i in self.board:
			for j in self.board[i]:
				if self.board[i][j].ismine:
					self.board[i][j].trigger()
		self.printboard()
		self.stdscr.refresh()
		time.sleep(5)

	def haswon(self):
		for i in self.board:
			for j in self.board[i]:
				if self.board[i][j].ismine and not self.board[i][j].ismarked:
					return False
				if self.board[i][j].ismarked and not self.board[i][j].ismine:
					return False
		return True

	def printboard(self):
		for i in self.board:
			line = ""
			for j in self.board[i]:
				char = self.board[i][j].getchar()
				color = 0
				if char in self.COLORS:
					color = self.COLORS[char]
				self.stdscr.addstr(i, j*2, char, curses.color_pair(color))

	def newboard(self, height, width, nummines):
		self.board = {}
		for i in range(0, height):
			self.board[i] = {}
			for j in range(0, width):
				self.board[i][j] = Square(i, j)

		rand = random.Random()

		for i in range(0, nummines):
			j = rand.randint(0, height - 1)
			k = rand.randint(0, width - 1)
			self.board[j][k].setmine(True)
		
		zeros = []

		for j in range(0, height):
			for k in range(0, width):
				for x in [-1, 0, 1]:
					for y in [-1, 0, 1]:
						if (x != 0 or y != 0) and (j + y) in self.board and (k + x) in self.board[j + y]:
							self.board[j][k].addneighbor(self.board[j + y][k + x])
				if not self.board[j][k].ismine and self.board[j][k].number == 0:
					zeros.append(self.board[j][k])

		zeros[rand.randint(0, len(zeros) - 1)].trigger()
				
		

if __name__ == '__main__':
	width = 30
	height = 20
	percentage = 16
	if len(sys.argv) > 1:
		if sys.argv[1] == '--help' or sys.argv[1] == '-h':
			print "Usage: " + sys.argv[0] + " [width[ height[ percentagemines]]]"
			sys.exit(0)
		width = int(sys.argv[1])
	if len(sys.argv) > 2:
		height = int(sys.argv[2])
	if len(sys.argv) > 3:
		percentage = int(sys.argv[3])

	game = mines(width, height, percentage)
