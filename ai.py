# NAME(S): Liam Hillery
#
# APPROACH:
# |--------------------------------------------------------------------------------|
# While I considered doing more for this project, I decided against it because I
# didn't want to make my life harder for future projects by building off of a more
# convoluted algorithm than necessary. My thoughts at the beginning of this project
# were that I needed:
#   a.) Several states for the agent depending on its current goal
#   b.) Some method of remembering places the agent had already seen
#   c.) Some way to move from one place to another if the agent knows a path between
#       them
#
# My original intention was to use two states: one in which the agent searched for
# the goal and one in which it moved there once it know where the goal was. It would
# use a linked implementation of a graph to store the map, and use Dijkstra's
# algorithm to move between tiles. For the most part, this implementation didnt
# change, but there were a few important issues with my original plan that led me to
# this solution.
#
# Most notably of these changes, I added a state. This current algorithm has three
# modes, though it can switch between these modes in the middle of a cycle:
#   1.) Follow a path, no questions asked
#   2.) Find a path to somewhere new
#   3.) Find a path to the goal
# This change only really affected one thing, and that is that the agent would
# always follow its plan, unless it saw a path to the end. The flow of the program
# now looks something like:
#                                   +--------+------------------------+
#                                   |        |                        |
#                                   v        |                        |
# Find a path to somewhere new -> Follow that path ---+---> Find a path to the goal
#             ^                                       |
#             |                                       |
#             +---------------------------------------+
#
# Similarly, when finding a path, the program first had to know where the
# destination was before it could use Dijkstra's, so it had to run some traversal
# anyway. Once I realised that, I just used breadth-first search to find the
# shortest path, since this application is quite small. (this is what prompted the
# addition of the path-following phase)
# 
# Finally, instead of using a graph, I stored the map in a 2-dimensional list, since
# all of the tiles had to be accessed with coordinates anyway, so they would have to
# be indexable with vectors somehow. Also, the map is always rectangular, so its
# worst-case memory size would be equivalent or nearly equivalent. (plus it was much
# easier to render in terminal for debugging, for a small performance hit)

import random
from aiDependancies.tile import Tile

# define how cardinal directions are oriented in the agent's map
directionCoordinates = {
    'N': ( 0, -1),
    'S': ( 0,  1),
    'W': (-1,  0),
    'E': ( 1,  0)
}

# define opposite directions, since it's cheap and easy
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

        # for debugging
        self.print = False

        self.turn = 0
        self.location = [0, 0]     # relative location of the agent, (x, y)
        self.memory = [[Tile()]]   # memory stored sideways relative to the world, (y, x)
        self.memoryOrigin = [0, 0] # coordinate of "top-left" tile in memory, (x, y)
        self.memorySize = [1, 1]   # bounds of memory, (x, y)

        # remember the current "plan" to avoid recalculating paths
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

        # if the agent ever reaches the finish, use it no matter what
        if percepts['X'][0] == 'r': return 'U'
        
        # for each percept
        for direction, tiles in percepts.items():

            # (except X)
            if direction == 'X': continue

            # add the tile to memory
            for i in range(len(tiles)):
                tileLocation = (
                    self.location[0] + (i+1)*directionCoordinates[direction][0],
                    self.location[1] + (i+1)*directionCoordinates[direction][1]
                )
                self.rememberTile(Tile(tileLocation[0], tileLocation[1], tiles[i]))
            
            # and plan a path to the finish if it is spotted
            if 'r' in tiles:
                self.nextActions = [direction for tile in tiles]
                self.nextActions[-1] = 'U'

        # print the current state of memory, if enabled
        self.printMap()
        if self.print: print(self.location)

        # if there is no plan, make one
        if not self.nextActions:
            # by finding the closest unknown tile
            self.nextActions = self.findClosestUnknown()

        # perform the first action in the plan
        choice = self.nextActions.pop(0)
        self.move(directionCoordinates[choice])
        return choice

    # function to handle expanding memory to accomidate new information, if necessary
    def rememberTile(self, t: Tile = Tile()):
        # if the tile is "left" of memory
        while (t.relativePosition[0] < self.memoryOrigin[0]):
            for i in range(self.memorySize[1]): self.memory[i].insert(0, None)
            self.memorySize[0] += 1
            self.memoryOrigin[0] -= 1
        
        # if the tile is "right" of memory
        while (t.relativePosition[0] >= self.memoryOrigin[0] + self.memorySize[0]):
            for i in range(self.memorySize[1]): self.memory[i].append(None)
            self.memorySize[0] += 1

        # if the tile is "above" memory
        while (t.relativePosition[1] < self.memoryOrigin[1]):
            self.memory.insert(0, [None for i in range(self.memorySize[0])])
            self.memorySize[1] += 1
            self.memoryOrigin[1] -= 1
        
        # if the tile is "below" memory
        while (t.relativePosition[1] >= self.memoryOrigin[1] + self.memorySize[1]):
            self.memory.append([None for i in range(self.memorySize[0])])
            self.memorySize[1] += 1

        # once expanded, store the tile data
        self.memory[t.relativePosition[1] - self.memoryOrigin[1]][t.relativePosition[0] - self.memoryOrigin[0]] = t

        # register which directions of the tile are known and which are not
        for direction, offset in directionCoordinates.items():
            neighbor = self.tileAt(t.relativePosition[0] + offset[0], t.relativePosition[1] + offset[1])
            if neighbor:
                if directionOpposites[direction] in neighbor.unknowns: neighbor.unknowns.remove(directionOpposites[direction])
                if direction in t.unknowns: t.unknowns.remove(direction)
    
    # since memory is not indexed with coordinates, just make a function to avoid mistakes
    def tileAt(self, x, y):
        if not (x in range(self.memoryOrigin[0], self.memoryOrigin[0]+self.memorySize[0]) and y in range(self.memoryOrigin[1], self.memoryOrigin[1]+self.memorySize[1])): return None
        return self.memory[y-self.memoryOrigin[1]][x-self.memoryOrigin[0]]
    
    
    def move(self, amount):
        tile = self.tileAt(self.location[0] + amount[0], self.location[1] + amount[1])

        # if the agent doesn't hit a wall when trying to move, update its position
        if tile:
            if tile.type != 'w':
                self.location[0] += amount[0]
                self.location[1] += amount[1]
    
    # find the closest tile with at least one unknown neighbor, using bft
    def findClosestUnknown(self):
        # store the coordinates of "seen" tiles
        tilesChecked = [self.location]

        # store the visitable tiles alongside the path taken to reach them
        tileFrontier = [([], self.tileAt(self.location[0], self.location[1]))]

        # while there are still unsearched tiles
        while tileFrontier:
            # remove a tile
            currentPath, currentTile = tileFrontier.pop(0)

            # move to it if it has an unknown neighbor
            if currentTile.unknowns: return currentPath

            # add unseen neighbors to the frontier if not
            neighbors = []

            # for each direction (in a random order because determinism is less fun)
            for direction, offset in sorted(directionCoordinates.items(), key=lambda e: random.random()):
                # add the neighbor in that direction, alongside the updated path to it
                # this neighbor will always be known, since the function would have already returned otherwise
                neighbors.append([
                    currentPath + [direction],
                    self.tileAt(currentTile.relativePosition[0] + offset[0], currentTile.relativePosition[1] + offset[1])
                ])
            
            # now, select only those neighbors which are not already in the frontier and aren't walls
            frontierAdditions = list(filter(lambda t: t[1] and t[1].type != 'w' and t[1].relativePosition not in tilesChecked, neighbors))

            # and add those to the list of seen tiles and the list of visitable tiles
            tileFrontier.extend(frontierAdditions)
            tilesChecked.extend([addition[1].relativePosition for addition in frontierAdditions])
        
        # if nothing is found, walk randomly (this should never happen if the map is completeable)
        return random.choice(['N', 'S', 'E', 'W'])

    def printMap(self):
        # print the current map knowledge using some unreadaable list manipulation (sorry)
        if self.print: 
            print("    | " + ' '.join([f"{i+self.memoryOrigin[0]:4}" for i in range(self.memorySize[0])]))
            print("----+-" + 5*self.memorySize[0]*'-')
            print('\n'.join([f"{i+self.memoryOrigin[1]:3d} | " +' '.join([f"{str(tile) if tile else "  ? ":>4}" for tile in self.memory[i]]) for i in range(self.memorySize[1])]))
            print("----+-" + 5*self.memorySize[0]*'-')
            print()