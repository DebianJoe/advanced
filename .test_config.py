#!/usr/bin/python

# This tests Game.conf for syntax errors,
# valid numbers and existing function & class names.

import sys
import json
import random
import ConfigParser
import AI
import Actors

red = "\033[1;31m"
green = "\033[1;32m"
yellow = "\033[1;33m"
reset = "\033[1;m"
has_errors = False

def has_key(dic, key):
    """
    Do not call this directly.
    """

    if key in dic.keys():
        return True
    else:
        print(yellow + '\t\t"' + key + '" is not defined' + reset)
        return False

def is_string(dic, key):
    """
    Test if the key exists in dictionary.
    """

    global has_errors
    if not has_key(dic, key):
        has_errors = True

def is_numeric(dic, key):
    """
    Test if the key value in dictionary is a number.
    """

    global has_errors
    if has_key(dic, key):
        try:
            int(dic[key])
        except ValueError:
            has_errors = True
            print(yellow + '\t\t"' + key + '" is not numeric' + reset)

def is_hitdie(dic, key):
    """
    Test if the key value in dictionary is a hitdie.
    """

    global has_errors
    if has_key(dic, key):
        try:
            hitdie = str(dic[key])
            d_index = hitdie.lower().index('d')
            #test if both components of hitdie are numeric
            int(hitdie[0:d_index])
            int(hitdie[d_index + 1:])
        except ValueError:
            has_errors = True
            print(yellow + '\t\t"' + key + '" is not numeric' + reset)
            print(yellow + '\t' + "Valid hitdies consist of two integers" + reset)
            print(yellow + '\t' + "separated by a letter d" + reset)

def has_attrib(target, dic, key):
    """
    Test if the key value in dictionary is a Class or Function in target import.
    """

    global has_errors
    if has_key(dic, key):
        try:
            # ignore blank entries
            name = dic[key]
            if len(name) > 1:
                getattr(target, name)
        except AttributeError:
            has_errors = True
            print(yellow + '\t\t"' + dic[key] + '" not a valid function or class' + reset)
    else:
        has_errors = True


def is_list(dic, key):
    """
    Test if the key value in dictionary is a list.
    """

    global has_errors
    if has_key(dic, key):
        try:
            value = json.loads(dic[key])
            if not type(value) is list:
                raise Exception('not a list type')
        except Exception, e:
            has_errors = True
            print(yellow + '\t\t"' + key + '" invalid' + reset)

def is_list_of_list(dic, key):
    """
    Test if the key value in dictionary is a list.
    """

    global has_errors
    if has_key(dic, key):
        try:
            value = json.loads(dic[key])
            if not type(value) is list:
                raise Exception('not a list type')
            if len(value) == 0:
                raise Exception('empty list')
            if not type(value[0]) is list:
                raise Exception('must be a list of lists')
            if len(value[0]) < 2:
                raise Exception('need at least two values in the list')
        except Exception, e:
            has_errors = True
            print(yellow + '\t\t"' + key + '" invalid - ' + str(e) + reset)

if __name__ == '__main__':
    config = ConfigParser.ConfigParser()
    try:
        print('\nChecking Game.conf')
        config.read('Game.conf')
    except Exception, e:
        print(red + str(e) + reset)
        sys.exit(1)

    #TEST LISTS SECTION HERE
    lists = dict(config.items('lists'))
    print('Checking lists section')
    #is_list(lists, 'monster list')
    is_list_of_list(lists, 'max monsters')
    #is_list(lists, 'item list')
    is_list_of_list(lists, 'max items')

    #check monsters section
    print('Checking monsters section')
    for monster_name in config.get('lists', 'monster list').split(', '):
        monster = dict(config.items(monster_name))
        print('* testing %s...' % monster_name)

        # TEST MONSTER HERE
        is_string(monster, 'char')
        is_string(monster, 'name')
        is_list_of_list(monster, 'chance')
        is_list(monster, 'color')
        is_hitdie(monster, 'hitdie')
        is_numeric(monster, 'defense')
        is_numeric(monster, 'power')
        is_numeric(monster, 'xp')
        has_attrib(AI, monster, 'ai')

    print('Checking items section')
    for item_name in config.get('lists', 'item list').split(', '):
        item = dict(config.items(item_name))
        print('* testing %s...' % item_name)

        # TEST ITEM HERE
        has_attrib(Actors, item, 'type')
        is_string(item, 'char')
        is_string(item, 'name')
        is_list_of_list(item, 'chance')

        # Equipment specific
        if item['type'] == 'Equipment':
            is_numeric(item, 'defense_bonus')
            is_numeric(item, 'power_bonus')

    if has_errors:
        print(red + '\nUnit test failed :(' + reset)
    else:
        print(green + '\n' + random.choice(("all systems go :)",
            "ready to rock \'n roll :)", "all tests passed :)")) + reset)
