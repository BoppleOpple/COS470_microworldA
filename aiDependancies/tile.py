# corresponding strings for rendering tiles
tileCharacters = {
	'g': ' ',
	'w': 'xxxx',
	'r': ' :D '
}

class Tile:
	def __init__(self, x=0, y=0, cellType='g'):
		self.relativePosition = (x, y)       # position in the agent's coordinate system
		self.type = cellType                 # character corresponding to the cell type
		self.unknowns = ['N', 'S', 'E', 'W'] # list of which directions are known and which are not
	
	# again, just some code for terminal output
	def __str__(self):
		if self.type not in tileCharacters.keys(): return str(self.type)
		return tileCharacters[self.type]