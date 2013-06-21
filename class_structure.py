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

#Load custom modules
import CONSTANTS
import Utility

#Load system modules
import random
import ConfigParser

import json #used to load tables from strings

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
    
    _monsterLibrary = None
    @property
    def monsterLibrary(self):
        """
        Returns the monster library used by this game.
        """
        return self._monsterLibrary
        
    #constructor
    def __init__(self, owner):
        """
        Constructor to create a new game.
        Arguments
            owner - Application object that owns this game
        """
        self._application = owner
        
        #initialize monster library
        config = ConfigParser.ConfigParser()
        config.read(CONSTANTS.MONSTER_CONFIG)
        self._monsterLibrary = MonsterLibrary(config)
        #reset Game
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
        #add some monsters
        self.placeMonsters()
    
    def placeMonsters(self):
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
        self._tiles = [[ Tile(map,x,y)
            for y in range(MapHeight) ]
            for x in range(MapWidth) ]
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
        self._tiles = [[ Tile(self,x,y)
               for y in range(self.height) ]
           for x in range(self.width) ]
        
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
            new_room = Room(x, y, w, h)

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
 
            (new_x, new_y) = new_room.center()
            
            #create corridor towards previous room
            if num_rooms > 0:
                #all rooms after the first: connect to the previous room
 
                #center coordinates of previous room
                (prev_x, prev_y) = self.rooms[num_rooms-1].center()
 
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
    
    _actor = None
    @property
    def actor(self):
        """
        Returns actor on this tile (can be None).
        """
        return self._actor
    @actor.setter
    def actor(self, myActor):
        self._actor = myActor
    
    @property
    def empty(self):
        """
        Returns a boolean indicating if this tile is empty
        """
        if self._actor == None: return True
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
        self._map = map
        self._x = x
        self._y = y

##########
# ACTORS #
##########
class Actor(object):
    """
    Base class for everything that can occur in the gameworld.
    Example sub classes: Items and Characters.
    """
    
    #class variables
    _id = "ID not set"
    @property
    def id(self):
        """
        ID code for this Actor
        """
        return self._id

    _name = "Name not set"
    @property
    def name(self):
        """
        Name of this Actor
        """
        return self._name
            
    _baseMaxHitPoints = 0
    @property
    def maxHitPoints(self):
        """
        Maximum hitpoints of this Actor
        """  
        bonus = 0
        #TODO
        #return actual max_hp, by summing up the bonuses from all equipped items
        #bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
        return self._baseMaxHitPoints + bonus

    _currentHitPoints = 0
    @property
    def currentHitPoints(self):
        """
        The current amount of hitpoints
        """
        return self._currentHitPoints
    @currentHitPoints.setter
    def currentHitPoints(self, hitPoints):
        if hitPoints > self.maxHitPoints:
            self._currentHitPoints = self.maxHitPoints
        else:
            self._currentHitPoints = hitPoints
    
    _char = None
    @property
    def char(self):
        """
        Returns a 1 char shorthand for this actor.
        """
        return self._char
    
    _tile = None
    @property
    def tile(self):
        """
        Returns the Tile on which this Actor is located. Can be None.
        """
        return self._tile
                
    #Constructor
    def __init__(self):
        """
        Creates a new basic Actor, normally not used
        """
        raise NotImplementedError( "Should not instatiate a base Actor object" )
        
    #functions
    def __str__(self):
        return self._name + " " + super(Actor,self).__str__()
    
    def moveTo(self, targetTile):
        """
        moves this actor to the targetTile
        """
        self._tile = targetTile
        targetTile.actor = self
                
##############
# CHARACTERS #
##############
class Character(Actor):
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
    
    _xpValue = 0
    @property
    def xpValue(self):
        """
        Return xp value
        """
        return self._xpValue
        
    _basePower = 0
    @property
    def power(self):
        """
        Return attack power
        """
        bonus = 0
        #TODO
        #return actual power, by summing up the bonuses from all equipped items
        #bonus = sum(equipment.power_bonus for equipment in get_all_equipped(self.owner))
        return self._basePower + bonus
 
    _baseDefense = 0
    @property
    def defense(self):  
        """
        Return defense value
        """
        bonus = 0
        #TODO
        #return actual defense, by summing up the bonuses from all equipped items
        #bonus = sum(equipment.defense_bonus for equipment in get_all_equipped(self.owner))
        return self.base_defense + bonus
  
    #Constructor
    #TODO
    
    #Functions
    def attack(self, target):
        #a simple formula for attack damage
        damage = self.power - target.fighter.defense
 
        if damage > 0:
            #make the target take some damage
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
            target.fighter.take_damage(damage,self)
        else:
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')
 
    def take_damage(self, damage, attacker):
        global killerrabbit_death, wearing_amulet
        # are we immune from rabbits?
        if attacker.owner.name == 'killerrabbit' and wearing_amulet:
            message('The Amulet of the Flying Circus protects you!')
            return
        #apply damage if possible
        if damage > 0:
            self.hp -= damage
 
            #check for death. if there's a death function, call it
            if self.hp <= 0:
                function = self.death_function
                if function is not None:
                    function(self.owner,attacker)
 
    def heal(self, amount):
        #heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

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
    
    #constructor
    def __init__(self):
        """
        Creates a new uninitialized Monster object.
        Use MonsterLibrary.createMonster() to create an initialized Monster.
        """
        pass
        
#########
# ITEMS #
#########
class Item(Actor):
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
    
    def createMonster(self,monster_key):
        """
        Function to create and initialize a new Monster.
        Arguments
            monster_key - string that identifies a monster in the config file.
        """
        # load the monster data from the config
        monster_data = dict(self.configParser.items(monster_key))
        
        # do not create multiple unique monsters
        if monster_data['unique'] == 'True':
            unique_ids = []
            for unique_monster in self.uniques:
                unique_ids.append(unique_monster.id)
            if monster_key in unique_ids:
                #This unique was already created, do nothing
                return None
        
        #create the monster based on monster_data
        newMonster = Monster()
        
        #initialize all variables
        #Actor components
        newMonster._id = monster_key
        newMonster._char = monster_data['char']
        newMonster._baseMaxHitPoints = \
                Utility.roll_hit_die(monster_data['hitdie'])
        newMonster._currentHitPoints=newMonster._baseMaxHitPoints
        newMonster._name = monster_key
        #Character components    
        newMonster._baseDefense = defense=int(monster_data['defense'])
        newMonster._basePower = int(monster_data['power'])
        newMonster._xpValue = int(monster_data['xp'])
        #Monster components
        newMonster._flavorText = monster_data['flavor']
        newMonster._killedByText = monster_data['killed_by']

        #TODO: missing logic here
        #Actor._tile
        #death_function=globals().get(monster_data['death_function'], None))
        ##death_function=monster_data['death_function'])
        #ai_class = globals().get(monster_data['ai_component'])
        ##ai_component=monster_data['ai_component']
        ## and this instanstiates it if not None
        #ai_component = ai_class and ai_class() or None
        
        # register the monster
        if monster_data['unique'] == 'True':
            self.uniqueMonsters.append(newMonster)
        else:
            self.regularMonsters.append(newMonster)
        return newMonster
    
    def getMaxMonstersPerRoomForDifficulty(self, difficulty):
        #maximum number of monsters per room
        max_monsters = Utility.from_dungeon_level(
                json.loads(self.configParser.get('lists', 'max monsters')),
                difficulty)
        return max_monsters

    def getRandomMonster(self, difficulty):
        #TODO: read these chances at creation time of the library
        #chance of each monster
        monster_chances = {}
        for monster_name in self.configParser.get('lists', 'monster list').split(', '):
            chance_table = json.loads(self.configParser.get(monster_name, 'chance'))
            monster_chances[monster_name] = Utility.from_dungeon_level(chance_table,difficulty)

        #create a random monster
        choice = Utility.random_choice(monster_chances)
        monster = self.createMonster(choice)
        return monster            
       
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

####################
# Inventory system #
####################
#TODO

######################
# Magic/Event system #
######################
class Effect(object):
    """
    Base class for more specialized events, melee or magic effects.
    """
    
    #class variables
    _id = "ID not set"
    @property
    def id(self):
        """
        ID code for this Effect
        """
        return self._id

class MagicEffect(Effect):
    """
    Base class for magic effects.
    """
    #current thinking is that this class can both represent targeted as area
    #of effect spells.


#########################
# Game log for messages #
#########################
#TODO

    

if __name__ == '__main__':
    print("There is not much sense in running this file.")
    import test_application
    test_application.launch()
