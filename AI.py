#!/usr/bin/python

######
# AI #
######
from Actors import *
from Utilities import message
import math

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
        message(self.character.name + ' at ' + str(self.character.tile) +
                ' takes turn.', "AI")
        #Only take action if we are in a level
        if self.character.level is None:
            message("   Not in a level, can't take action.", "AI")
            return

        #Only take action if we find the player
        if self.player is None:
            for c in self.character.level.characters:
                if type(c) is Player:
                    self._player = c
            if self.player is None:
                message("   No player found, staying put", "AI")
                return


        #TODO medium: read this from the config file via monsterlibrary via
        #new class variable in Character class
        RoS = 8  # Range of Sight
        RoA = 1  # Range of Attack
        distance = Utilities.distanceBetween(self.character, self.player)
        #message('   Player ' + self.player.name + ' found at ' + \
        #        str(self.player.tile) + ' distance: ' + str(distance), "AI")

        #Only take action if player is within range of sight
        if distance > RoS:
            #message("   Player out of range of sight", "AI")
            return
        #Attack if player is within range of attack
        elif distance < RoA:
            message("   Attacking player", "AI")
            self.character.attack(self.player)
            return
        else:
            message("   Moving towards player", "AI")
            self.character.moveTowards(self.player)
            return


class ConfusedMonsterAI(AI):
    """
    AI sub class that provides AI implementation for confused monsters.
    """
