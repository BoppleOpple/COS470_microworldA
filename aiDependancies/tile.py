class Tile:
	def __init__(self, x=0, y=0, cellType='g'):
		self.relativePosition = (x, y)
		self.type = cellType
		self.unknowns = ['N', 'S', 'E', 'W']
	
	def __str__(self):
		return self.type