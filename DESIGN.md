Class design
============
This document attempts to explain the high level class structure of this project. I strongly recommend to first read through this doc before digging into the code. It should help you understand the general layout
of the project much faster.

<b>Not every class is mentioned in this document, only the most important ones.</b>In the class definitions you will also find additional comments that explain each class in more detail.

Main classes
------------
These are the main classes:
* <b>Application</b> is the class that gets "started", it links game logic to user interface.
* <b>Game</b> is the top level class for all game logic, once initialized it will have multiple levels.
* <b>Level</b> represents one level of the game, each level has at least
   * one <b>Map</b> object
   * multiple <b>Character</b> objects
   * multiple <b>Item</b> objects
Note that <b>Level</b>, <b>Character</b> and <b>Item</b> are generic classes, 
they define generic interfaces to allow easy polymorphism of their subclasses. Ideally we only use these generic classes in our code. That way we write code that works for future specialized sub classes as well.
The following specialised sub classes are there at the moment, we can of course add more.

* <b>Level</b> subclasses:
   * <b>GeneratedLevel</b><br> A randomly generated level.
   * <b>TownLevel</b><br> A level representing a town with a fixed layout.
* <b>Character</b> subclasses:
   * <b>Player</b><br> Character representing the player
   * <b>NPC</b><br> Character representing an NPC, for example a vendor
   * <b>Monster</b><br> Character representing a monster
* <b>Item</b> subclasses:
   * <b>Equipment</b><br> Item that can be equiped (armor, weapon)
   * <b>Consumable</b><br> Item that can be consumed (potion, scroll)

Supporting classes
------------------
<b>Libraries to abstract data access</b><br>
To avoid hardcoding monster and item data in the code I would propose to externalize this data. 
A library class will allow to easily access it. These classes can also help with the creation of new
Monsters and Items.
* <b>Library</b> subclasses:<br>Contains the logic to access the external data store
   * <b>MonsterLibrary</b><br>Expands with monster creation functionality
   * <b>ItemLibrary</b><br>Expands with item creation functionality

<b>AI related</b><br>
I'm not entirely sure yet on how to implement AI, I propose to start with something basic. A generic <b>AI</b> class
that will show a uniform interface to the main classes (like <b>Game</b>) with specialized subclasses that implement 
actual AIs.
* <b>AI</b> subclasses:<br>
   * <b>BasicMonsterAI</b><br>
   * <b>ConfusedMonsterAI</b><br>
   * <b>PlayerAI</b><br> This is a bit of a special case, I'm wondering if we can have the player controls mapped via this AI class. That way the game can ask every character to take a turn some AI classes will propose an action, this one could request the player to provide input.

<b>Utility</b><br>
A class in which reusable utility functions can be placed. For example a function to roll a hitdie.
  

