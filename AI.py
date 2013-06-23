#!/usr/bin/python

######
# AI #
######
from Actors import *

class AI(object):
    """
    Base class for AI logic
    Methods are empty, to be implemented by subclasses
    """

    _character = None

    @property
    def character(self):
        """
        Returns character to which this AI is linked.
        """
        return self._character

    def __init__(self, character):
        """
        Constructor
        Arguments
            character - Character to which this AI is linked.
        """
        self._character = character

    def takeTurn(self):
        """
        Take one turn
        """
        raise Utilities.GameError("Class AI does not have implementation"
                "for takeTurn(), please use one of the subclasss")


class PlayerAI(AI):
    """
    AI sub class that provides player control over characters
    """


class BasicMonsterAI(AI):
    """
    AI sub class that provides AI implementation for basic monsters.
    """

    _player = None
    @property
    def player(self):
        """
        Returns player object if player has been spotted, if not returns None.
        """
        return self._player

    def __init__(self, monster):
        """
        Constructor
        Arguments
            monster - Monster to which this AI is linked.
        """
        super(BasicMonsterAI, self).__init__(monster)
        #init class variables
        self._player = None

    def takeTurn(self):
        """
        Take one turn
        """
        print self.character.name + ' at ' + str(self.character.tile) + ' takes turn.'
        #Only take action if we are in a level
        if self.character.level is None:
            print "   Not in a level, can't take action."
            return

        #Only take action if we find the player
        if self.player is None:
            for c in self.character.level.characters:
                if type(c) is Player:
                    self._player = c
            if self.player is None:
                print "   No player found, staying put"
                return


        #TODO medium: read this from the config file via monsterlibrary via
        #new class variable in Character class
        RoS = 8  # Range of Sight
        RoA = 1  # Range of Attack
        distance = Utilities.distanceBetween(self.character, self.player)
        print '   Player ' + self.player.name + ' found at ' + \
                str(self.player.tile) + ' distance: ' + str(distance)

        #Only take action if player is within range of sight
        if distance > 8:
            print "   Player out of range of sight"
            return
        #Attack if player is within range of attack
        elif distance <= RoA:
            print "   Attacking player"
            return
        else:
            print "   Moving towards player"

           #move towards player if far away
           # if monster.distance_to(player) >= 2:
            #    monster.move_towards(player.x, player.y)

            #close enough, attack! (if the player is still alive.)
            #elif player.fighter.hp > 0:
             #   monster.fighter.attack(player)


        #other approach could be to leverage field of view
        #monster = self.owner
        #if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):


class ConfusedMonsterAI(AI):
    """
    AI sub class that provides AI implementation for confused monsters.
    """
