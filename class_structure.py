#!/usr/bin/python

##################################################
# To understand the design, it is recommended to #
#      read the class design document first!     #
##################################################

#This file contains a rough class outline for a roguelike to be built with
#libtcod or another graphical front-end.
#Focus for the class design is on game logic at the moment.
#Ideally we can couple the graphics/user interface as loosely as possible.
#
#I have tried to focus on the main aspects but the model should be able 
#to evolve over time. The idea is that it can be extended by inheritance,
#adding more specialised classes where needed.
#
#This file is written in python syntax and should compile, however there is no 
#sense in running it by itself. Also when we go for implementation I would
#propose to split up the file in multiple modules.
#
#For illustration purposes (and to experiment I admit :-p) I have already 
#added some class variables and functions. These are by no means permanent,
#consider it as examples ;-)
#
#All comments welcome!
#
# -Frost

import CONSTANTS

############# Classes related to User interface #################
class Application():
    """
    This class represents a running instance of the application.
    It connects the game logic to the user interface
    """

#If we implement our own graphical interface we will need to add 
#a class structure for it.
#Also to facilitate the use of an external library (like libtcod or
#pygame) we might need to add classes here.
#I haven't done this yet. Currently experimenting with libtcod to 
#see what would be needed.

############# Classes related to Game logic #################
class Game():
    """
    The game class contains the logic to run the game.
    It knows about turns
    It has pointers to all the other stuff, via the Game object you can drill 
    down to all components
    It can save and load
    It keeps track of the levels and knows which is the current level
    At the moment I don't see the need for sub classes 
    """

    #Class variables
    _application = None
    @property
    def application():
        """
        The Application object that owns this game Object
        """
        return self._application
        
    #Simple array to store Level objects
    _levels = []
    @property
    def levels(self):
        """
        Returns the list of levels in this game.
        """
        return self._levels
    _currentLevel = 0
    @property
    def currentLevel(self):
        """
        Returns the current level
        """
        return self.levels[self._currentLevel]
    
    #constructor
    def __init__(self, owner):
        """
        Constructor to create a new game.
        Arguments
            owner - Application object that owns this game
        """
        self._application = owner
        self.resetGame()
        
    #functions (not exhaustive)
    def resetGame(self):
        #clear existing levels
        self._levels = []
        #generate new level 
        myLevel = GeneratedLevel(self,1)
        self._levels.append(myLevel)
        return
    
    def loadGame(self):
        return
    
    def saveGame(self):
        return
    
class Utility():
    """
    Reusable utilities and logic go here
    At the moment I don't see the need for sub classes 
    """
    #examples
    # random number generator
    # rolling a hitdie
    # debug messages

 
##########
# LEVELS #
##########
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
    
    _characters = []
    @property
    def characters(self):
        """
        The characters on this level
        """
        return self._characters
    
    _items = []
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
        self._game = owner
        self._difficulty = difficulty
        
    #functions
        
        
class GeneratedLevel(Level):
    """
    Class representing a randomly generated level
    Specialised logic to generate a random map.
    We may have different flavors (algorithms of these
    """
    #constructor
    def __init__(self, owner, difficulty):
        """
        Constructor to create a new generated level.
        Arguments
            owner - Game object that owns this level
            difficulty - Difficulty of this level
        """
        #call constructor of super class
        super(GeneratedLevel,self).__init__(owner, difficulty)
        #generate the map
        self._map = Map(CONSTANTS.MAP_WIDTH,CONSTANTS.MAP_HEIGHT)

class TownLevel(Level):
    """
    Class representing a fixed town level
    Specalised class that uses a fixed map and fixed characters (for example 
    town vendors)
    """


#######
# MAP #
#######
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
    
    #Constants used to generate map
    ROOM_MAX_SIZE = 10
    ROOM_MIN_SIZE = 6
    MAX_ROOMS = 30

    def __init__(self, MapWidth, MapHeight):
        """
        Constructor to create a new map
        Arguments
            MapWidth - Map width in tiles
            MapHeight - Map height in tiles
        """
        #Create a big empty map
        self._tiles = [[ Tile(map,x,y)
               for y in range(MapHeight) ]
           for x in range(MapWidth) ]
        
        #Block the entire map
        #for y in range(MapHeight):
            #for x in range(MapWidth):
                #myTile = self.tiles[x][y]
                #myTile.blocked = True
                #myTile.blockSight = True
    
class Room():
    """
    Describes a rectangular section of a map
    """
    #Frost: TODO: clean up properties and comments of this class
    
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
 
    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)
 
    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

#classes could be added for corridors in case we want to place stuff in corridors?

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
        if isBlocked == True: self._block_sight = True
        
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
            
    def __init__(self, map, x, y):
        """
        Constructor to create a new tile, all tiles are created empty
        (unexplored, unblocked and not blocking line of sight)
        Arguments
            map - Map object of which this tile is a part
            x - x coordinate of the tile on the map
            y - y coordinate of the tile on the map
        """
        self._map = map
        self._x = x
        self._y = y
            
##############
# CHARACTERS #
##############
class Character(object):
    """
    Base class for characters that can move around and interact
    Should probably not be instatiated but describes the general interface of 
    a character
    Basic logic is in here, more specialised logic will be in the subclasses
    Every character has an AI that governs it
    Every character manages an inventory of items
    """

    #Class variables
    _inventoryItems = []
    @property
    def inventoryItems(self):
        """
        Returns a list of items representing this characters inventory.
        These are the unequiped items only.
        """
        return self._inventoryItems
    
    _equipedItems = []
    @property
    def equipedItems(self):
        """
        Returns a list of items that this characters has equiped.
        These are the equiped items only.
        """
        return self._equipedItems
        
    @property
    def allItems(self):
        """
        Returns a list of all items in this characters possession.
        Includes equiped and unequiped items.
        """
        return self._inventoryItems.append(self._equipedItems)
        
    _tile = None
    @property
    def tile(self):
        """
        Returns tile on which this character is located (might be None)
        """
        return self._tile
        
class Player(Character):
    """
    Sub class representing a player
    """

class NPC(Character):
    """
    Sub class representing a NPC, for example a vendor
    Probably we'll need to override some inventory concepts
    """

class Monster(Character):
    """
    Sub class representing a monster
    Later we can consider more specialised subclasses 
    for example Humanoid, Undead, Animal
    """
    
    #Class variables
    _flavorText = "Flavor text not set"
    @property
    def flavorText(self):
        """
        Fancy description of the monster.
        """
        return self._flavorText
 
    _killedByText = "Killed by text not set"
    @property
    def killedByText(self):
        """
        Killed by message that can be shown if this monster kills the player.
        """
        return self._killedByText
        
#########
# ITEMS #
#########
class Item(object):
    """
    Base class for items
    Should probably not be instatiated but describes the general interface of 
    an item
    """


class Equipment(Item):
    """
    Sub class for equipment = items that can be equiped
    Might need more subclasses for weapons versus armor
    """

class Consumable(Item):
    """
    Sub class for items that can be used.
    Not sure we might want a different class for scrolls and potions
    """

class QuestItem(Item):
    """
    Sub class for quest items
    Probably don't need this in the beginning but it would fit in here :)
    """

#############
# Libraries #
#############

class Library(object):
    """
    This class represents an interface towards a data store.
    """
    #Current draft implementation is based on a configParser
    
    #class variables
    _configParser = None
    @property
    def configParser(self):
        return self._configParser
    
    #constructor
    def __init__(self,myConfigParser):
        """
        Constructor to create a new library based on a config parser.
        Arguments
        config - an initialised config parser
        """
        self._configParser = myConfigParser
        
class MonsterLibrary(Library):
    """
    This class represents a library of monsters.
    Logic to create monsters goes here. It contains logic related to managing
    a population of monsters.
    """
    
    #class variables
    _uniqueMonsters = []
    @property
    def uniqueMonsters(self):
        """
        Returns a list of all created unique Monster objects
        """
        return self._uniqueMonsters
    
    _regularMonsters = []
    @property
    def regularMonsters(self):
        """
        Returns a list of all created regular Monster objects
        """
        return self._regularMonsters
    
    @property
    def monsters(self):
        """
        Returns a list of all created Monster objects
        """
        return self._regularMonsters.append(self._uniqueMonsters)
                
    def __init__(self,myConfigParser):
        """
        Constructor to create a new monster library
        Arguments
        config - an initialised config parser
        """
        #call super class constructor
        super(MonsterLibrary,self).__init__(myConfigParser)
    
    def createMonster(self,x,y,monster_key):
        """
        Function to build a new Monster.
        Arguments
            monster_key - string that identifies a monster in the config file.
        """
        # load the monster data from the config
        monster_data = dict(self.configParser.items(monster_key))
        
        #create the monster based on monster_data
        #TODO
        newMonster =None
        
        # register the monster
        self.regularMonsters.append(newMonster)
        return newMonster
        
######
# AI #
######
class AI(object):
    """
    Base class for AI logic
    Methods are empty, to be implemented by subclasses
    """
    
    def take_turn(self):
        """
        Take one turn
        """
        return

class PlayerAI(AI):
    """
    AI sub class that provides player control over characters
    """

class BasicMonsterAI(AI):
    """
    AI sub class that provides AI implementation for basic monsters.
    """
     #AI for a basic monster.
    def take_turn(self):
        #a basic monster takes its turn. if you can see it, it can see you
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
 
            #move towards player if far away
            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)
 
            #close enough, attack! (if the player is still alive.)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)

class ConfusedMonsterAI(AI):
    """
    AI sub class that provides AI implementation for confused monsters.
    """


if __name__ == '__main__':
    print("There is not much sense in running this file.")
