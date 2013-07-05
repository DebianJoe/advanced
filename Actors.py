#!/usr/bin/python

#from Maps import Tile

import random
import Utilities
import CONSTANTS
import Effects

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
        self.registerWithLevel(targetLevel)

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
        return self._name + " " + super(Actor, self).__str__()

    def registerWithLevel(self, level):
        """
        This function registers this actor with the provided level.
        It has to be overridden in the Actor subclasses to ensure that the
        actor correctly registers with the level.
        """
        raise Utilities.GameError('Missing implementation registerWithLevel()')

    def moveToRandomTile(self):
        """
        moves this actor to a random tile on the current level
        """
        if self.level is not None:
            self.moveToTile(self.level.getRandomEmptyTile)

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
        self.level = targetLevel
        self.moveToTile(targetTile)

    def removeFromLevel(self):
        """
        This method removes this actor from the level
        """
        if self.tile is not None:
            self.tile.removeActor(self)
        self._tile = None
        if self.level is not None:
            self.level.removeActor(self)
        self._level = None

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
    _message = ''

    @property
    def message(self):
        """
        In game message that should be displayed when portal is used.
        """
        return self._message

    _destination = None

    @property
    def destinationPortal(self):
        """
        The destination portal where this portal leads to
        """
        return self._destination

    def __init__(self):
        """
        Constructor to create a new portal
        """
        super(Portal, self).__init__()

    def connectTo(self, otherPortal):
        """
        Connects this portal to another portal
        """
        self._destination = otherPortal
        otherPortal._destination = self

    def registerWithLevel(self, level):
        """
        Makes the level aware that this portal is on it.
        """
        level.addPortal(self)


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
        return self._inventoryItems + self._equipedItems

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
        super(Character, self).__init__()
        #initialize class variables
        self._baseDefense = 0
        self._basePower = 1
        self._equipedItems = []
        self._inventoryItems = []
        self._xpValue = 0
        self._AI = None
        self._state = Character.ACTIVE

    #Functions
    def registerWithLevel(self, level):
        """
        Makes the level aware that this character is on it.
        """
        level.addCharacter(self)

    def addItem(self, item):
        """
        adding item puts it in this characters inventory
        """
        self.inventoryItems.append(item)
        #TODO: check for auto equip

    def removeItem(self, item):
        """
        removes the item from the characters inventory
        """
        if item in self.equipedItems:
            #unequip the item
            self.unEquipItem(item)
        self.inventoryItems.remove(item)

    def equipItem(self, item):
        """
        basic implementation of equiping, doesn't take into account
        equipment slots. Should be overridden in subclass implementations.
        """
        #can only equip if item is in inventory
        if item in self.inventoryItems:
            #can only equip if not yet equiped
            if item not in self.equipedItems:
                self.equipedItems.append(item)

    def unEquipItem(self, item):
        """
        basic implementation of equiping, doesn't take into account
        equipment slots. Should be overridden in subclass implementations.
        """
        #can only unequip if item is equiped
        if item in self.equipedItems:
            self.equipedItems.remove(item)

    def pickUpItem(self, item):
        """
        Make this character pick up an item.
        Arguments
            item - the item to be picked up
        """
        #remove the item from its tile and level
        item.removeFromLevel()
        #add the item to the inventory of this character
        self.addItem(item)
        #message
        Utilities.message(self.name.capitalize() + ' picks up a '
                    + item.name + '.', "GAME")

    def dropItem(self, item):
        """
        Make this character drop an item on the current tile.
        Arguments
            item - the item to be dropped
        """
        #unequip it if required
        if item in self.equipedItems:
            self.unEquipItem(item)
        #if it is in the inventory remove it
        if item in self.inventoryItems:
            self.inventoryItems.remove(item)
        #add it to the current tile of the character
        item.moveToLevel(self.level, self.tile)
        #message
        Utilities.message(self.name.capitalize() + ' drops a '
                    + item.name + '.', "GAME")

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
                    + target.name + ' for ' + str(damage) + ' Damage.', "GAME")
            target.takeDamage(damage, self)
        else:
            Utilities.message(self.name.capitalize() + ' attacks '
                    + target.name + ' but it has no effect!', "GAME")

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
        #check for death
        if self.currentHitPoints < 0:
            Utilities.message(self.name.capitalize() + ' is killed!', "GAME")
            self._killedBy(attacker)

    def _killedBy(self, attacker):
        """
        This function handles the death of this Character
        """
        if type(attacker) is Player:
            #yield experience to the player
            attacker.gainXp(self.xpValue)
            Utilities.message(attacker.name + ' gains '
                    + str(self.xpValue) + ' XP.', "GAME")
        if type(attacker) is Monster:
            if attacker.killedByText != '':
                Utilities.message(attacker.killedByText, "GAME")
        #transform this character into a corpse and remove AI
        self._char = '%'
        self._AI = None
        self._name = 'remains of ' + self.name
        self._state = Character.DEAD

    def takeHeal(self, amount, healer):
        """
        function to heal a given amount of hitpoints
        arguments
           amount - the number of hitpoints to heal
           healer - the source of teh healing
        """
        #heal by the given amount
        if amount > 0:
            self.currentHitPoints += amount
            Utilities.message(self.name.capitalize() + ' gains '
                    + str(amount) + ' hitpoints from a ' +  healer.name
                    + '.', "GAME")

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
    def xp(self):
        """
        Returns the current xp of the player.
        """
        return self._xp

    @property
    def nextLevelXp(self):
        """
        Returns the required Xp to reach the next player level
        """
        return CONSTANTS.LEVEL_UP_BASE + self.playerLevel * CONSTANTS.LEVEL_UP_FACTOR

    _playerLevel = 1

    @property
    def playerLevel(self):
        """
        Returns the current level of the player.
        """
        return self._playerLevel

    #constructor
    def __init__(self):
        """
        Creates and initializes new player object. Note that the object is not
        linked to a game tile. It should be moved to the tile after creation.
        """
        #call super class constructor
        super(Player, self).__init__()

        #initialize all variables
        #Actor components
        self._id = 'player'
        self._char = '@'
        self._baseMaxHitPoints = 100
        self._currentHitPoints = 100
        self._name = random.choice(('Joe', 'Wesley', 'Frost'))
        #Character components
        self._baseDefense = 2
        self._basePower = 6
        self._xpValue = 0
        self._AI = None
        #Player components
        self._xp = 0
        self._playerLevel = 1

    #functions
    def gainXp(self, amount):
        """
        Increase xp of this player with the given amount
        arguments
            amount - integer
        """
        self._xp += amount
        #TODO:
        #Check for level up


    def followPortal(self, portal):
        """
        Send player through specified portal.
        """
        #Game message
        Utilities.message(portal.message, "GAME")
        #Move the player to the destination
        destinationLevel = portal.destinationPortal.level
        destinationTile = portal.destinationPortal.tile
        self.moveToLevel(destinationLevel, destinationTile)
        #change the current level of the game to the destinationlevel
        myGame = destinationLevel.game
        myGame.currentLevel = destinationLevel

    def tryMoveOrAttack(self, dx, dy):
        """
        Player tries to move or attack in direction (dx, dy).
        This function is meant to be called from the GUI.
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

    def tryFollowPortalUp(self):
        """
        Player attempts to follow a portal up at the current location.
        This function is meant to be called from the GUI.
        """
        #check if there is a portal up on the current tile
        for a in self.tile.actors:
            if type(a) is Portal and a.char == '<':
                self.followPortal(a)
                break

    def tryFollowPortalDown(self):
        """
        Player attempts to follow a portal down at the current location.
        This function is meant to be called from the GUI.
        """
        #check if there is a portal up on the current tile
        for a in self.tile.actors:
            if type(a) is Portal and a.char == '>':
                self.followPortal(a)
                break

    def tryPickUp(self):
        """
        Player attempts to pick up something on the current location.
        This function is meant to be called from the GUI.
        """
        #check if there is an item on the current tile
        for a in self.tile.actors:
            if isinstance(a, Item):
                self.pickUpItem(a)

    def tryUseItem(self, item):
        """
        Player attempts to use an item.
        This function is meant to be called from the GUI.
        """
        if isinstance(item, Consumable):
            #try to use the consumable
            if item.effect is not None and item.isConsumed is False:
                if item.effect.targetType == Effects.Effect.SELF:
                    item.applyTo(self)
            #remove the item it is used up
            if item.isConsumed == True:
                self.removeItem(item)

        elif isinstance(item, Equipment):
            pass
            #try to equip
        else:
            raise Utilities.GameError("Missing implementation to use item")


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
        super(Monster, self).__init__()


#########
# ITEMS #
#########
class Item(Actor):
    """
    Base class for items
    Should probably not be instatiated but describes the general interface of
    an item
    """

    def registerWithLevel(self, level):
        """
        Makes the level aware that this item is on it.
        """
        level.addItem(self)

    #constructor
    def __init__(self, item_data):
        """
        Creates a new Item object, normally not used directly but called
        by sub class constructors.
        """
        #call super class constructor
        super(Item, self).__init__()
        #Initialize Actor components
        self._id = item_data['key']
        self._char = item_data['char']
        self._baseMaxHitPoints = 1
        self._currentHitPoints = self._baseMaxHitPoints
        self._name = item_data['name']


class Equipment(Item):
    """
    Sub class for equipment = items that can be equiped
    Might need more subclasses for weapons versus armor
    """

    _defenseBonus = 0

    @property
    def defenseBonus(self):
        """
        The defense bonus of this piece of equipment
        """
        return self._defenseBonus

    _powerBonus = 0

    @property
    def powerBonus(self):
        """
        The power bonus of this piece of equipment
        """
        return self._powerBonus

    #constructor
    def __init__(self, item_data):
        """
        Creates a new uninitialized Equipment object.
        Use ItemLibrary.createItem() to create an initialized Item.
        """
        #call super class constructor
        super(Equipment, self).__init__(item_data)
        #Initialize equipment properties
        self._defenseBonus = item_data['defense_bonus']
        self._powerBonus = item_data['power_bonus']

class Consumable(Item):
    """
    Sub class for items that can be used and consumed.
    """

    _effect = None

    @property
    def effect(self):
        """
        The effect that this consumable can generate.
        """
        return self._effect

    _consumed = False

    @property
    def isConsumed(self):
        """
        Boolean indicating if this consumable has been consumed.
        """
        return self._consumed

    #constructor
    def __init__(self, item_data):
        """
        Creates a new uninitialized Consumable object.
        Use ItemLibrary.createItem() to create an initialized Item.
        """
        #call super class constructor
        super(Consumable, self).__init__(item_data)
        #consumables usually have an effect
        if item_data['effect'] != '':
            effect_class = eval("Effects." + item_data['effect'])
            newEffect = effect_class and effect_class(self) or None
            newEffect._effectHitDie = item_data['effecthitdie']
            self._effect = newEffect
            self._consumed = False
        else:
            self._effect = None
            self._consumed = True

    #functions
    def applyTo(self, target):
        """
        Applies the effect of this consumable to a target.
        The target can be several types of object, it depends on the
        specific Effect subclass.
        """
        #consumable can be used only once.
        if self._consumed is False:
            self.effect.applyTo(target)
            self._consumed = True
            self._effect = None


class QuestItem(Item):
    """
    Sub class for quest items
    Probably don't need this in the beginning but it would fit in here :)
    """
