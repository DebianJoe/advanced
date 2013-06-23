#!/usr/bin/python

######################
# Magic/Event system #
######################
class Effect(object):
    """
    Base class for more specialized events, melee or magic effects.
    """
    
    #class variables
    _id = "ID not set"
    @property
    def id(self):
        """
        ID code for this Effect
        """
        return self._id

class MagicEffect(Effect):
    """
    Base class for magic effects.
    """
    #current thinking is that this class can both represent targeted as area
    #of effect spells.
