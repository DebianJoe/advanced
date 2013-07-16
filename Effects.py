#!/usr/bin/python

######################
# Magic/Event system #
######################

import Utilities

class EffectTarget:
    """
    Enumerator class to describe effect target types.
    """
    SELF = 0
    AREA = 1

class Effect(object):
    """
    Base class for more specialized events, melee or magic effects.
    """

    #class variables

    _source = None

    @property
    def source(self):
        """
        The source of this effect
        """
        return self._source

    _targetType = EffectTarget.SELF

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

    _effectColor = (0, 0, 0)

    @property
    def effectColor(self):
        """
        RGB tuple that indicates the color of this effect.
        """
        return self._effectColor
    
    #constructor
    def __init__(self, source):
        """
        Constructor for a new Effect, meant to be used by the Effect subclasses.
        arguments
            source - an object representing the source of the effect
        """
        self._source = source
        #TODO: read effect color from config file
        self._effectColor = (255,-255,-255)

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
        self._targetType = EffectTarget.SELF

    def applyTo(self, target):
        """
        Healing affect will be applied to target character.
        arguments
            target - Character object
        """
        healAmount = Utilities.rollHitDie(self.effectHitDie)
        target.takeHeal(healAmount, self.source)
        effectTiles = [target.tile]
        Utilities.registerEffect(self, effectTiles)


class NovaEffect(MagicEffect):
    """
    This class represents a damage nova effect
    """

    #constructor
    def __init__(self, source):
        super(NovaEffect, self).__init__(source)
        self._effectDescription = "A wave of magical energy ripples outward."
        self._targetType = EffectTarget.AREA

    def applyTo(self, novaSource):
        """
        Nova effect will ripple outward from source actor
        arguments
            novaSource - Actor object
        """
        damageAmount = Utilities.rollHitDie(self.effectHitDie)
        #find all tiles that are impacted by the nova
        sourceTile = novaSource.tile
        fullCircle = True
        excludeBlockedTiles = True
        effectTiles = sourceTile.map.getCircleTiles(sourceTile.x, sourceTile.y, 2, fullCircle, excludeBlockedTiles)
        #exclude the center of the nova
        effectTiles.remove(sourceTile)
        #find all targets in range
        targets = []
        for tile in effectTiles:
            for actor in tile.actors:
                targets.append(actor)
        #apply damage to every target
        for target in targets:
            target.takeDamage(damageAmount, novaSource)
        #effect visualization
        Utilities.registerEffect(self, effectTiles)



