#!/usr/bin/python

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

class ConfusedMonsterAI(AI):
    """
    AI sub class that provides AI implementation for confused monsters.
    """
