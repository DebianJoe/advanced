#!/usr/bin/python

import random
import Utilities
import CONSTANTS
import math


class Map(object):
    """
    Describes the 2D layout of a level
    Contains logic to calculate distance, intersection, field of view, ...
    """
    _tiles = None

    @property
    def tiles(self):
        """
        Returns the tiles that make up this map.
        """
        return self._tiles

    _areas = None

    @property
    def areas(self):
        """
        List of rectangular sub areas on this map.
        """
        return self._areas

    @property
    def width(self):
        """
        Returns an integer indicating the width of the map
        """
        if self._tiles:
            return len(self._tiles)
        else:
            return 0

    @property
    def height(self):
        """
        Returns an integer indicating the height of the map
        """
        if self._tiles:
            return len(self._tiles[0])
        else:
            return 0

    @property
    def each_map_position(self):
        """
        Returns a 2D list that can be used to iterate over each map tile
        x/y position:

            for x, y in each_map_position():
                pass
        """

        return [(x, y) for x in range(self.width) for y in range(self.height)]

    @property
    def explored_tiles(self):
        """
        Returns a list of all tiles explored.
        This includes tiles in and out of the visible range.
        """

        # this flattens the 2D tiles list into one list, filtered out.
        return [t for sublist in self.tiles for t in sublist if t.explored]

    #Every map has a Tile object which contains the entry point
    _entryTile = None

    @property
    def entryTile(self):
        """
        Returns Tile on which entry is located
        """
        return self._entryTile

    #Every map has a Tile object which contains the entry point
    _exitTile = None

    @property
    def exitTile(self):
        """
        Returns Tile on which exit is located
        """
        return self._exitTile

    _rangeOfView = 10

    @property
    def rangeOfView(self):
        """
        Range of view used to determine field of view on this map.
        """
        return self._rangeOfView

    #constructor
    def __init__(self, MapWidth, MapHeight):
        """
        Constructor to create a new empty map
        Arguments
            MapWidth - Map width in tiles
            MapHeight - Map height in tiles
        """
        #Initialize range of view
        self._rangeOfView = CONSTANTS.TORCH_RADIUS
        #Create a big empty map
        self._tiles = [[Tile(map, x, y)
            for y in range(MapHeight)]
            for x in range(MapWidth)]
        self.generateMap()
        self.refreshBlockedTileMatrix()

    #functions
    def generateMap(self):
        """
        Place holder function, subclass must provide actual implementation.
        """
        raise GameError("Can't use Map class directly, use a subclass!")

    def refreshBlockedTileMatrix(self):
        """
        Refresh a 2D matrix of 1's and 0'1 that indicate if a Tile position
        blocks line of sight.

        We could have looped over each tile and check this
        for each player movement, but this way is neater and more efficient.
        """

        self.solidTileMatrix = Utilities.make_matrix(self.width, self.height, 0)
        for x, y in self.each_map_position:
            self.solidTileMatrix[x][y] = self.tiles[x][y].blockSight

    def updateFieldOfView(self, x, y):
        """
        Update the map tiles with what is in field of view, marking
        those as explored.
        """
        view_range = self.rangeOfView
        for tx, ty in self.each_map_position:
            tile = self.tiles[tx][ty]
            dist = Utilities.distanceBetweenPoints(x, y, tx, ty)
            visible = dist <= view_range
            line_of_sight = Utilities.line_of_sight(
                self.solidTileMatrix, x, y, tx, ty)
            if visible and line_of_sight:
                tile.inView = True
                tile.explored = True
            else:
                self.tiles[tx][ty].inView = False
            # set all actors as in view too
            for actor in tile.actors:
                actor.inView = visible and line_of_sight

    def getRandomEmptyTile(self):
        """
        Returns an empty tile on this level, excluding the outermost cells.
        """
        levelArea = Room(self, 1, 1, self.width - 2, self.height - 2)
        return levelArea.getRandomEmptyTile()

    def getCircleTiles(self, x, y, radius, fullCircle=False, excludeBlockedTiles=False):
        """
        Frost: This utility function returns an array of tiles that 
        approximates a circle on the map.
        Arguments
            x - the x coordinate of the center of the circle
            y - the y coordinate of the center of the circle
            radius - the radius of the circle
            fullCircle - when false only the tiles on the border of the 
                circle are returned, when true all tiles inside.
            excludeBlockedTiles - excludes blocked tiles
        """
        #prepare variables
        circleTiles = []
        maxX = self.width - 1
        maxY = self.height - 1
        #maxI is a relevant sample size, if it is to small it will lead to gaps in the circle.
        #the following works for reasonably sized circles.
        maxI = 6 * radius
        halfMaxI = maxI / 2
        if fullCircle:
            #add center
            circleTiles.append(self.tiles[x][y])
        #go around the edge of the circle in maxI samples
        for i in range(0, maxI):
            #for each edge sample calculate the coordinates
            xPos = int(round(x + radius * math.cos((math.pi/halfMaxI)*i)))
            yPos = int(round(y + radius * math.sin((math.pi/halfMaxI)*i)))
            #add relevant tiles between the found circle edge and the circle center
            while xPos <> x or yPos <> y:
                #tile has to be on the map
                if xPos >= 0 and yPos >= 0 and xPos <= maxX and yPos <= maxY:
                    #avoid adding duplicates
                    if self.tiles[xPos][yPos] not in circleTiles:
                        possibleTile = self.tiles[xPos][yPos]
                        if excludeBlockedTiles:
                            #exclude blocked tiles
                            if not possibleTile.blocked:
                                circleTiles.append(possibleTile)
                        else:
                            #include all tiles
                            circleTiles.append(possibleTile)
                if fullCircle:
                    #move towards interior
                    if xPos > x:
                        xPos -= 1
                    elif xPos < x:
                        xPos += 1
                    elif xPos == x:
                        if yPos > y:
                            yPos -= 1
                        elif yPos < y:
                            yPos += 1
                else:
                    #adding only the edge is enough
                    break        
        #return the found tiles that make up the circle   
        return circleTiles
    
    def __str__(self):
        """
        Basic way to print out a map, can be used to debug.
        """
        output = ''
        for y in range(0, self.height):
            line = ''
            for x in range(0, self.width):
                if self.tiles[x][y].blocked:
                    line = line + 'x'
                else:
                    line = line + ' '
            output += line + '\n'
        return output


class DungeonMap(Map):
    """
    This class represents a randomized dungeon map.
    """
    @property
    def rooms(self):
        """
        Returns the rooms of this dungeon map.
        Note that this property is actually just a rename of the base class
        "areas" property.
        """
        return self._areas

    def clearRooms(self):
        """
        Clears the list of houses.
        """
        self._areas = []

    def __init__(self, MapWidth, MapHeight):
        """
        Constructor to create a new dungeon map
        Arguments
            MapWidth - Map width in tiles
            MapHeight - Map height in tiles
        """
        super(DungeonMap, self).__init__(MapWidth, MapHeight)
        #Initialize range of view
        self._rangeOfView = CONSTANTS.TORCH_RADIUS

    def generateMap(self):
        """
        generate a randomized dungeon map
        """
        #clear existing rooms
        self.clearRooms()

        #Constants used to generate map
        ROOM_MAX_SIZE = CONSTANTS.DUNGEON_ROOM_MAX_SIZE
        ROOM_MIN_SIZE = CONSTANTS.DUNGEON_ROOM_MIN_SIZE
        MAX_ROOMS = CONSTANTS.DUNGEON_MAX_ROOMS

        #Create a new map with empty tiles
        self._tiles = [[Tile(self, x, y)
               for y in range(self. height)]
           for x in range(self. width)]

        #Block all tiles
        for y in range(self.height):
            for x in range(self.width):
                myTile = self.tiles[x][y]
                myTile.blocked = True
                myTile.blockSight = True

        #cut out rooms
        num_rooms = 0
        for r in range(MAX_ROOMS):
            #random width and height
            w = random.randrange(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            h = random.randrange(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            #random position without going out of the boundaries of the map
            x = random.randrange(0, self.width - w - 1)
            y = random.randrange(0, self.height - h - 1)
            #create a new room
            new_room = Room(self, x, y, w, h)

            #abort if room intersects with existing room
            intersects = False
            for other_room in self.rooms:
                if new_room.intersect(other_room):
                    intersects = True
                    break
            if intersects is True:
                break

            #cut it out of the map
            #go through the tiles in the room and make them passable
            for x in range(new_room.x1 + 1, new_room.x2):
                for y in range(new_room.y1 + 1, new_room.y2):
                    self.tiles[x][y].blocked = False
                    self.tiles[x][y].blockSight = False

            (new_x, new_y) = new_room.center

            #create corridor towards previous room
            if num_rooms > 0:
                #all rooms after the first: connect to the previous room

                #center coordinates of previous room
                (prev_x, prev_y) = self.rooms[num_rooms - 1].center

                #create a corridor
                if random.randrange(0, 1) == 1:
                    #first move vertically, then horizontally
                    self._createVerticalTunnel(prev_x, new_x, prev_y)
                    self._createHorizontalTunnel(prev_y, new_y, new_x)
                else:
                    #first move horizontally, then vertically
                    self._createHorizontalTunnel(prev_x, new_x, new_y)
                    self._createVerticalTunnel(prev_y, new_y, prev_x)

            #finally, append the new room to the list
            self.rooms.append(new_room)
            num_rooms += 1

        #Set entry and exit tiles
        (entryX, entryY) = self.rooms[0].center
        self._entryTile = self._tiles[entryX][entryY]
        (exitX, exitY) = self.rooms[len(self.rooms) - 1].center
        self._exitTile = self._tiles[exitX][exitY]

    def _createHorizontalTunnel(self, x1, x2, y):
        #horizontal tunnel. min() and max() are used in case x1>x2
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].blockSight = False

    def _createVerticalTunnel(self, y1, y2, x):
        #vertical tunnel
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].blockSight = False

    def getRandomEmptyTile(self):
        """
        finds a random empty tile on the map of this level
        """
        emptyTile = None
        while emptyTile is None:
            #pick a random room of the map
            room = random.choice(self.rooms)
            #find an empty tile in the room
            emptyTile = room.getRandomEmptyTile()
        return emptyTile


class TownMap(Map):
    """
    This class represents a randomized town map.
    """
    @property
    def houses(self):
        """
        The list of houses in this town.
        Note that this property is actually just a rename of the base class
        "areas" property.
        """
        return self._areas

    def clearHouses(self):
        """
        Clears the list of houses.
        """
        self._areas = []

    def __init__(self, MapWidth, MapHeight):
        """
        Constructor to create a new town map
        Arguments
            MapWidth - Map width in tiles
            MapHeight - Map height in tiles
        """
        super(TownMap, self).__init__(MapWidth, MapHeight)
        #Initialize range of view
        self._rangeOfView = CONSTANTS.TOWN_RADIUS

    def generateMap(self):
        """
        Generate a randomized town map
        """
        #clear existing houses
        self.clearHouses()

        #Constants used to generate map
        HOUSE_MAX_SIZE = CONSTANTS.TOWN_HOUSE_MAX_SIZE
        HOUSE_MIN_SIZE = CONSTANTS.TOWN_HOUSE_MIN_SIZE
        MAX_HOUSES = CONSTANTS.TOWN_MAX_HOUSES

        #Create a new map with empty tiles
        self._tiles = [[Tile(self, x, y)
               for y in range(self. height)]
           for x in range(self. width)]

        #Block only the town border
        for y in range(self.height):
            for x in range(self.width):
                myTile = self.tiles[x][y]
                myTile.explored = True
                if x == 0 or y == 0 \
                        or x == self.width - 1 or y == self.height - 1:
                    myTile.blocked = True
                    myTile.blockSight = True
                else:
                    myTile.blocked = False
                    myTile.blockSight = False

        #generate houses
        num_houses = 0
        for r in range(MAX_HOUSES):
            #random width and height
            w = random.randrange(HOUSE_MIN_SIZE, HOUSE_MAX_SIZE)
            h = random.randrange(HOUSE_MIN_SIZE, HOUSE_MAX_SIZE)
            #random position staying away from the edges of town
            x = random.randrange(2, self.width - w - 2)
            y = random.randrange(2, self.height - h - 2)
            #create a new house
            new_house = Room(self, x, y, w, h)

            #abort if house intersects with existing house
            #border distance ensures there are free tiles between houses
            intersects = False
            for other_house in self.houses:
                if new_house.intersect(other_house, border=2):
                    intersects = True
                    break
            if intersects is True:
                break

            #create the outline of the house on the map
            for x in range(new_house.x1, new_house.x2 + 1):
                for y in range(new_house.y1, new_house.y2 + 1):
                    self.tiles[x][y].blocked = True
                    self.tiles[x][y].blockSight = True

            #finally, append the new room to the list
            self.houses.append(new_house)
            num_houses += 1


class SingleRoomMap(Map):
    """
    This class represents a very simple map with only one room.
    It can for example be used to represent the interior of a house.
    """
    _room = None

    @property
    def room(self):
        """
        Returns the room of this single room map.
        """
        return self._room

    def __init__(self, MapWidth, MapHeight, myRoom):
        """
        Constructor to create a new empty map
        Arguments
            MapWidth - Map width in tiles
            MapHeight - Map height in tiles
        """
        #Register room
        self._room = myRoom
        super(SingleRoomMap, self).__init__(MapWidth, MapHeight)
        #Initialize range of view
        self._rangeOfView = CONSTANTS.TORCH_RADIUS

    def generateMap(self):
        #Create a new map with empty tiles
        self._tiles = [[Tile(self, x, y)
               for y in range(self. height)]
           for x in range(self. width)]

        #Block all tiles
        for y in range(self.height):
            for x in range(self.width):
                myTile = self.tiles[x][y]
                myTile.blocked = True
                myTile.blockSight = True

        #Cut out the single room
        for x in range(self.room.x1, self.room.x2 + 1):
            for y in range(self.room.y1, self.room.y2 + 1):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].blockSight = False


class Room():
    """
    Describes a rectangular room on the map
    """
    #TODO EASY: clean up properties and provide comments for this class
    #could use some additional properties as well maybe.
    def __init__(self, map, x, y, w, h):
        self._map = map
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    @property
    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)

    def intersect(self, other, border=0):
        """
        Returns true if this room intersects with another one
        arguments
            other - another room
            border - optional parameter to include a border distance between
                     both rooms
        """
        return (self.x1 - border <= other.x2 and self.x2 + border >= other.x1
                and
                self.y1 - border <= other.y2 and self.y2 + border >= other.y1)

    def getRandomEmptyTile(self):
        aTile = None
        xRange = range(self.x1, self.x2 + 1)
        random.shuffle(xRange)
        yRange = range(self.y1, self.y2 + 1)
        random.shuffle(yRange)
        for x in xRange:
            for y in yRange:
                if not self._map.tiles[x][y].blocked and self._map.tiles[x][y].empty:
                    aTile = self._map.tiles[x][y]
        return aTile


class Tile():
    """
    represents a Tile on the map
    """

    _x = 0

    @property
    def x(self):
        """
        Returns x coordinate of tile relevant to map
        """
        return self._x

    _y = 0

    @property
    def y(self):
        """
        Returns y coordinate of tile relevant to map
        """
        return self._y

    _map = None

    @property
    def map(self):
        """
        Returns the map on which this tile is located
        """
        return self._map

    _explored = False

    @property
    def explored(self):
        """
        Returns a boolean indicating if this tile has been explored.
        """
        return self._explored

    @explored.setter
    def explored(self, isExplored):
        self._explored = isExplored

    _blocked = False

    @property
    def blocked(self):
        """
        Returns a boolean indicating if this tile is blocked.
        """
        return self._blocked

    @blocked.setter
    def blocked(self, isBlocked):
        self._blocked = isBlocked
        #Blocked tiles also block line of sight
        # NOTE: not neccesarily, this is how windows and fences are made :)
        # Lol, good point, and we need shrubberies! :)
        if isBlocked is True:
            self._block_sight = True

    _block_sight = False

    @property
    def blockSight(self):
        """
        Returns a boolean indicating if this tile blocks line of sight.
        """
        return self._block_sight

    @blockSight.setter
    def blockSight(self, blocksLineOfSight):
        self._blockSight = blocksLineOfSight

    _in_view = True

    @property
    def inView(self):
        """
        Returns if this tile is in the player field of vision.
        This is set by the game engine during each turn.
        """

        return self._in_view

    _actors = []

    @property
    def actors(self):
        """
        Returns actors on this tile.
        """
        return self._actors

    @property
    def empty(self):
        """
        Returns a boolean indicating if this tile is empty
        """
        if len(self.actors) == 0:
            return True
        return False

    def __init__(self, map, x, y):
        """
        Constructor to create a new tile, all tiles are created empty
        (unexplored, unblocked and not blocking line of sight)
        Arguments
            map - Map object of which this tile is a part
            x - x coordinate of the tile on the map
            y - y coordinate of the tile on the map
        """
        self._actors = []
        self._map = map
        self._x = x
        self._y = y

    def __str__(self):
        """
        Overrides object standard string representation.
        This enables str(thisTile).
        """
        return '(' + str(self.x) + ',' + str(self.y) + ')'

    def addActor(self, myActor):
        """
        This function adds and actor to this tile
        """
        self._actors.append(myActor)

    def removeActor(self, myActor):
        """
        This function adds and actor to this tile
        """
        self._actors.remove(myActor)
