class Square:
	
	def __init__(self, y, x):
		self.ismarked = False
		self.x = x
		self.y = y
		self.ismine = False
		self.number = 0
		self.viewable = False
		self.neighbors = []

	def setmine(self, ismine):
		self.ismine = ismine

	def addmine(self):
		self.number = self.number + 1

	def getchar(self):
		if self.viewable:
			if self.ismine:
				return 'M'
			if self.number == 0:
				return ' '
			return str(self.number)
		if self.ismarked:
			return 'F'
		return '#'

	def addneighbor(self, neighbor):
		if neighbor.ismine:
			self.addmine()
		self.neighbors.append(neighbor)

	def trigger(self):
		if self.viewable:
			return False
		self.viewable = True
		if self.ismine:
			return True
		if self.number == 0:
			for n in self.neighbors:
				n.trigger()
		return False

	def toggleismarked(self):
		self.ismarked = not self.ismarked
