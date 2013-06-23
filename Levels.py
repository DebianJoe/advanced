#!/usr/bin/python

import CONSTANTS
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
            
    #constructor
    def __init__(self, owner, difficulty):
        """
        Constructor to create a new level.
        Arguments
            owner - Game object that owns this level
            difficulty - Difficulty of this level
        """
        #initialize class variables (makes them unique to this instance)
        self._game = owner
        self._difficulty = difficulty
        self._portals = []
        self._characters = []
        self._items = []
        
class GeneratedLevel(Level):
    """
    Class representing a randomly generated level
    Specialised logic to generate a random map.
    We may have different flavors (algorithms of these
    """
    #constructor
    def __init__(self, owner, difficulty, previousLevel=None):
        """
        Constructor to create a new generated level.
        Arguments
            owner - Game object that owns this level
            difficulty - Difficulty of this level
            previousLevel (optional) - Level that comes before this one
            nextLevel (optional) - Level that comes after this one
        """
        #call constructor of super class
        super(GeneratedLevel,self).__init__(owner, difficulty)
        #generate the map
        self._map = Map(CONSTANTS.MAP_WIDTH,CONSTANTS.MAP_HEIGHT)
        #add some monsters
        self._placeMonsters()
    
    def addPortal(self, portal):
        self._addActor(portal)
        self.portals.append(portal)

    def addPlayer(self, player):
        self._addActor(player)
        self.characters.append(player)
            
    def _addActor(self, actor):
        emptyTile = None
        while emptyTile == None:
            #pick a random room
            aRoom = random.choice(self.map.rooms)
            #find an empty tile in the room
            emptyTile = aRoom.getRandomEmptyTile()
        #place the actor on the empty tile
        actor.moveTo(emptyTile)
            
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
                x = random.randrange(room.x1+1, room.x2-1)
                y = random.randrange(room.y1+1, room.y2-1)
                target_tile = self.map.tiles[x][y]
     
                #only place it if the tile is not blocked and empty
                if not target_tile.blocked and target_tile.empty:
                    
                    # get a random monster
                    new_monster = lib.getRandomMonster(self.difficulty)
                    new_monster.moveTo(target_tile)
                    
                    self.characters.append(new_monster)

class TownLevel(Level):
    """
    Class representing a fixed town level
    Specalised class that uses a fixed map and fixed characters (for example 
    town vendors)
    """
    #TODO
