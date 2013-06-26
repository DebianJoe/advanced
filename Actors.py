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
    @tile.setter
    def tile(self, targetTile):
        """
        Moves this actor to the targetTile.
        """
        if self._tile is not None:
            self._tile.removeActor(self)
        self._tile = targetTile
        targetTile.addActor(self)


    _level = None
    @property
    def level(self):
        """
        Returns level on which this Actor is located. Can be None.
        """
        return self._level
    @level.setter
    def level(self, targetLevel):
        """
        Moves this actor to the targetLevel
        """
        if self._level is not None:
            self.level.removeActor(self)
        self._level = targetLevel

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

    _inView = False

    @property
    def inView(self):
        """
        This actor is in view of the player.
        """
        
        return self._inView

    @inView.setter
    def inView(self, visible):
        
        self._inView = visible

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
        self._level = None

    #functions
    def __str__(self):
        return self._name + " " + super(Actor,self).__str__()

    def moveToTile(self, targetTile):
        """
        moves this actor to the targetTile on the current level
        """
        if not targetTile.blocked:
            self.tile = targetTile

    def moveToLevel(self, targetLevel, targetTile):
        """
        moves this actor to the targetTile on the targetLevel
        """
        self.moveToTile(targetTile)
        self.level = targetLevel

    def moveAlongVector(self, vx, vy):
        """
        moves this actor on the current map according to the specified vector
        """
        #only works if we are on a map
        if self.tile is not None:
            targetX = self.tile.x + vx
            targetY = self.tile.y + vy
            #avoid out of bounds
            Utilities.clamp(targetX, 0, self.tile.map.width)
            Utilities.clamp(targetY, 0, self.tile.map.height)
            #move
            self.moveToTile(self.level.map.tiles[targetX][targetY])

    def moveTowards(self, targetActor):
        """
        Moves this actor towards the provided actor.
        arguments
            actor - the target Actor object
        """
        #vector towards the target
        dx = targetActor.tile.x - self.tile.x
        dy = targetActor.tile.y - self.tile.y
        #distance towards the target
        distance = Utilities.distanceBetween(self, targetActor)
        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        #move along the vector
        self.moveAlongVector(dx, dy)

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

    ACTIVE = 0
    DEAD = 1
    _state = ACTIVE
    @property
    def state(self):
        """
        Returns this characters state
        """
        return self._state

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
        self._state = Character.ACTIVE

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
        #check for death
        if self.currentHitPoints < 0:
            self._killedBy(attacker)

    def _killedBy(self, attacker):
        """
        This function handles the death of this Character
        """
        Utilities.message(attacker.name + ' kills ' + self.name, "KILL")
        #yield experience to the attacker
        if type(attacker) is Player:
            attacker.gainXp(self.xpValue)
            Utilities.message(attacker.name + ' gains '
                    + str(self.xpValue) + ' XP.', "XP")
        #transform this character into a corpse and remove AI
        self._char = '%'
        self._AI = None
        self._name = 'remains of ' + self.name
        self._state = Character.DEAD

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
    _playerLevel = 0
    @property
    def playerLevel(self):
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
        self._AI = None
        #Player components
        self._xp = 0
        self._playerLevel = 1

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

    def moveOrAttack(self, dx, dy):
        """
        Player moves or attacks in direction (dx, dy)
        """
        #the coordinates the player is moving to/attacking
        x = self.tile.x + dx
        y = self.tile.y + dy
        targetTile = self.level.map.tiles[x][y]

        #try to find an attackable actor there
        target = None
        for a in targetTile.actors:
            #only attack monsters
            if type(a) is Monster:
                #don't attack dead monsters
                if a.state != Character.DEAD:
                    target = a

        #attack if target found, move otherwise
        if target is not None:
            self.attack(target)
        else:
            self.moveAlongVector(dx, dy)

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
