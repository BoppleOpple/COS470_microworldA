class Tile:
	def __init__(self, x=0, y=0, cellType='g'):
		self.relativePosition = (x, y)
		self.type = cellType
	
	def __str__(self):
		return self.type