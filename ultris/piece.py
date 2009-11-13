class Piece:

	COLOR = 0
	CHAR = '&'

	x = 0
	y = 0
	squares = {}
	rotationindex = 0

	def __init__(self):
		pass

	def getsquares(self):
		return self.squares[self.rotationindex]

	def getwidth(self):
		maxwidth = 0
		for y in self.squares[self.rotationindex]:
			maxwidth = max(maxwidth, max(self.squares[self.rotationindex][y]))

		return maxwidth

	def wouldoverlappieceifmoved(self, piece, direction):
		squares = piece.getsquares()
		retval = False
		for y in squares:
			for x in squares[y]:
				if self.wouldoverlapifmoved(direction, piece.x + x, piece.y + y):
					retval = True
		return retval

	def wouldoverlappieceifdropped(self, piece):
		squares = piece.getsquares()
		retval = False
		for y in squares:
			for x in squares[y]:
				if self.wouldoverlapifdropped(piece.x + x, piece.y + y):
					retval = True
		return retval

	def wouldoverlappieceifturned(self, piece):
		squares = piece.getsquares()
		retval = False
		for y in squares:
			for x in squares[y]:
				if self.wouldoverlapifturned(piece.x + x, piece.y + y):
					retval = True
		return retval

	def wouldoverlapifmoved(self, direction, x, y):
		return (y - self.y) in self.squares[self.rotationindex] and (x - (self.x + direction)) in self.squares[self.rotationindex][y - self.y]

	def wouldoverlapifdropped(self, x, y):
		return (y - (self.y + 1)) in self.squares[self.rotationindex] and (x - self.x) in self.squares[self.rotationindex][y - (self.y + 1)]
	
	def overlaps(self, x, y):
		return (y - self.y) in self.squares[self.rotationindex] and (x - self.x) in self.squares[self.rotationindex][y - self.y]
	
	def wouldoverlapifturned(self, x, y):
		nextrotationindex = self.rotationindex + 1
		if nextrotationindex not in self.squares:
			nextrotationindex = 0
		return (y - self.y) in self.squares[nextrotationindex] and (x - self.x) in self.squares[nextrotationindex][y - self.y]

	def turn(self):
		self.rotationindex = self.rotationindex + 1
		if self.rotationindex not in self.squares:
			self.rotationindex = 0

	def istouching(self, x, y):
		return (y - self.y - 1) in self.squares[self.rotationindex] and (x - self.x) in self.squares[self.rotationindex][y - self.y - 1]

class SquarePiece (Piece):
	squares = { 0 : { 0 : { 0 : True, 1 : True }, 1 : { 0 : True, 1 : True } } }
	CHAR = '&'
	COLOR = 1

class TPiece (Piece):
	squares = { 0 : { 0 : { 0 : True, 1 : True, 2 : True }, 
			  1 : { 	  1 : True } },

		    1 : { 0 : { 	  1 : True }, 
			  1 : { 0 : True, 1 : True }, 
			  2 : { 	  1 : True } },

		    2 : { 0 : { 	  1 : True }, 
			  1 : { 0 : True, 1 : True, 2 : True } },
		    
		    3 : { 0 : { 0 : True }, 
			  1 : { 0 : True, 1 : True }, 
			  2 : { 0 : True } } }
	CHAR = '#'
	COLOR = 2

class LPiece (Piece):
	squares = { 0 : { 0 : { 0 : True, 1 : True, 2 : True },
		   	  1 : {	0 : True } },
		
		    1 : { 0 : { 0 : True, 1 : True },
			  1 : { 	  1 : True },
			  2 : { 	  1 : True } },
		   
		    2 : { 0 : { 		    2 : True },
			  1 : { 0 : True, 1 : True, 2 : True } },

		    3 : { 0 : { 0 : True },
			  1 : { 0 : True },
			  2 : { 0 : True, 1 : True } } }
	
	CHAR = '%'
	COLOR = 3

class LongPiece (Piece):
	squares = { 0 : { 0 : { 0 : True, 1 : True, 2 : True, 3 : True } },

		    1 : { 0 : { 1 : True },
			  1 : { 1 : True },
			  2 : { 1 : True },
			  3 : { 1 : True } } }
	
	CHAR = "="
	COLOR = 4

class ReverseLPiece (Piece):
	squares = { 0 : { 0 : { 0 : True },
			  1 : {	0 : True, 1 : True, 2 : True } },
		
		    1 : { 0 : { 0 : True, 1 : True },
			  1 : { 0 : True },
			  2 : { 0 : True } },
		   
		    2 : { 0 : { 0 : True, 1 : True, 2 : True },
			  1 : {                     2 : True } },

		    3 : { 0 : {           1 : True },
			  1 : {           1 : True },
			  2 : { 0 : True, 1 : True } } }
	
	CHAR = '@'
	COLOR = 5

class SPiece (Piece):
	squares = { 0 : { 0 : {           1 : True, 2 : True },
		          1 : { 0 : True, 1 : True } },

		    1 : { 0 : { 0 : True },
			  1 : { 0 : True, 1 : True },
			  2 : {           1 : True } } }
	
	CHAR = '#'
	COLOR = 6

class ReverseSPiece (Piece):
	squares = { 0 : { 0 : { 0 : True, 1 : True },
		          1 : {           1 : True, 2 : True } },

		    1 : { 0 : {           1 : True },
			  1 : { 0 : True, 1 : True },
			  2 : { 0 : True } } }
	
	CHAR = '$'
	COLOR = 7
