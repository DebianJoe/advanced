#!/usr/bin/python

#from Maps import Tile

import random
import Utilities

##########
# ACTORS #
##########
class Actor(object):
    """
    Base class for everything that can occur in the gameworld.
    Example sub classes: Items and Characters.
    """
    #Frostlock: I'm not completely happy with the name Actor but haven't
    # found anything better yet :-)
    # Also I added hitpoints on this level, every Actor can be destroyed,
    # including items and portals.

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

    _baseMaxHitPoints = 0
    @property
    def maxHitPoints(self):
        """
        Maximum hitpoints of this Character (overrides Actor)
        """
        bonus = 0
        #TODO medium:
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

    #Constructor
    def __init__(self):
        """
        Creates a new basic Actor, normally not used directly but should
        be called by subclasses.
        """
        #initialize class variables (makes them unique to this instance)
        self._baseMaxHitPoints = 1
        self._char = '?'
        self._currentHitPoints = 1
        self._id = 'not set'
        self._name = 'Nameless'
        self._tile = None

    #functions
    def __str__(self):
        return self._name + " " + super(Actor,self).__str__()

    def moveTo(self, targetTile):
        """
        moves this actor to the targetTile
        """
        if self.tile != None:
            self.tile.removeActor(self)
        self._tile = targetTile
        targetTile.addActor(self)


class Portal(Actor):
    """
    This class can be used to represent portals in and out of a level
    """

    _destination = None
    @property
    def destination(self):
        """
        The level where this portal leads to
        """
        return self._destination

    def __init__(self, destination):
        """
        Constructor to create a new portal
        """
        super(Portal,self).__init__()
        self._destination = destination

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
        #include power bonuses of equipped items
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
        #include defense bonuses of equipped items
        #bonus = sum(equipment.defense_bonus for equipment in get_all_equipped(self.owner))
        return self._baseDefense + bonus

    _AI = None
    @property
    def AI(self):
        """
        Return AI associated to this character.
        """
        return self._AI

    #Constructor
    def __init__(self):
        """
        Creates a new character object, normally not used directly but called
        by sub class constructors.
        """
        #call super class constructor
        super(Character,self).__init__()
        #initialize class variables
        self._baseDefense = 0
        self._basePower = 1
        self._equipedItems = []
        self._inventoryItems = []
        self._xpValue = 0
        self._AI = None

    #Functions
    def attack(self, target):
        """
        Attack another Character
        Arguments
            target - the Character to be attacked
        """
        #a simple formula for attack damage
        damage = self.power - target.defense

        if damage > 0:
            Utilities.message(self.name.capitalize() + ' attacks '
                    + target.name + ' for ' + str(damage) + ' Damage.')
            target.takeDamage(damage,self)
        else:
            Utilities.message(self.name.capitalize() + ' attacks '
                    + target.name + ' but it has no effect!')

    def takeDamage(self, amount, attacker):
        """
        function to take damage from an attacker
        arguments
           damage - the incoming damage
           attacker - the attacking Actor
        """
        #apply damage if possible
        if amount > 0:
            self.currentHitPoints -= amount
            Utilities.message(self.name.capitalize() + ' looses '
                    + str(amount) + ' hitpoints (current: '
                    + str(self.currentHitPoints) + ').')

            #TODO
            #check for death. if there's a death function, call it
            #if self.hp <= 0:
             #   function = self.death_function
              #  if function is not None:
               #     function(self.owner,attacker)

    def takeHeal(self, amount, attacker):
        """
        function to heal a given amount of hitpoints
        arguments
           amount - the number of hitpoints to heal
        """
        #heal by the given amount
        if amount > 0:
            self.currentHitPoints += amount
            Utilities.message(self.name.capitalize() + ' gains '
                    + str(amount) + ' hitpoints (current: '
                    + str(self.currentHitPoints) + ').')

    def takeTurn(self):
        """
        Function to make this Character take one turn.
        """
        if self.AI is not None:
            self.AI.takeTurn()
        else:
            print 'No AI available for ' + str(self)

class Player(Character):
    """
    Sub class representing a player
    """
    #class variables

    _xp = 0
    @property
    def xp():
        """
        Returns the current xp of the player.
        """
    _level = 0
    @property
    def level():
        """
        Returns the current level of the player.
        """

    #constructor
    def __init__(self):
        """
        Creates and initializes new player object. Note that the object is not
        linked to a game tile. It should be moved to the tile after creation.
        """
        #call super class constructor
        super(Player,self).__init__()

        #initialize all variables
        #Actor components
        self._id = 'player'
        self._char = '@'
        self._baseMaxHitPoints = 100
        self._currentHitPoints = 100
        self._name = random.choice(('Joe','Wesley','Frost'))
        #Character components
        self._baseDefense = 2
        self._basePower = 2
        self._xpValue = 0
        #Player components
        self._xp = 0
        self._level = 1

        #TODO: missing logic here
        #death_function=globals().get(monster_data['death_function'], None))
        ##death_function=monster_data['death_function'])
        #ai_class = globals().get(monster_data['ai_component'])
        ##ai_component=monster_data['ai_component']
        ## and this instanstiates it if not None
        #ai_component = ai_class and ai_class() or None

    #functions
    def gainXp(self,amount):
        """
        Increase xp of this player with the given amount
        arguments
            amount - integer
        """
        self._xp += amount
        #TODO:
        #Check for level up

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
        #call super class constructor
        #(ensure instance gets unique copies of class variables)
        super(Monster,self).__init__()

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
