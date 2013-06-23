#!/usr/bin/python

######
# AI #
######


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

    def __init__(self, monster):
        """
        Constructor
        Arguments
            monster - Monster to which this AI is linked.
        """
        super(BasicMonsterAI, self).__init__(monster)

    def takeTurn(self):
        """
        Take one turn
        """
        print 'Hmm what should I do?'

class ConfusedMonsterAI(AI):
    """
    AI sub class that provides AI implementation for confused monsters.
    """
