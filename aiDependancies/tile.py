tileCharacters = {
	'g': ' ',
	'w': 'xxxx',
	'r': ' :D '
}

class Tile:
	def __init__(self, x=0, y=0, cellType='g'):
		self.relativePosition = (x, y)
		self.type = cellType
		self.unknowns = ['N', 'S', 'E', 'W']
	
	def __str__(self):
		if self.type not in tileCharacters.keys(): return str(self.type)
		return tileCharacters[self.type]