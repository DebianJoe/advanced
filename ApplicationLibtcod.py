#!/usr/bin/python

# This file contains a test implementation of the application class.
# This one is based on libtcod.

import libtcodpy as libtcod

# You can import everyghin you need from module Game
# the Game module will chain load other modules
from Game import Game
from Game import Player
from Game import MonsterLibrary
import CONSTANTS

#actual size of the window
SCREEN_WIDTH = 85 
SCREEN_HEIGHT = 50

#libtcod parameters 
LIMIT_FPS = 20  #20 frames-per-second maximum
PANEL_HEIGHT = 7

#libtcod colors
COLOR_DARK_WALL = libtcod.light_orange * libtcod.dark_grey * 0.2
COLOR_DARK_GROUND = libtcod.orange * 0.4

COLOR_LIGHT_WALL = libtcod.light_orange * 0.3
COLOR_LIGHT_GROUND = libtcod.orange * 0.9

class ApplicationLibtcod():
    """
    This class represents a running instance of the application.
    It connects the game logic to the user interface.
    It is a test implementation of a GUI based on libtcod.
    """
    
    #TODO easy: this class needs better documentation comments 
    
    _game = None
    @property
    def game(self):
        """
        The game object used by this application
        """
        return self._game
    
    _mapConsole = None
    @property
    def mapConsole(self):
        """
        libtcod console (off screen) used to draw the main map
        """
        return self._mapConsole
    
    _panelConsole = None
    @property
    def panelConsole(self):
        """
        libtcod console (off screen) used to draw the panel
        """
        return self.panelConsole
            
    def __init__(self):
        #Initialize libtcod
        libtcod.console_set_custom_font('./media/arial10x10.png', 
                libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 
                'Crunchbang Project', False)
        libtcod.sys_set_fps(LIMIT_FPS)
        
        #Initialize ofscreen consoles
        self._mapConsole = libtcod.console_new(CONSTANTS.MAP_WIDTH, CONSTANTS.MAP_HEIGHT)
        self._panelConsole = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
        
        #Create a new game object for this application
        self._game = Game(self)
         
    def menuBox(self,header, options, width):
        """
        This function will show a menu.
        Arguments
            header - String, text for the header
            options - String list, text for the options
            width - Width (in characters) of the menu box
        """
        if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
     
        #calculate total height for the header (after auto-wrap) and one line per option
        header_height = libtcod.console_get_height_rect(0, 0, 0, width, SCREEN_HEIGHT, header)
        if header == '':
            header_height = 0
        height = len(options) + header_height
     
        #create an off-screen console that represents the menu's window
        window = libtcod.console_new(width, height)
     
        #print the header, with auto-wrap
        libtcod.console_set_default_foreground(window, libtcod.white)
        libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)
     
        #print all the options
        y = header_height
        letter_index = ord('a')
        for option_text in options:
            text = '(' + chr(letter_index) + ') ' + option_text
            libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
            y += 1
            letter_index += 1
     
        #blit the contents of "window" to the root console
        x = SCREEN_WIDTH/2 - width/2
        y = SCREEN_HEIGHT/2 - height/2
        libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 1.0)
     
        #present the root console to the player and wait for a key-press
        libtcod.console_flush()
        while not libtcod.console_is_window_closed():
            key = libtcod.console_wait_for_keypress(True)
            
            #TODO: Remove in next libtcod version
            #Attention: dirty hack, bug in libtcod fires keypress twice...
            key = libtcod.console_wait_for_keypress(True)
            
            #convert the ASCII code to an index
            index = key.c - ord('a')
            #if it corresponds to an option, return it
            if index >= 0 and index < len(options): return index
            #if it is the escape key return None
            if key.vk == libtcod.KEY_ESCAPE: 
                print "Escape menu"
                return None
        
    def testMenu(self):
        img = libtcod.image_load('./media/menu_background.png')
 
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)
        
        choice = None
        while choice == None and not libtcod.console_is_window_closed():
            #show options and wait for the player's choice
            choice = self.menuBox('What option do you want to launch?', 
                        ['Run some test code!',     #Choice 0
                        'Show me some game stuff!',       #Choice 1
                        'Quit'],                   #Choice 2
                        36)
            #interpret choice
            if choice == None: continue
            if choice == 0:
                print "Running some test code!"
                lib = MonsterLibrary()
                myRandom = lib.getRandomMonster(2)
                myRat = lib.createMonster('rat')
                print myRat
                print myRandom
                myRat.attack(myRandom)
                myRat.attack(myRandom)
                myRat.attack(myRandom)
                myRat.attack(myRandom)
                myRat.attack(myRandom)
                myRat.attack(myRandom)
                myRat.attack(myRandom)
                choice = None
            elif choice == 1:
                print "Showing some game stuff!"
                self.newGame()
                self.playGame()
            elif choice == 2:  #quit
                print "Quiting"
                return
        
    def newGame(self):
        self.game.resetGame()
    
    def loadGame(self, fileName):
        self.game.loadGame(fileName)
        
    def saveGame(self, fileName):
        self.game.saveGame(fileName)
        
    def renderAll(self):
        """
        This function renders the main screen
        """
        currentMap = self.game.currentLevel.map.tiles
        con =  self.mapConsole
        libtcod.console_clear(con)
        
        #Go over every cell of the MAP
        for y in range(CONSTANTS.MAP_HEIGHT):
            for x in range(CONSTANTS.MAP_WIDTH):
                if currentMap[x][y].blockSight:
                    #it is a wall
                    libtcod.console_set_char_background(con, x, y, COLOR_LIGHT_WALL, libtcod.BKGND_SET )
                else:
                    #it is empty space
                    libtcod.console_set_char_background(con, x, y, COLOR_LIGHT_GROUND, libtcod.BKGND_SET )
                    
        #TODO hard: Need to manage field of view. Design not clear.
        #Frostlock: Ideally I would like to add the fov capability in the 
        #game logic where it can be used by this class
        #Note the example code in previous project!
        
        #Go over every cell of the MAP
        for y in range(CONSTANTS.MAP_HEIGHT):
            for x in range(CONSTANTS.MAP_WIDTH):
                wall = currentMap[x][y].blockSight

                if wall:
                    libtcod.console_set_char_background(con, x, y, COLOR_LIGHT_WALL, libtcod.BKGND_SET)
                else:
                    libtcod.console_set_char_background(con, x, y, COLOR_LIGHT_GROUND, libtcod.BKGND_SET)

        #Draw entries and exits for the level
        for myActor in self.game.currentLevel.portals:
            libtcod.console_set_default_foreground(con, libtcod.purple)
            libtcod.console_put_char(con, myActor.tile.x, myActor.tile.y, myActor.char, libtcod.BKGND_NONE)
            
        #Draw level characters
        for myActor in self.game.currentLevel.characters:
            libtcod.console_set_default_foreground(con, libtcod.green)
            if type(myActor) == Player:
                    libtcod.console_set_default_foreground(con, libtcod.white)
            libtcod.console_put_char(con, myActor.tile.x, myActor.tile.y, myActor.char, libtcod.BKGND_NONE)
        
        #TODO medium: make sure player is visible 
        #idea: it is drawn above with the characters, just redraw on top?
        
        #blit the contents of "con" to the root console
        libtcod.console_blit(con, 0, 0, CONSTANTS.MAP_WIDTH, CONSTANTS.MAP_HEIGHT, 0, 0, 0)
        
        #TODO medium: create a GUI panel
        #Frostlock: this needs some game message log first in the game logic
    
    def handleKeys(self):
        key = libtcod.console_wait_for_keypress(True)
        #TODO: Remove in next libtcod version
        #Attention: dirty hack, bug in libtcod fires keypress twice...
        key = libtcod.console_wait_for_keypress(True)
        
        key_char = chr(key.c)
        
        if key.vk == libtcod.KEY_ESCAPE:
            return 'exit'
        elif key_char == '>':
            #go down
            print "> Going down"
            self.game.nextLevel()
        elif key_char == '<':
            #go up
            print "< Going up"
            self.game.previousLevel()
                            
    def playGame(self):
        mouse = libtcod.Mouse()
        key = libtcod.Key()
        #main loop
        while not libtcod.console_is_window_closed():
            
            #render the screen
            self.renderAll()
            #refresh visual
            libtcod.console_flush()
            
            #handle keys and exit game if needed
            if self.handleKeys() == 'exit':
                break
        
            #TODO hard: actual play :-) 
            #at the moment this only shows some game stuff


#########################################################################
#Launching code
#########################################################################
def launch():
    myApplication = ApplicationLibtcod()
    myApplication.testMenu()
    
if __name__ == '__main__':
    launch()
#########################################################################    
    


