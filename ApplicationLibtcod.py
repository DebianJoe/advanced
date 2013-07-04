#!/usr/bin/python

# This file contains a test implementation of the application class.
# This one is based on libtcod.

import libtcodpy as libtcod

# You can import everything you need from module Game
# the Game module will chain load other modules
from Game import Game
from Game import Player
import Actors
import Libraries
import Maps
import CONSTANTS
import Utilities
import textwrap


#actual size of the window
SCREEN_WIDTH = 85
SCREEN_HEIGHT = 50

#libtcod parameters
LIMIT_FPS = 20  # 20 frames-per-second maximum
PANEL_HEIGHT = 7
BAR_WIDTH = 20
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

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
        return self._panelConsole

    _messages = None

    @property
    def messages(self):
        """
        returns the most recent game messages
        """
        return self._messages

    def addMessage(self, new_msg):  # , color = libtcod.white):
        #split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
        for line in new_msg_lines:
            #only keep the last messages
            if len(self.messages) == MSG_HEIGHT:
                del self.messages[0]
            #add the new line
            self.messages.append(line)  # (line, color) )

    def __init__(self):
        """
        Constructor that creates a new instance of the application
        """
        #Initialize libtcod
        libtcod.console_set_custom_font('./media/arial10x10.png',
                libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT,
                'Crunchbang Project', False)
        libtcod.sys_set_fps(LIMIT_FPS)

        #Initialize ofscreen consoles
        self._mapConsole = libtcod.console_new(CONSTANTS.MAP_WIDTH, CONSTANTS.MAP_HEIGHT)
        self._panelConsole = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

        #Prepare to receive messages from the game utilities
        #(this allows the utilities to send game messages to this application)
        self._messages = []
        Utilities.application = self

        #Create a new game object for this application
        #self._game = Game(self)

    ##########################################################################
    # show functions
    #   These functions all use a similar technique to show something on screen
    #       1) They store what was on screen before them
    #       2) They show something new
    #       3) They go into a loop handling user input
    #       4) Once the loop breaks they restore what was on screen before them
    #   This allows to create multiple menu's and screens on top of eachother
    ##########################################################################
    def showMenu(self, header, options, width):
        """
        This function will show a menu. The application waits for user input
        before returning the selected option.
        The function will return None if the user escapes the menu.
        Arguments
            header - String, text for the header
            options - String list, text for the options
            width - Width (in characters) of the menu box
        """
        if len(options) > 26:
            raise ValueError('Cannot have a menu with more than 26 options.')

        #calculate total height for the header (after auto-wrap)
        header_height = libtcod.console_get_height_rect(0, 0, 0, width, SCREEN_HEIGHT, header)
        if header == '':
            header_height = 0
        #add one line per option
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

        #Show in the middle of the screen
        x = SCREEN_WIDTH / 2 - width / 2
        y = SCREEN_HEIGHT / 2 - height / 2

        #store the current view
        behind_window = libtcod.console_new(width, height)
        libtcod.console_blit(0, x, y, width, height, behind_window, 0, 0, 1.0, 1.0)

        #blit the contents of "window" to the root console
        libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 1.0)

        #present the root console to the player and wait for a key-press
        libtcod.console_flush()
        returnMsg = ''
        while not libtcod.console_is_window_closed():
            key = libtcod.console_wait_for_keypress(True)
            #TODO: Remove in next libtcod version
            #Attention: dirty hack, bug in libtcod fires keypress twice...
            key = libtcod.console_wait_for_keypress(True)

            #convert the ASCII code to an index
            index = key.c - ord('a')
            #if it corresponds to an option, return it
            if index >= 0 and index < len(options):
                returnMsg = index
                break
            #if it is the escape key return None
            if key.vk == libtcod.KEY_ESCAPE:
                returnMsg = None
                break

        #Clean up (restore whatever was behind this window)
        libtcod.console_blit(behind_window, 0, 0, width, height, 0, x, y, 1.0, 1.0)
        libtcod.console_flush()

        return returnMsg

    def showMessage(self, header, message, width):
        """
        This function will show a pop up message in the middle of the screen.
        It waits for the user to acknowledge the message by hitting enter or
        escape
        """
        #calculate total height for the header (after auto-wrap)
        header_height = libtcod.console_get_height_rect(0, 0, 0, width, SCREEN_HEIGHT, header)
        if header == '':
            header_height = 0
        #calculate total height for the message (after auto-wrap)
        msg_height = libtcod.console_get_height_rect(0, 0, 0, width, SCREEN_HEIGHT, message)
        if message == '':
            msg_height = 0
        height = header_height + msg_height

        #create an off-screen console that represents the message window
        window = libtcod.console_new(width, height)

        #print the header, with auto-wrap
        libtcod.console_set_default_foreground(window, libtcod.red)
        libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

        #print the message, with auto-wrap
        libtcod.console_set_default_foreground(window, libtcod.white)
        libtcod.console_print_rect_ex(window, 0, header_height, width, height, libtcod.BKGND_NONE, libtcod.LEFT, message)

        #center the pop up on the screen
        x = SCREEN_WIDTH / 2 - width / 2
        y = SCREEN_HEIGHT / 2 - height / 2

        #store the current view
        behind_window = libtcod.console_new(width, height)
        libtcod.console_blit(0, x, y, width, height, behind_window, 0, 0, 1.0, 1.0)

        #blit the contents of "window" to the root console
        libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 1.0)

        #present the root console to the player and wait for a key-press
        libtcod.console_flush()
        #Loop until player accepts message using enter or escape
        returnMsg = ''
        while not libtcod.console_is_window_closed():
            key = libtcod.console_wait_for_keypress(True)
            #TODO: Remove in next libtcod version
            #Attention: dirty hack, bug in libtcod fires keypress twice...
            key = libtcod.console_wait_for_keypress(True)
            #Wait for enter or escape
            if key.vk == libtcod.KEY_ESCAPE:
                returnMsg = 'Escape'
                break
            if key.vk == libtcod.KEY_ENTER:
                returnMsg = 'Enter'
                break

        #Clean up (restore whatever was behind this window)
        libtcod.console_blit(behind_window, 0, 0, width, height, 0, x, y, 1.0, 1.0)
        libtcod.console_flush()

        return returnMsg

    def showWelcomeScreen(self):
        #store the current view
        behind_window = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
        libtcod.console_blit(0, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, behind_window, 0, 0, 1.0, 1.0)

        #show the background image, at twice the regular console resolution
        img = libtcod.image_load('./media/menu_background.png')
        libtcod.image_blit_2x(img, 0, 0, 0)

        while not libtcod.console_is_window_closed():
            #show options and wait for the player's choice
            choice = self.showMenu('Main menu:\n----------',
                        ['Start a new game',       # Choice 0
                        'Continue previous game',  # Choice 1
                        'Go to debug mode',        # Choice 2
                        'Quit'],                   # Choice 3
                        36)
            #interpret choice
            if choice is None:
                continue
            if choice == 0:
                print "Start a new game"
                self.newGame()
                self.showGameScreen()
                continue
            elif choice == 1:
                print "Continue previous game"
                self.showMessage('Oops...',
                        'I don\'t know how to load a game yet :-)', 36)
            elif choice == 2:  # quit
                print "Go to debug mode"
                self.showDebugScreen()

            elif choice == 3:
                print "Quiting"
                break

        #Clean up (restore whatever was behind this window)
        libtcod.console_blit(behind_window, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0, 1.0, 1.0)
        libtcod.console_flush()

    def showDebugScreen(self):
        #store the current view
        behind_window = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
        libtcod.console_blit(0, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, behind_window, 0, 0, 1.0, 1.0)

        #show the background image, at twice the regular console resolution
        img = libtcod.image_load('./media/menu_debug.png')
        libtcod.image_blit_2x(img, 0, 0, 0)

        while not libtcod.console_is_window_closed():
            #show options and wait for the player's choice
            choice = self.showMenu('Select debug option:',
                        ['Run some test code!',      # Choice 0
                        'Show me some game stuff!',  # Choice 1
                        'Back'],                     # Choice 2
                        36)
            #interpret choice
            if choice is None:
                continue
            if choice == 0:
                print "Running some test code!"
                self.runTestCode()
                self.showMessage('Test code complete!',
                        'There might be some output in the console...', 36)
                continue
            elif choice == 1:
                print "Showing some game stuff!"
                self.newGame()
                self.showGameScreen()
            elif choice == 2:  # quit
                print "Back"
                break
        #Clean up (restore whatever was behind this window)
        libtcod.console_blit(behind_window, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0, 1.0, 1.0)
        libtcod.console_flush()

    def showGameScreen(self):
        #store the current view
        behind_window = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
        libtcod.console_blit(0, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, behind_window, 0, 0, 1.0, 1.0)

        #main loop
        while not libtcod.console_is_window_closed():
            #render the screen
            self.renderAll()
            #refresh visual
            libtcod.console_flush()

            #handle keys and exit game if needed
            #this allows the player to play his turn
            if self.handleKeys() == 'exit':
                break

            #Let the game play a turn
            self.game.playTurn()

        #Clean up (restore whatever was behind this window)
        libtcod.console_blit(behind_window, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0, 1.0, 1.0)
        libtcod.console_flush()

    def showInventory(self):
        if self.game is not None and self.game.player is not None:
            header = "Inventory"
            width = 45
            options = []
            items = self.game.player.allItems
            for item in items:
                options.append(item.name)
            selection = self.showMenu(header, options, width)
            if selection is not None:
                self.game.player.tryUseItem(items[selection])

    ##########################################################################
    # DebugScreen functions
    ##########################################################################
    def runTestCode(self):
        """
        This function ties into the debug menu. It is meant to allow execution
        of some test code. Feel free to change the contents of this function.
        """
        #lib = MonsterLibrary()
        #myRandom = lib.getRandomMonster(2)
        #myRat = lib.createMonster('rat')
        #print myRat
        #print myRandom
        #myRat.attack(myRandom)
        #myRat.attack(myRandom)
        #myRat.attack(myRandom)

        lib = Libraries.ItemLibrary()
        myItem = lib.createItem('heal')
        print myItem
        myItem = lib.createItem('sword')
        print myItem
        myItem = lib.createItem('cloak')
        print myItem
        myItem = lib.createItem('fireball')
        print myItem


        #myMap = Maps.TownMap(CONSTANTS.MAP_WIDTH, CONSTANTS.MAP_HEIGHT)
        #print myMap

    ##########################################################################
    # GameScreen functions
    ##########################################################################
    def newGame(self):
        self._messages = []
        self._game = Game(self)

    def loadGame(self, fileName):
        self.game.loadGame(fileName)

    def saveGame(self, fileName):
        self.game.saveGame(fileName)

    def renderAll(self):
        """
        This function renders the main screen
        """

        con = self.mapConsole
        libtcod.console_clear(con)
        level = self.game.currentLevel

        # draw the map tiles
        for tile in level.map.explored_tiles:
            if tile.blocked:
                # these are wall tiles
                if tile.inView:
                    # the player can see these
                    bg_color = COLOR_LIGHT_WALL
                else:
                    # these are out of sight
                    bg_color = COLOR_DARK_WALL
            else:
                # and these are floor tiles...
                if tile.inView:
                    bg_color = COLOR_LIGHT_GROUND
                else:
                    bg_color = COLOR_DARK_GROUND
            libtcod.console_set_char_background(
                con, tile.x, tile.y, bg_color, libtcod.BKGND_SET)

            # draw any actors standing on this tile.
            # includes Monsters and Portals
            for myActor in tile.actors:
                if myActor.visible:
                    actor_color = libtcod.white
                    # NOTE if the Actor base stores it's own color there is no
                    # need for type checking.
                    if type(myActor) is Actors.Portal:
                        actor_color = libtcod.purple
                    elif type(myActor) is Actors.Monster:
                        actor_color = libtcod.green
                    libtcod.console_set_default_foreground(con, actor_color)
                    libtcod.console_put_char(
                        con, tile.x, tile.y, myActor.char, libtcod.BKGND_NONE)

            #Redraw player character (makes sure it is on top)
            player = self.game.player
            libtcod.console_set_default_foreground(con, libtcod.white)
            libtcod.console_put_char(
                con, player.tile.x, player.tile.y,
                player.char, libtcod.BKGND_NONE)

        #blit the contents of "con" to the root console
        libtcod.console_blit(con, 0, 0, CONSTANTS.MAP_WIDTH, CONSTANTS.MAP_HEIGHT, 0, 0, 0)

        ##Notes on field of view
        ##
        ##Joe: Explain, the Fov is treated as a secondary map
        ##The question is do we wish to deal with it the same way?
        ##Ideally, if rooms are set before map is drawn, you save the
        ##generation of colors until inside FOV range, where you change
        ##the colors of them to match your final scheme, and then turn
        ##them back to the "shadowed" colors once player has set an
        ##"explored" option.
        ##NOTE Wesley:
        ##   I did this before in another project as handled by the Game.
        ##   After each move the Game does a look_around() and marks a monster
        ##   or tile as seen == True and in_range == True (if in fov).
        ##   Then we just draw tiles where seen, and monsters where in_range.
        ##   I will try add this tonight, it is pure python and simple and good
        ##   for learning how these things work :)

        #TODO medium: create a GUI panel
        #Frostlock: this needs some game message log first in the game logic
        panel = self.panelConsole
        libtcod.console_set_default_background(panel, libtcod.black)
        libtcod.console_clear(panel)

        ##print the game messages, one line at a time
        if self.messages is not None:
            y = 1
            for line in self.messages:
                libtcod.console_set_default_foreground(panel, libtcod.white)
                libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE,
                        libtcod.LEFT, line)
                y += 1

        if player is not None:
            #Player health bar
            self.renderBar(panel, 1, 1, BAR_WIDTH, 'HP',
                    player.currentHitPoints, player.maxHitPoints,
                    libtcod.dark_red, libtcod.darker_gray)
            #Player xp bar
            self.renderBar(panel, 1, 2, BAR_WIDTH, 'XP',
                    player.xp, player.nextLevelXp,
                    libtcod.darker_green, libtcod.darker_gray)
        if self.game.currentLevel is not None:
            #Dungeon level
            libtcod.console_print_ex(panel, 1, 3, libtcod.BKGND_NONE,
                    libtcod.LEFT, str(self.game.currentLevel.name))

        #TODO: display names of objects under the mouse
        # Frost: this would require running this loop constantly which is not
        # happening at the moment. Currently it pauses to wait for the player to
        # hit a key.
        #libtcod.console_set_default_foreground(panel, libtcod.light_gray)
        #libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE,
        #        libtcod.LEFT, get_names_under_mouse())

        #blit the contents of "panel" to the root console
        libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH,
                PANEL_HEIGHT, 0, 0, PANEL_Y)

    def renderBar(self, panel, x, y, total_width,
            name, value, maximum, bar_color, back_color):
        """
        Helper function to render interface bars
        """
        #render a bar (HP, experience, etc). first calculate the width of the bar
        bar_width = int(float(value) / maximum * total_width)

        #render the background first
        libtcod.console_set_default_background(panel, back_color)
        libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

        #now render the bar on top
        libtcod.console_set_default_background(panel, bar_color)
        if bar_width > 0:
            libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

        #finally, some centered text with the values
        libtcod.console_set_default_foreground(panel, libtcod.white)
        libtcod.console_print_ex(panel, x + total_width / 2, y,
                libtcod.BKGND_NONE, libtcod.CENTER,
                name + ': ' + str(value) + '/' + str(maximum))

    def handleKeys(self):
        key = libtcod.console_wait_for_keypress(True)
        #TODO: Remove in next libtcod version
        #Attention: dirty hack, bug in libtcod fires keypress twice...
        key = libtcod.console_wait_for_keypress(True)

        key_char = chr(key.c)

        if key.vk == libtcod.KEY_ESCAPE:
            return 'exit'
        if self.game.state == Game.PLAYING:
            player = self.game.player
            #movement keys
            if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
                player.tryMoveOrAttack(0, -1)
            elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
                player.tryMoveOrAttack(0, 1)
            elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
                player.tryMoveOrAttack(-1, 0)
            elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
                player.tryMoveOrAttack(1, 0)
            elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
                player.tryMoveOrAttack(-1, -1)
            elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
                player.tryMoveOrAttack(1, -1)
            elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
                player.tryMoveOrAttack(-1, 1)
            elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
                player.tryMoveOrAttack(1, 1)
            #portal keys
            elif key_char == '>':
                player.tryFollowPortalDown()
            elif key_char == '<':
                player.tryFollowPortalUp()
            #inventory
            elif key_char == 'i':
                self.showInventory()
            #interact
            elif key_char == ',':
                player.tryPickUp()
            # update field of vision
            self.game.currentLevel.map.updateFieldOfView(
                player.tile.x, player.tile.y)

#This is where it all starts!
if __name__ == '__main__':
    myApplication = ApplicationLibtcod()
    myApplication.showWelcomeScreen()
