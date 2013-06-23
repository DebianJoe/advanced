#!/usr/bin/python

#######################################################
# To understand the design, it is recommended to read #
# the class design documentation on the wiki first!   #
#######################################################

#This file is the main module for the game logic

#a rough class outline for a roguelike to be built with
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

#Chain load proprietary modules
import CONSTANTS
import Utilities
from Maps import *
from Levels import *
from Actors import *
from Libraries import *
from AI import *
from Effects import *

#Load system modules
import random

############# Classes related to User interface #################
class Application(object):
    """
    This class represents a running instance of the application.
    It connects the game logic to the user interface. It should be inherited
    by actual implementations of a graphical interface.
    """

#Frostlock:
#If we implement our own graphical interface we will probably need to add 
#a class structure for it as well.
#Also to facilitate the use of an external library (like libtcod or
#pygame) we might need to add classes here.
#I haven't done this yet. I'm currently experimenting with libtcod to 
#see what would be needed.
#In my case I have a "ApplicationLibtcod" class inheriting from this one.

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
        #reset Game
        self.resetGame()
        
    #functions
    def resetGame(self):
        #initialize monster library
        self._monsterLibrary = MonsterLibrary()

        #clear existing levels
        self._levels = []
        #generate new levels
        previousLevel = None
        for i in range(0,10):
            if i > 0: previousLevel = self.levels[i-1]
            currentLevel = GeneratedLevel(self,i+1) #difficulty > 0
            self._levels.append(currentLevel)
            if previousLevel != None:
                #add portal in previous level to current level
                downPortal = Portal(currentLevel)
                downPortal._char = '>'
                downPortal._name = 'The way down'
                previousLevel.addPortal(downPortal)
                #add portal in current level to previous level
                upPortal = Portal(previousLevel)
                upPortal._char = '<'
                upPortal._name = 'The way up'
                currentLevel.addPortal(upPortal)
        
        #Create player object
        player = Player()
        firstLevel = self.levels[0]
        firstLevel.addPlayer(player)
        
        return

    #TODO medium: implement saving and loading of gamestate
    def loadGame(self, fileName):
        return
    
    def saveGame(self, fileName):
        return
 
    def nextLevel(self):
        """
        Moves the game to the next level
        """
        if self._currentLevel < len(self.levels) - 1:
            self._currentLevel += 1
    
    def previousLevel(self):
        """
        Moves the game to the previous level
        """
        if self._currentLevel > 0:
            self._currentLevel -= 1        
            
if __name__ == '__main__':
    print("There is not much sense in running this file.")
    print("Try running ApplicationLibtcod.")
