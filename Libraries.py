#!/usr/bin/python

import CONSTANTS
import Utilities
from Actors import *
import AI

#library/config file implementation
import ConfigParser  # used for config file implementation
import json  # used to load structured data like tables from strings


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
    def __init__(self, myConfigParser):
        """
        Constructor to create a new library based on a config parser.
        Arguments
            config - an initialised config parser
        """
        #initialize class variables
        self._configParser = myConfigParser


class MonsterLibrary(Library):
    """
    This class represents a library of monsters.
    Logic to create monsters goes here. It contains logic related to managing
    a population of monsters.
    """

    #class variables

    _monsterChances = {}

    @property
    def monsterChances(self):
        """
        Returns the chance table for monster occurrences.
        """
        return self._monsterChances

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
        return self._uniqueMonsters.append(self._regularMonsters)

    def __init__(self):
        """
        Constructor to create a new monster library
        """
        #initialize configParser
        config = ConfigParser.ConfigParser()
        config.read(CONSTANTS.MONSTER_CONFIG)
        #call super class constructor
        super(MonsterLibrary, self).__init__(config)
        #initialize class variables
        self._uniqueMonsters = []
        self._regularMonsters = []
        self._monsterChances = {}
        for monster_name in self.configParser.get('lists', 'monster list').split(', '):
            chance_table = json.loads(self.configParser.get(monster_name, 'chance'))
            self._monsterChances[monster_name] = chance_table



    def createMonster(self, monster_key):
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
            for unique_monster in self.uniqueMonsters:
                unique_ids.append(unique_monster.id)
            if monster_key in unique_ids:
                #This unique was already created, do nothing
                raise Utilities.GameError('Unique monster' + monster_key + ' already exists.')

        #create the monster based on monster_data
        newMonster = Monster()

        #initialize all variables
        #Actor components
        newMonster._id = monster_key
        newMonster._char = monster_data['char']
        newMonster._baseMaxHitPoints = \
                Utilities.roll_hit_die(monster_data['hitdie'])
        newMonster._currentHitPoints = newMonster._baseMaxHitPoints
        newMonster._name = monster_data['name']
        #Character components

        newMonster._baseDefense = int(monster_data['defense'])
        newMonster._basePower = int(monster_data['power'])
        newMonster._xpValue = int(monster_data['xp'])
        #gets a class object by name; and instanstiate it if not None
        ai_class = eval('AI.' + monster_data['ai'])
        newMonster._AI = ai_class and ai_class(newMonster) or None

        #Monster components
        newMonster._flavorText = monster_data['flavor']
        newMonster._killedByText = monster_data['killed_by']

        # register the monster
        if monster_data['unique'] == 'True':
            self.uniqueMonsters.append(newMonster)
        else:
            self.regularMonsters.append(newMonster)
        return newMonster

    def getMaxMonstersPerRoomForDifficulty(self, difficulty):
        #maximum number of monsters per room
        max_monsters = Utilities.from_dungeon_level(
                json.loads(self.configParser.get('lists', 'max monsters')),
                difficulty)
        return max_monsters

    def getRandomMonster(self, difficulty):
        #Avoid recreating unique monsters
        for unique_monster in self.uniqueMonsters:
            del monster_chances[unique_monster.id]

        #create a random monster
        choice = Utilities.random_choice(self.monsterChances, difficulty)
        monster = self.createMonster(choice)
        return monster


class ItemLibrary(Library):
    """
    This class represents a library of items. Logic to create items is
    implemented in this class.
    """

    _itemChances = {}

    @property
    def itemChances(self):
        """
        Returns the chance table for item occurrences.
        """
        return self._itemChances

    _items = []

    @property
    def items(self):
        """
        Returns a list of the items that this library has created.
        """
        return self._items

    def __init__(self):
        """
        Constructor to create a new item library
        """
        #initialize configParser
        config = ConfigParser.ConfigParser()
        config.read(CONSTANTS.MONSTER_CONFIG)
        #call super class constructor
        super(ItemLibrary, self).__init__(config)
        #initialize class variables
        self._items = []
        self._itemChances = {}
        for item_name in self.configParser.get('lists', 'item list').split(', '):
            chance_table = json.loads(self.configParser.get(item_name, 'chance'))
            self._itemChances[item_name] = chance_table

    def createItem(self, item_key):
        """
        Function to create and initialize a new Item.
        Arguments
            item_key - string that identifies an item in the config file.
        """
        # load the item data from the config
        item_data = dict(self.configParser.items(item_key))
        item_data["key"] = item_key

        #create the correct type of item
        item_class = eval(item_data['type'])
        newItem = item_class and item_class(item_data) or None

        if newItem is None:
            raise Utilities.GameError('Failed to create item type ' + item_data['type'])

        #initialize all variables

        # register the new item
        self.items.append(newItem)
        return newItem

    def getMaxItemsPerRoomForDifficulty(self, difficulty):
        #maximum number of items per room
        max_items = Utilities.from_dungeon_level(
                json.loads(self.configParser.get('lists', 'max items')),
                difficulty)
        return max_items

    def getRandomItem(self, difficulty):
        #create a random item
        choice = Utilities.random_choice(self.itemChances, difficulty)
        item = self.createItem(choice)
        return item
