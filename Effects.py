#!/usr/bin/python

######################
# Magic/Event system #
######################

import Utilities

class Effect(object):
    """
    Base class for more specialized events, melee or magic effects.
    """

    #class variables

    #_id = "ID not set"

    #@property
    #def id(self):
        #"""
        #ID code for this Effect
        #"""
        #return self._id

    _source = None

    @property
    def source(self):
        """
        The source of this effect
        """
        return self._source

    SELF = 0
    _targetType = SELF

    @property
    def targetType(self):
        """
        indicates the type of target this effect needs, enumerator
        """
        return self._targetType

    _effectHitDie = "1d6"

    @property
    def effectHitDie(self):
        """
        Hit die used to determine the random size of this effect.
        """
        return self._effectHitDie

    _effectDescription = "Description not set"

    @property
    def effectDescription(self):
        """
        Textual description that describes what happens when
        this effect is applied.
        """
        return self._effectDescription

    #constructor
    def __init__(self, source):
        """
        Constructor for a new Effect, meant to be used by the Effect subclasses.
        arguments
            source - an object representing the source of the effect
        """
        self._source = source

    #functions
    def applyTo(self, target):
        """
        Applies this effect to a target. The target can be several types of
        objects, it depends on the specific Effect subclass.
        """

class MagicEffect(Effect):
    """
    Base class for magic effects.
    """
    #current thinking is that this class can both represent targeted as area
    #of effect spells.

class HealEffect(MagicEffect):
    """
    This class represents a healing effect
    """

    #constructor
    def __init__(self, source):
        super(HealEffect, self).__init__(source)
        self._effectDescription = "Wounds close, bones knit."
        self._targetType = Effect.SELF

    def applyTo(self, target):
        """
        Healing affect will be applied to target character.
        arguments
            target - Character object
        """
        healAmount = Utilities.rollHitDie(self.effectHitDie)
        target.takeHeal(healAmount, self.source)




