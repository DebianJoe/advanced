#!/usr/bin/python

#Load this module to access the global constants

"""
This module contains all the constants that are used by the application.
Note that all constants are CAPITAL letters only for clarity.
"""
#size of the map
MAP_WIDTH = 85
MAP_HEIGHT = 43

#dungeon generation
DUNGEON_ROOM_MAX_SIZE = 10
DUNGEON_ROOM_MIN_SIZE = 6
DUNGEON_MAX_ROOMS = 30

#town generation
TOWN_HOUSE_MAX_SIZE = 14
TOWN_HOUSE_MIN_SIZE = 8
TOWN_MAX_HOUSES = 18

#field of view
TORCH_RADIUS = 10
TOWN_RADIUS = 30

#experience and level-ups
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150

#config files
MONSTER_CONFIG = "dungeons.conf"

#config switches
SHOW_AI_LOGGING = False
