#!/usr/bin/python

import curses
import time
import sys
import math
import piece
import random

class Ultris:

	width =  10
	height = 30
	level = 1
	numlines = 0
	pieces = []
	nextpieces = []
	delay = 0.8
	grid = {}
	score = 0
	paused = True
	lost = False

	PERCENTAGE = 0.8

	def __init__(self, numpieces, level, width, height):
		for i in range(0, numpieces):
			self.pieces.append(self.newpiece())
			self.pieces[i].x = 4 * (1 - i) 
			self.nextpieces.append(self.newpiece())
		self.level = level
		self.width = width
		self.height = height
		for y in range(0, self.height):
			self.grid[y] = {}
			for x in range(0, self.width):
				self.grid[y][x] = None
		self.delay = math.pow(self.delay, level)
		self.level = level
		curses.wrapper(self.newgame)
		print "Lines: " + str(self.numlines) + ", Score: " + str(self.score)

	def newgame(self, stdscr):
		self.stdscr = stdscr
		self.gamewin = self.stdscr.subwin(self.height + 1, self.width * 2 + 2, 0, 0)
		curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_RED)
		curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLUE)
		curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)
		curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_GREEN)
		curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_CYAN)
		curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
		curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)
		self.stdscr.nodelay(True)
		key = None
		self.clock = time.clock()
		self.draw()
		while key != ord('q') and not self.lost:
			key = None
			key = stdscr.getch()
			if key == ord('p'):
				self.togglepause()
			
			if key == ord('j') or key == curses.KEY_LEFT:
				self.move(self.pieces[0], -1)
			if key == ord('l') or key == curses.KEY_RIGHT:
				self.move(self.pieces[0], 1)
			if key == ord('k') or key == curses.KEY_DOWN:
				self.steppiece(0)
			if key == ord('i') or key == curses.KEY_UP:
				self.turn(self.pieces[0])

			if key == ord('a') and len(self.pieces) > 1:
				self.move(self.pieces[1], -1)
			if key == ord('d') and len(self.pieces) > 1:
				self.move(self.pieces[1], 1)
			if key == ord('s') and len(self.pieces) > 1:
				self.steppiece(1)
			if key == ord('w') and len(self.pieces) > 1:
				self.turn(self.pieces[1])
			
			if not self.paused and time.clock() > self.clock + self.delay:
				self.clock = time.clock()
				self.step()
	
	def togglepause(self):
		self.paused = not self.paused
		self.draw()

	def turn(self, piece):
		canturn = True
		for y in self.grid:
			if piece.wouldoverlapifturned(-1, y):
				canturn = False
			if piece.wouldoverlapifturned(self.width, y):
				canturn = False
			for x in self.grid[y]:
				if self.grid[y][x] and piece.wouldoverlapifturned(x, y):
					canturn  = False

		for otherpiece in self.pieces:
			if otherpiece != piece and piece.wouldoverlappieceifturned(otherpiece):
				canturn = False

		if canturn:
			piece.turn()
			self.draw()


	def move(self, piece, direction):
		canmove = True
		for y in self.grid:
			if piece.wouldoverlapifmoved(direction, -1, y):
				canmove = False
			if piece.wouldoverlapifmoved(direction, self.width, y):
				canmove = False
			for x in self.grid[y]:
				if self.grid[y][x] and piece.wouldoverlapifmoved(direction, x, y):
					canmove = False
		for otherpiece in self.pieces:
			if otherpiece != piece and piece.wouldoverlappieceifmoved(otherpiece, direction):
				canmove = False

		if canmove:
			piece.x = piece.x + direction
			self.draw()

	def newpiece(self):
		rand = random.Random()
		i = rand.randint(0, 6)
		if i == 0:
			return piece.SquarePiece()
		if i == 1:
			return piece.TPiece()
		if i == 2:
			return piece.LPiece()
		if i == 3:
			return piece.ReverseLPiece()
		if i == 4:
			return piece.LongPiece()
		if i == 5:
			return piece.SPiece()
		if i == 6:
			return piece.ReverseSPiece()


	def step(self):
		for piece in range(0, len(self.pieces)):
			self.steppiece(piece)
		self.checklose()

	def checklose(self):
		for piece in self.pieces:
			for y in self.grid:
				for x in self.grid[y]:
					if self.grid[y][x] and piece.overlaps(x, y):
						self.lost = True

	def steppiece(self, i):
		piece = self.pieces[i]
		saved = False
		for y in self.grid:
			for x in self.grid[y]:
				if not saved and self.grid[y][x] and piece.wouldoverlapifdropped(x, y):
					self.savepiece(piece)
					saved = True

		for x in range(0, self.width):
			if not saved and piece.wouldoverlapifdropped(x, self.height - 1):
				self.savepiece(piece)
				saved = True

		if saved:
			self.pieces[i] = self.nextpieces.pop(0)
			self.pieces[i].x = 4 * (1 - i)
			self.nextpieces.append(self.newpiece())
		else:
			dropable = True
			for otherpiece in self.pieces:
				if otherpiece != piece and piece.wouldoverlappieceifdropped(otherpiece):
					dropable = False	

			if dropable:
				piece.y = piece.y + 1

		self.draw()


	def savepiece(self, piece):
		rand = random.Random()
		self.score = self.score + rand.randint(0, self.level * 100)
		squares = piece.getsquares()
		for y in squares:
			for x in squares[y]:
				self.grid[piece.y + y][piece.x + x] = (piece.CHAR, piece.COLOR)

		self.checklines()

	def checklines(self):
		lines = []
		for y in self.grid:
			linedone = True
			for x in self.grid[y]:
				if self.grid[y][x] is None:
					linedone = False
			if linedone:
				lines.append(y)

		for y in lines:
			for y2 in range(y - 1, 0, -1):
				for x in self.grid[y2]:
					self.grid[y2 + 1][x] = self.grid[y2][x]

			for x in self.grid[0]:
				self.grid[0][x] = None
			
			self.numlines = self.numlines + 1
			if self.numlines % 10 == 0:
				self.level = self.level + 1
				self.delay = self.delay * self.PERCENTAGE
		self.draw()


	def draw(self):
		self.stdscr.erase()
		self.gamewin.border()
		if self.paused:
			self.gamewin.addstr(1, 1, "Paused.")
			self.gamewin.addstr(2, 1, "Press p.")
		else:
			i = 0
			for piece in self.pieces:
				squares = piece.getsquares()
				CHAR = piece.CHAR
				if len(self.pieces) > 1:
					if i == 0:
						CHAR = ">"
					else:
						CHAR = "<"
				for y in squares:
					for x in squares[y]:
						self.gamewin.addstr(piece.y + y + 1, (piece.x + x) * 2 + 1, CHAR + CHAR, curses.color_pair(piece.COLOR))
				i = i + 1

			for y in self.grid:
				for x in self.grid[y]:
					if self.grid[y][x]:
						(CHAR, color) = self.grid[y][x]
						self.gamewin.addstr(y + 1, x * 2 + 1, CHAR + CHAR, curses.color_pair(color))
		
		self.stdscr.addstr(0, self.width * 2 + 2, "Next:")
		i = 1
		for piece in self.nextpieces:
			squares = piece.getsquares()
			for y in squares:
				for x in squares[y]:
					self.stdscr.addstr(i + y, self.width * 2 + 2 + x * 2, piece.CHAR + piece.CHAR, curses.color_pair(piece.COLOR))
			i = i + y + 1

		self.stdscr.addstr(i, self.width * 2 + 2, "Lines: " + str(self.numlines))
		self.stdscr.addstr(i + 1, self.width * 2 + 2, "Level: " + str(self.level))
		self.stdscr.addstr(i + 2, self.width * 2 + 2, "Score: " + str(self.score))

		self.gamewin.refresh()


if __name__ == '__main__':
	numpieces = 1
	level = 1
	width = 10
	height = 30
	if len(sys.argv) > 1:
		if sys.argv[1] == '-h' or sys.argv[1] == '--help':
			print "Usage " + sys.argv[0] + " [numpieces[ startlevel[ width[ height]]]]"
			exit(0)
		numpieces = min(max(int(sys.argv[1]), 1), 2)
	if len(sys.argv) > 2:
		level = int(sys.argv[2])
	if len(sys.argv) > 3:
		width = int(sys.argv[3])
	if len(sys.argv) > 4:
		height = int(sys.argv[4])
	
	ultris = Ultris(numpieces, level, width, height)
