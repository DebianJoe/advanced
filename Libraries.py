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
        newMonster._name = monster_key
        #Character components
        newMonster._baseDefense = int(monster_data['defense'])
        newMonster._basePower = int(monster_data['power'])
        newMonster._xpValue = int(monster_data['xp'])
        newMonster._AI = AI.BasicMonsterAI(newMonster)
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
        #TODO: read these chances at creation time of the library, no
        #sense in doing it again for every monster

        #chance of each monster
        monster_chances = {}
        for monster_name in self.configParser.get('lists', 'monster list').split(', '):
            chance_table = json.loads(self.configParser.get(monster_name, 'chance'))
            monster_chances[monster_name] = Utilities.from_dungeon_level(chance_table, difficulty)

        #Avoid recreating unique monsters
        for unique_monster in self.uniqueMonsters:
            del monster_chances[unique_monster.id]

        #create a random monster
        choice = Utilities.random_choice(monster_chances)
        monster = self.createMonster(choice)
        return monster
