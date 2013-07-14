#Module with reusable utility functions

#TODO easy: this module needs better documentation comments
# standardize functions names in this module (get rid of _)

#TODO medium: this module should be made PEP8 compliant
import random
import math
import CONSTANTS


# rolling a hitdie
def rollHitDie(hitdie):
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

def randomChoiceIndex(chances):
    """
    Returns the index of a random choice based on a list of chances.
    """
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

# This property is used by the message function to send game messages
# to the application where they can be shown.
_application = None


@property
def application():
    return _application


@application.setter
def application(myApp):
    _application = myApp


def message(text, category=None):
    """
    Utility function to deal with in game messages.
    arguments
        text - String representing the message
        category - String representing the category in which this message falls
    """
    #Not much implemented at the moment
    if category is None:
        #Default to console output
        print text
    elif category.upper() == "GAME":
        if application is not None:
            application.addMessage(text)
        else:
            print "GAME: " + text
    elif category.upper() == "AI":
        if CONSTANTS.SHOW_AI_LOGGING is True:
            print "AI: " + text
    else:
        #Default to console output
        print text

def registerEffect(effectColor, effectTiles):
    if application is not None:
        application.registerEffect(effectColor, effectTiles)
    
def clamp(n, minn, maxn):
    """
    This function returns the number n limited to the range min-max.
    It is meant to be used to keep coordinates withing the limites of the map.
    """
    #Hurray for readability ;-)
    return max(min(maxn, n), minn)


def distanceBetween(actor1, actor2):
    """
    Calculate the euclidian distance (straightline) between two actors.
    Arguments
        actor1 - First actor
        actor2 - Second actor
    """
    dx = actor1.tile.x - actor2.tile.x
    dy = actor1.tile.y - actor2.tile.y
    return math.sqrt(dx ** 2 + dy ** 2)


def distanceBetweenPoints(x, y, u, v):
    """
    Return the distance between two points (x, y) and (u, v).
    """

    dx = x - u
    dy = y - v
    return math.sqrt(dx ** 2 + dy ** 2)


def make_matrix(width, height, initial_value):
    """
    Returns a list of initial values that can be accessed like a 2D array:

        matrix[x][y]

    """

    return [[initial_value for y in range(0, height)] for x in range(0, width)]


def get_line_segments(x1, y1, x2, y2):
    """
    Returns a list of line segments that make up a line between two points.
    Returns [(x1, y1), (x2, y2), ...]

    Source: http://roguebasin.roguelikedevelopment.org/index.php?title=Bresenham%27s_Line_Algorithm

    """

    points = []
    issteep = abs(y2 - y1) > abs(x2 - x1)
    if issteep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    rev = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        rev = True
    deltax = x2 - x1
    deltay = abs(y2 - y1)
    error = int(deltax / 2)
    y = y1
    ystep = None
    if y1 < y2:
        ystep = 1
    else:
        ystep = -1
    for x in range(x1, x2 + 1):
        if issteep:
            points.append((y, x))
        else:
            points.append((x, y))
        error -= deltay
        if error < 0:
            y += ystep
            error += deltax
    # Reverse the list if the coordinates were reversed
    if rev:
        points.reverse()
    return points


def line_of_sight(matrix, x1, y1, x2, y2):
    """
    Returns True if there is line of sight between two points.
    Uses the matrix data to rely on blocking tiles.
    This is a matrix created with make_matrix().
    matrix values of 0 or False are not solid, 1 or True are solid.

    """

    segs = get_line_segments(x1, y1, x2, y2)
    hits = [matrix[x][y] for x, y in segs]
    amt = hits.count(True)
    # allow 1 case: if the final destination position is blocking
    return amt == 0 or (amt == 1 and matrix[x2][y2])


class GameError(Exception):
    """
    Simple error that can be raised in case there is a problem with the game.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
