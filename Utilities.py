#Module with reusable utility functions

#TODO easy: this module needs better documentation comments
#TODO easy: standardize functions names in this module (get rid of _) 

import random

# rolling a hitdie
def roll_hit_die(hitdie):
    """
    this function simulates rolling hit dies and returns the resulting 
    nbr of hitpoints. Hit dies are specified in the format xdy where
    x indicates the number of times that a die (d) with y sides is 
    thrown. For example 2d6 means rolling 2 six sided dices.
    Arguments
        hitdie - a string in hitdie format
    Returns
        integer number of hitpoints
    """
    #interpret the hitdie string
    d_index = hitdie.lower().index('d')
    nbr_of_rolls = int(hitdie[0:d_index])
    dice_size = int(hitdie[d_index + 1:])
    #roll the dice
    role_count = 0
    hitpoints = 0
    while role_count <= nbr_of_rolls:
        role_count += 1
        hitpoints += random.randrange(1, dice_size)
    return hitpoints

def random_choice_index(chances):  #choose one option from list of chances, returning its index
    #the dice will land on some number between 1 and the sum of the chances
    dice = random.randrange(1, sum(chances))
 
    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w
 
        #see if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1
 
def random_choice(chances_dict):
    #choose one option from dictionary of chances, returning its key
    chances = chances_dict.values()
    strings = chances_dict.keys()
 
    return strings[random_choice_index(chances)]

def from_dungeon_level(table, dungeon_level):
    #returns a value that depends on level. the table specifies what value occurs after each level, default is 0.
    for (value, level) in table:
        if dungeon_level >= level:
            return value
    return 0

def message(message):
    #TODO medium: improve implementation to keep log of messages
    #ideally would like several levels of messages (debug, detail, main)
    #that we we can only show relevant message level during gameplay
    print message

class GameError(Exception):
    """
    Simple error that can be raised in case there is a problem with the game.
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
