#!/usr/bin/python

import CONSTANTS
import Utilities
from Actors import Portal
from Maps import *


class Level(object):
    """
    Class representing one level.
    This is the generic version containing the shared logic that is inherited
    by the sub classes
    """

    #class variables
    _game = None

    @property
    def game(self):
        """
        The game that owns this level.
        """
        return self._game

    _name = None

    @property
    def name(self):
        """
        The name of the level.
        """
        return self._name

    _difficulty = 0

    @property
    def difficulty(self):
        """
        The difficulty of this level.
        """
        return self._difficulty

    _map = None

    @property
    def map(self):
        """
        The map of this level
        """
        return self._map

    _portals = None

    @property
    def portals(self):
        """
        The portals on this level
        """
        return self._portals

    _characters = None

    @property
    def characters(self):
        """
        The characters on this level
        """
        return self._characters

    _items = None

    @property
    def items(self):
        """
        The items on this level
        """
        return self._items

    _subLevels = []

    @property
    def subLevels(self):
        """
        Returns the list of sub levels in this level
        """
        return self._subLevels

    #constructor
    def __init__(self, owner, difficulty, name):
        """
        Constructor to create a new level.
        Arguments
            owner - Game object that owns this level
            difficulty - Difficulty of this level
            name - a textual name for this level
        """
        #initialize class variables (makes them unique to this instance)
        self._game = owner
        self._difficulty = difficulty
        self._name = name
        self._portals = []
        self._characters = []
        self._items = []
        self._subLevels = []

    def removeActor(self, myActor):
        """
        Remove the provided actor from this level.
        arguments
            myActor - the actor that should be removed
        """
        for c in self.characters:
            if c is myActor:
                self.characters.remove(c)
        for i in self.items:
            if i is myActor:
                self.items.remove(i)

    def addPortal(self, portal):
        """
        Register the given portal to this level.
        """
        self.portals.append(portal)

    def addCharacter(self, character):
        """
        Register the given character to this level.
        """
        self.characters.append(character)

    def addItem(self, item):
        """
        Register the given item to this level.
        """
        self.items.append(item)

    def getRandomEmptyTile(self):
        """
        Returns a randomly selected empty tile on this level.
        """
        if self.map is None:
            return None
        return self.map.getRandomEmptyTile()


class DungeonLevel(Level):
    """
    Class representing a randomly generated dungeon level.
    """
    #constructor
    def __init__(self, owner, difficulty, name):
        """
        Constructor to create a new generated level.
        Arguments
            owner - Game object that owns this level
            difficulty - Difficulty of this level
            name - a textual name for this level
        """
        #call constructor of super class
        super(DungeonLevel, self).__init__(owner, difficulty, name)
        #generate the map
        self._map = DungeonMap(CONSTANTS.MAP_WIDTH, CONSTANTS.MAP_HEIGHT)
        #add some monsters
        self._placeMonsters()

    def _placeMonsters(self):
        """
        This function will place monsters on this level depending on the
        difficulty level and using the MonsterLibrary in the Game
        """
        #Grab the MonsterLibrary
        lib = self.game.monsterLibrary
        #max number of monsters per room
        max_monsters = lib.getMaxMonstersPerRoomForDifficulty(self.difficulty)

        #generate monsters for every room
        for room in self.map.rooms:
            #choose random number of monsters to create
            num_monsters = random.randrange(0, max_monsters)
            for i in range(num_monsters):
                #choose random spot for new monster
                x = random.randrange(room.x1 + 1, room.x2 - 1)
                y = random.randrange(room.y1 + 1, room.y2 - 1)
                target_tile = self.map.tiles[x][y]

                #only place it if the tile is not blocked and empty
                if not target_tile.blocked and target_tile.empty:

                    # get a random monster
                    new_monster = lib.getRandomMonster(self.difficulty)
                    new_monster.moveToLevel(self, target_tile)


class TownLevel(Level):
    """
    Class representing a randomly generated town level.
    """

    #constructor
    def __init__(self, owner, difficulty, name):
        """
        Constructor to create a new generated level.
        Arguments
            owner - Game object that owns this level
            difficulty - Difficulty of this level
            name - a textual name for this level
        """
        #call constructor of super class
        super(TownLevel, self).__init__(owner, difficulty, name)
        #generate the map
        self._map = TownMap(CONSTANTS.MAP_WIDTH, CONSTANTS.MAP_HEIGHT)
        #generate sublevels for the houses
        for house in self.map.houses:
            self.generateHouseInterior(house)

    def generateHouseInterior(self, house):
        """
        This function will create a sublevel to represent the house interior.
        arguments
            house - one of the house areas on the town map
        """
        #consider all the possible locations for a door
        doorLocations = [(x, y)
                for x in range(house.x1 + 1, house.x2 - 1)
                for y in [house.y1, house.y2]]
        doorLocations = doorLocations + [(x, y)
                for x in [house.x1, house.x2]
                for y in range(house.y1 + 1, house.y2 - 1)]
        #Select actual location randomly
        doorX, doorY = random.choice(doorLocations)
        doorTile = self.map.tiles[doorX][doorY]
        #Cut a hole in the wall for the door
        doorTile.blocked = False
        doorTile.blockSight = False
        #Create the door that leads into the house
        doorIn = Portal()
        doorIn._char = '>'
        doorIn._name = 'door'
        doorIn._message = 'You enter the house.'
        doorIn.moveToLevel(self, doorTile)
        #Generate the level that represents the interior of the house
        houseLevel = SingleRoomLevel(self.game, self.difficulty, 'house', house)
        self.subLevels.append(houseLevel)
        doorTile = houseLevel.map.tiles[doorX][doorY]
        #Create the door that leads out of the house
        doorOut = Portal()
        doorOut._char = '<'
        doorOut._name = 'door'
        doorOut._message = 'You leave the house.'
        doorOut.moveToLevel(houseLevel, doorTile)
        #Connect the two doors
        doorIn.connectTo(doorOut)


class SingleRoomLevel(Level):
    """
    This class implements a level with only one room.
    It can for example be used to represent the interior of a house
    arguments
        area - the area that represents the room
    """
    def __init__(self, owner, difficulty, name, area):
        #call constructor of super class
        super(SingleRoomLevel, self).__init__(owner, difficulty, name)
        #generate the map
        self._map = SingleRoomMap(CONSTANTS.MAP_WIDTH, CONSTANTS.MAP_HEIGHT, area)
