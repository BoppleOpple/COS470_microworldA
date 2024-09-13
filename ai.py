# NAME(S): Liam Hillery
#
# APPROACH: [WRITE AN OVERVIEW OF YOUR APPROACH HERE.]
#     Please use multiple lines (< ~80-100 char) for you approach write-up.
#     Keep it readable. In other words, don't write
#     the whole damned thing on one super long line.
#
#     In-code comments DO NOT count as a description of
#     of your approach.

import random
from aiDependancies.tile import Tile

directionCoordinates = {
    'N': ( 0, -1),
    'S': ( 0,  1),
    'W': (-1,  0),
    'E': ( 1,  0)
}

directionOpposites = {
    'N': 'S',
    'S': 'N',
    'E': 'W',
    'W': 'E'
}

class AI:
    def __init__(self):
        """
        Called once before the sim starts. You may use this function
        to initialize any data or data structures you need.
        """
        self.print = True

        self.turn = 0
        self.location = [0, 0]     # relative location of the agent, (x, y)
        self.memory = [[Tile()]]   # memory stored sideways relative to the world, (y, x)
        self.memoryOrigin = [0, 0] # coordinate of "top-left" tile in memory, (x, y)
        self.memorySize = [1, 1]   # bounds of memory, (x, y)

        self.nextActions = []

    def update(self, percepts):
        """
        PERCEPTS:
        Called each turn. Parameter "percepts" is a dictionary containing
        nine entries with the following keys: X, N, NE, E, SE, S, SW, W, NW.
        Each entry's value is a single character giving the contents of the
        map cell in that direction. X gives the contents of the cell the agent
        is in.

        COMAMND:
        This function must return one of the following commands as a string:
        N, E, S, W, U

        N moves the agent north on the map (i.e. up)
        E moves the agent east
        S moves the agent south
        W moves the agent west
        U uses/activates the contents of the cell if it is useable. For
        example, stairs (o, b, y, p) will not move the agent automatically
        to the corresponding hex. The agent must 'U' the cell once in it
        to be transported.

        The same goes for goal hexes (0, 1, 2, 3, 4, 5, 6, 7, 8, 9).
        """

        if percepts['X'][0] == 'r': return 'U'

        for direction, tiles in percepts.items():
            if direction == 'X': continue

            for i in range(len(tiles)):
                tileLocation = (
                    self.location[0] + (i+1)*directionCoordinates[direction][0],
                    self.location[1] + (i+1)*directionCoordinates[direction][1]
                )
                self.rememberTile(Tile(tileLocation[0], tileLocation[1], tiles[i]))
            
            if 'r' in tiles:
                self.nextActions = [direction for tile in tiles]
                self.nextActions[-1] = 'U'

        self.printMap()
        if self.print: print(self.location)

        if not self.nextActions:
            self.nextActions = self.findClosestUnknown()

        choice = self.nextActions.pop(0)

        self.move(directionCoordinates[choice])

        return choice

    def rememberTile(self, t: Tile = Tile()):
        while (t.relativePosition[0] < self.memoryOrigin[0]):
            for i in range(self.memorySize[1]): self.memory[i].insert(0, None)
            self.memorySize[0] += 1
            self.memoryOrigin[0] -= 1
        
        while (t.relativePosition[0] >= self.memoryOrigin[0] + self.memorySize[0]):
            for i in range(self.memorySize[1]): self.memory[i].append(None)
            self.memorySize[0] += 1

        while (t.relativePosition[1] < self.memoryOrigin[1]):
            self.memory.insert(0, [None for i in range(self.memorySize[0])])
            self.memorySize[1] += 1
            self.memoryOrigin[1] -= 1
        
        while (t.relativePosition[1] >= self.memoryOrigin[1] + self.memorySize[1]):
            self.memory.append([None for i in range(self.memorySize[0])])
            self.memorySize[1] += 1

        self.memory[t.relativePosition[1] - self.memoryOrigin[1]][t.relativePosition[0] - self.memoryOrigin[0]] = t

        for direction, offset in directionCoordinates.items():
            neighbor = self.tileAt(t.relativePosition[0] + offset[0], t.relativePosition[1] + offset[1])
            if neighbor:
                if directionOpposites[direction] in neighbor.unknowns: neighbor.unknowns.remove(directionOpposites[direction])
                if direction in t.unknowns: t.unknowns.remove(direction)
    
    def tileAt(self, x, y):
        if not (x in range(self.memoryOrigin[0], self.memoryOrigin[0]+self.memorySize[0]) and y in range(self.memoryOrigin[1], self.memoryOrigin[1]+self.memorySize[1])): return None
        return self.memory[y-self.memoryOrigin[1]][x-self.memoryOrigin[0]]
    
    def move(self, amount):
        tile = self.tileAt(self.location[0] + amount[0], self.location[1] + amount[1])
        if tile:
            if tile.type != 'w':
                self.location[0] += amount[0]
                self.location[1] += amount[1]
    
    # TODO use coords instead of tile objects
    def findClosestUnknown(self):
        tilesChecked = []
        tileFrontier = [([], self.tileAt(self.location[0], self.location[1]))]
        while tileFrontier:
            currentPath, currentTile = tileFrontier.pop(0)
            if currentTile.unknowns: return currentPath

            neighbors = [(list(''.join(currentPath) + direction), self.tileAt(currentTile.relativePosition[0] + offset[0], currentTile.relativePosition[1] + offset[1])) for direction, offset in sorted(directionCoordinates.items(), key=lambda e: random.random())]
            
            frontierAdditions = list(filter(lambda t: t[1] and t[1].type != 'w' and t[1].relativePosition not in tilesChecked, neighbors))
            tileFrontier.extend(frontierAdditions)
            tilesChecked.extend([addition[1].relativePosition for addition in frontierAdditions])
        return random.choice(['N', 'S', 'E', 'W'])

    def printMap(self):
        if self.print: 
            print("    | " + ' '.join([f"{i+self.memoryOrigin[0]:4}" for i in range(self.memorySize[0])]))
            print("----+-" + 5*self.memorySize[0]*'-')
            print('\n'.join([f"{i+self.memoryOrigin[1]:3d} | " +' '.join([f"{str(tile):>4}" for tile in self.memory[i]]) for i in range(self.memorySize[1])]))
            print("----+-" + 5*self.memorySize[0]*'-')
            print()