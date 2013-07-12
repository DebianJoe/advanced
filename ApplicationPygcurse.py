#!/usr/bin/python

# This file contains a test implementation of the application class.
# This one is based on Pygcurse.

import pygcurse
import pygame

# You can import everything you need from module Game
# the Game module will chain load other modules
from Game import Game
from Game import Player
import Actors
import Maps
import CONSTANTS
import Utilities
import textwrap
import colors

#actual size of the window
SCREEN_WIDTH = 85
SCREEN_HEIGHT = 50

# the number of times to redraw the screen each second
LIMIT_FPS = 20
BAR_WIDTH = 20

# where the message panel lives on the screen as (x, y, w, h)
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MESSAGE_PANEL_REGION = (BAR_WIDTH + 2,
                        SCREEN_HEIGHT - PANEL_HEIGHT,
                        SCREEN_WIDTH - BAR_WIDTH - 2,
                        PANEL_HEIGHT)

MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 2

# draw the dungeon with these colors.
# dark tiles are out of the player's view.
# light tiles are illuminated by our torch.
COLOR_DARK_WALL = colors.darkest_gray
COLOR_DARK_GROUND = colors.darker_gray
COLOR_LIGHT_WALL = colors.darker_orange
COLOR_LIGHT_GROUND = colors.dark_orange


class ApplicationPygcurse():
    """
    This class represents a running instance of the application.
    It connects the game logic to the user interface.
    It is a test implementation of a GUI based on Pygcurse.
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

    def addMessage(self, new_msg):
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
        self.DEBUG_COUNT = 0
        #Initialize pygcurse
        self.win = pygcurse.PygcurseWindow(
            SCREEN_WIDTH, SCREEN_HEIGHT, fullscreen=False)
        pygame.display.set_caption('Crunchbang Project')

        # we will call win.update() manually after everything is drawn
        self.win.autoupdate = False

        #Prepare to receive messages from the game utilities
        #(this allows the utilities to send game messages to this application)
        self._messages = []
        Utilities.application = self

    def showMenu(self, header, options, width=20, height=10):
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

        #store the current view
        self.win.push_surface()

        # Show in the middle of the screen.
        menu_region = (
            self.win.centerx / 2,
            self.win.centery / 2 + (height / 2),
            width,
            height)

        # a list from a-n, where n is the length of our options
        hotkeys = [chr(ord('a') + i) for i in range(0, len(options))]

        # build a menu from the options list by prefixing each with a hotkey
        # then join them together with newlines.
        menu_choices = []
        for counter, option_text in enumerate(options):
            menu_choices.append('(%s) %s' % ((hotkeys[counter]), option_text))
        menu_choices = '\n'.join(menu_choices)

        # construct the menu as a textbox object. It recognizes newlines.
        # this guy draw a nice border for us too.
        
        #TODO: Frost: there is a problem here
        # the menu_region might be too small to contain all the menu items.
        # The height has to be calculated based on the number of menu items.
        # I think the showMessage function suffers from the same problem
        # (if you give it a really long text) 
        txt = pygcurse.PygcurseTextbox(
            self.win,
            region=menu_region,
            fgcolor=colors.white,
            bgcolor=colors.transparent,
            caption=header,
            text=menu_choices,
            margin=2,
            wrap=True,
            border='.')
        txt.update()

        # update the screen and handle keypresses
        self.win.update()
        menu_busy = True
        while menu_busy:
            key = pygcurse.waitforkeypress(LIMIT_FPS, True)
            if key == 'escape':
                return_value = None
                break
            if key in hotkeys:
                return_value = hotkeys.index(key)
                break

        #go back to the previous view
        self.win.pop_surface()
        
        return return_value
        
    def showMessage(self, header, message, width=20, height=10):
        """
        This function will show a pop up message in the middle of the screen.
        It waits for the user to acknowledge the message by hitting enter or
        escape
        """

        # store the current window for easy restore when we are done
        self.win.push_surface()

        # Show in the middle of the screen.
        menu_region = (
            self.win.centerx / 2,
            self.win.centery / 2 + (height / 2),
            width,
            height)

        textbox = pygcurse.PygcurseTextbox(
            self.win,
            region=menu_region,
            fgcolor=colors.white,
            bgcolor=colors.dark_sepia,
            caption=header,
            text=message,
            margin=2,
            wrap=True,
            border='.')

        # tell the textbox to draw itself onto our win canvas
        textbox.update()

        # update the screen and handle keypresses
        self.win.update()
        menu_busy = True
        result = ''
        while menu_busy:
            key = pygcurse.waitforkeypress(LIMIT_FPS)
            if key is None:
                result = 'Escape'
                break
            elif key == '\r':
                result = 'Enter'
                break

        # restore to original window
        self.win.pop_surface()
        return result

    def showWelcomeScreen(self):

        self.win.backgroundimage = pygame.image.load(
            './media/menu_background.png')
        menu_choices = ['Start a new game',
                        'Continue previous game',
                        'Go to debug mode',
                        'Quit'
                        ]
        show_menu = True
        while show_menu:
            choice = self.showMenu('Main menu', menu_choices, 36)
            #interpret choice
            if choice is None:
                show_menu = False
            if choice == 0:
                print "Start a new game"
                self.newGame()
                self.showGameScreen()
            elif choice == 1:
                if self._game is None:
                    self.showMessage('Notification', 'No game to continue', 36)
                else:
                    self.showGameScreen()
            elif choice == 2:  # quit
                print "Go to debug mode"
                self.showDebugScreen()
            elif choice == 3:
                print "Quiting"
                show_menu = False
        #self.win.backgroundimage = None

    def showDebugScreen(self):

        # note that the background image is still set from the welcome screen

        #store the current view
        self.win.push_surface()

        menu_choices = ['Run some test code!',
                        'Back',
                        ]
        show_menu = True
        while show_menu:
            choice = self.showMenu('Select debug option', menu_choices, 36)
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
                print "Back"
                show_menu = False
        self.win.pop_surface()

    def showGameScreen(self):
        #create a new window surface on top of whatever is currently shown
        self.win.push_surface()
        while True:
            self.renderAll()
            #handle keys and exit game if needed
            #this allows the player to play his turn
            if self.handleKeys() == 'exit':
                break

            #Let the game play a turn
            self.game.playTurn()
        #go back to the underlying window surface
        self.win.pop_surface()

    def useInventory(self):
        if self.game is not None and self.game.player is not None:
            header = "Select item to use, escape to cancel"
            width = 45
            options = []
            items = self.game.player.inventoryItems
            for item in items:
                options.append(item.name)
            selection = self.showMenu(header, options, width)
            if selection is not None:
                self.game.player.tryUseItem(items[selection])

    def dropInventory(self):
        if self.game is not None and self.game.player is not None:
            header = "Select item to drop, escape to cancel"
            width = 45
            options = []
            items = self.game.player.inventoryItems
            for item in items:
                options.append(item.name)
            selection = self.showMenu(header, options, width)
            if selection is not None:
                self.game.player.tryDropItem(items[selection])
                
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

        #myMap = Maps.TownMap(CONSTANTS.MAP_WIDTH, CONSTANTS.MAP_HEIGHT)
        #print myMap
        text = "this is a very long and useless text.this is a very long and useless text."
        self.showMessage("long test message", text)
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
        level = self.game.currentLevel
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
            self.win.putchar(' ', tile.x, tile.y, bgcolor=bg_color)

            # draw any actors standing on this tile.
            # includes Monsters and Portals
            for myActor in tile.actors:
                if myActor.inView:
                    actor_color = colors.white
                    # NOTE if the Actor base stores it's own color there is no
                    # need for type checking.
                    if type(myActor) is Actors.Portal:
                        actor_color = colors.purple
                    elif type(myActor) is Actors.Monster:
                        actor_color = colors.green
                    self.win.putchar(myActor.char, tile.x, tile.y)

            #Redraw player character (makes sure it is on top)
            player = self.game.player

            self.win.putchar(
                player.char, player.tile.x, player.tile.y, fgcolor=colors.white)

        # show game messages via a PygcurseTextbox.
        message_box = pygcurse.PygcurseTextbox(
            self.win,
            region=MESSAGE_PANEL_REGION,
            fgcolor=colors.white,
            bgcolor=colors.black,
            text='\n'.join(self.messages),
            wrap=True,
            border='basic',
            margin=0
            )
        message_box.update()

        if player is not None:
            #Player health bar
            self.renderBar(1, PANEL_Y + 1, BAR_WIDTH, 'HP',
                    player.currentHitPoints, player.maxHitPoints,
                    colors.dark_red, colors.darker_gray)
            #Player xp bar
            self.renderBar(1, PANEL_Y + 2, BAR_WIDTH, 'XP',
                    player.xp, player.nextLevelXp,
                    colors.darker_green, colors.darker_gray)
        if self.game.currentLevel is not None:
            #Dungeon level
            self.win.putchars(str(self.game.currentLevel.name), 2, 2)

        self.win.update()

        #TODO: display names of objects under the mouse
        # Frost: this would require running this loop constantly which is not
        # happening at the moment. Currently it pauses to wait for the player to
        # hit a key.

    def renderBar(self, x, y, total_width,
            name, value, maximum, bar_color, back_color):
        """
        Helper function to render interface bars
        """
        # render a bar (HP, experience, etc). first calculate the width of the bar
        bar_width = int(float(value) / maximum * total_width)

        for idx in range(0, total_width):
            # use the bar_color while the index is inside the bar_width
            the_color = bar_color if idx <= bar_width else back_color
            self.win.putchar(' ', x + idx, y, bgcolor=the_color)

        # finally, some centered text with the values
        title = '%s: %s/%s' % (name, value, maximum)
        center = total_width - len(title) / 2
        self.win.putchars(title, x, y,
            fgcolor=colors.white, bgcolor=None)

    def handleKeys(self):
        """
        Handle any keyboard presses.
        """

        key = pygcurse.waitforkeypress(LIMIT_FPS, True)
        if key == 'escape':
            return 'exit'

        # this defines all they movement keys we can handle.
        # it supports various layouts: vi keys, keypad, arrows
        movement_keys = {
                    'h': (-1, +0),       # vi keys
                    'l': (+1, +0),
                    'j': (+0, +1),
                    'k': (+0, -1),
                    'y': (-1, -1),
                    'u': (+1, -1),
                    'b': (-1, +1),
                    'n': (+1, +1),
                    '[4]': (-1, +0),     # numerical keypad
                    '[6]': (+1, +0),
                    '[2]': (+0, +1),
                    '[8]': (+0, -1),
                    '[7]': (-1, -1),
                    '[9]': (+1, -1),
                    '[1]': (-1, +1),
                    '[3]': (+1, +1),
                    'left': (-1, +0),    # arrows and pgup/dn keys
                    'right': (+1, +0),
                    'down': (+0, +1),
                    'up': (+0, -1),
                    'home': (-1, -1),
                    'pageup': (+1, -1),
                    'end': (-1, +1),
                    'pagedown': (+1, +1),
                    }

        if self.game.state == Game.PLAYING:
            player = self.game.player

            # movement
            if key in movement_keys:
                # the * here is Python syntax to unpack a list.
                # this allows us to pass a list as parameters.
                # http://docs.python.org/2/tutorial/controlflow.html#unpacking-argument-lists
                player.tryMoveOrAttack(*movement_keys[key])

            #portal keys
            elif key == '>':
                player.tryFollowPortalDown()
                # clear characters
                self.win.setscreencolors(clear=True)
            elif key == '<':
                player.tryFollowPortalUp()
                # clear characters
                self.win.setscreencolors(clear=True)
            #inventory
            elif key == 'i':
                self.useInventory()
            elif key == 'd':
                self.dropInventory()
            #interact
            elif key == ',':
                player.tryPickUp()
                
            # update field of vision
            self.game.currentLevel.map.updateFieldOfView(
                player.tile.x, player.tile.y)

#This is where it all starts!
if __name__ == '__main__':
    myApplication = ApplicationPygcurse()
    myApplication.showWelcomeScreen()
