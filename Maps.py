#!/usr/bin/python

import random


class Map():
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

    _rooms = None

    @property
    def rooms(self):
        """
        List of the rooms in this map.
        """
        return self._rooms

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

    #constructor
    def __init__(self, MapWidth, MapHeight):
        """
        Constructor to create a new empty map
        Arguments
            MapWidth - Map width in tiles
            MapHeight - Map height in tiles
        """
        #Create a big empty map
        self._tiles = [[Tile(map, x, y)
            for y in range(MapHeight)]
            for x in range(MapWidth)]
        self.generateMap()

    #functions
    def generateMap(self):
        """
        generate a random map
        """

        #Constants used to generate map
        ROOM_MAX_SIZE = 10
        ROOM_MIN_SIZE = 6
        MAX_ROOMS = 30

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
        self._rooms = []
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
            for other_room in self.rooms:
                if new_room.intersect(other_room):
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
            self._rooms.append(new_room)
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

    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

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
        if isBlocked is True:
            self._block_sight = True

    _block_sight = False

    @property
    def blockSight(self):
        """
        Returns a boolean indicating if this tile blocks line of sight.
        """
        return self._blocked

    @blockSight.setter
    def blockSight(self, blocksLineOfSight):
        self._blockSight = blocksLineOfSight

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
