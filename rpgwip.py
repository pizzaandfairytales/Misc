#!/usr/bin/python

#notes: maybe leave formulas up to init.txt

import libtcodpy as libtcod
import math
import textwrap
import shelve


#actual size of the window
SCREEN_WIDTH = 15
SCREEN_HEIGHT = 12

#size of the map
MAP_WIDTH = 15
MAP_HEIGHT = 12

LIMIT_FPS = 20  #20 frames-per-second maximum

class Map:
    def __init__(self, width, height, tiles, warps):
        self.width = width
        self.height = height
        self.tiles = tiles
        self.warps = warps

    def draw(self):
        for x in range(self.width):
            for y in range(self.height):
                libtcod.console_set_default_foreground(con, self.tiles[x][y].color)
                libtcod.console_put_char(con, x, y, self.tiles[x][y].char, libtcod.BKGND_NONE)

class Tile:
    #a tile of the map and its properties
    def __init__(self, name, char, red, green, blue, blocking):
        self.name = name
        self.char = char
        self.color = libtcod.Color(red, green, blue)
        self.blocking = blocking

class Warp:
    def __init__(self, dest, origin_x, origin_y, dest_x, dest_y):
        self.dest = dest
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.dest_x = dest_x
        self.dest_y = dest_y

class Object:
    #this is a generic object: the player, a monster, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, x, y, char, name, color, blocks=False):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks

    def move(self, dx, dy):
        #move by the given amount, if the destination is not blocked
        if not oob(self.x + dx, self.y + dy):
            if not is_blocked(self.x + dx, self.y + dy):
                self.x += dx
                self.y += dy

    def send_to_back(self):
        #make this object be drawn first, so all others appear above it if they're in the same tile.
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def draw(self):
        #set the color and then draw the character that represents this object at its position
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def warp(self):
        dest = ""
        dest_x = 0
        dest_y = 0
        warp = False
        for item in map.warps:
            if item.origin_x == self.x and item.origin_y == self.y:
                dest = item.dest
                dest_x = item.dest_x
                dest_y = item.dest_y
                warp = True
        if warp:
            clearscreen()
            parsemap(dest)
            self.x = dest_x
            self.y = dest_y

    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

def is_blocked(x, y):
    #first test the map tile
    if map.tiles[x][y].blocking:
        return True
    return False

def oob(x, y):
    if y < 0 or y >= map.height or x < 0 or x >= map.width:
        return True
    return False

def render_all():
    global map, player
    player.clear()
    map.draw()
    player.draw()
    libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)

def handle_keys():
    key = libtcod.console_wait_for_keypress(True)
    if key.vk == libtcod.KEY_ESCAPE:
        return True  #exit game
    if game_state == 'playing':
        if key.vk == libtcod.KEY_UP:
            player.move(0, -1)
        elif key.vk == libtcod.KEY_DOWN:
            player.move(0, 1)
        elif key.vk == libtcod.KEY_LEFT:
            player.move(-1, 0)
        elif key.vk == libtcod.KEY_RIGHT:
            player.move(1, 0)
        elif chr(key.c) == '.':
            player.warp()

def clearscreen():
    for x in range(SCREEN_WIDTH):
        for y in range(SCREEN_HEIGHT):
            libtcod.console_put_char(con, x, y, ' ', libtcod.BKGND_NONE)

def parsemap(file):
    global map
    f = open (("./data/maps/" + file), "r")
    width = int(f.readline())
    height = int(f.readline())
    f.readline()
    tiles = []
    expanded_2d = []
    for x in range (height):
        z = (f.readline()).split()
        # the maps are run-length encoded, we want to decompress and store in expanded
        expanded = []
        for element in z:
            asterisk = element.find('*')
            # if the asterisk isn't found, we just want to add 1 copy of this tile
            if asterisk == -1:
                expanded.append(element)
            else:
                # gets the number after the asterisk
                number = int(element[asterisk+1:])
                for n in range(number):
                    # removes the multiplication tail
                    element_cleaned = element[:asterisk]
                    # adds that block multiple times
                    expanded.append(element_cleaned)
        expanded_2d.append(expanded)

    for x in range(width):
        tilerow = []
        for y in range(height):
            path = "./data/tiles/" + expanded_2d[y][x] + ".txt"
            f2 = open(path, "r")
            char = (f2.readline())[0]
            red = int(f2.readline())
            green = int(f2.readline())
            blue = int(f2.readline())
            blocking = f2.readline()
            f2.close()
            if blocking == "blocking: yes" or blocking == "yes":
                blocking = True
            else:
                blocking = False
            tile = Tile(expanded_2d[y][x], char, red, green, blue, blocking)
            tilerow.append(tile)
        tiles.append(tilerow)

    f.readline()
    warps = []
    numWarps = int(f.readline())
    for x in range(numWarps):
        z = (f.readline()).split()
        warp = Warp(z[0], int(z[2]), int(z[3]), int(z[5]), int(z[6]))
        print z[2]
        print z[3]
        warps.append(warp)


    f.close()
    map = Map(width, height, tiles, warps)

def new_game():
    global player, inventory, party, game_state, map

    parsemap("map.txt")
    #libtcod.console_wait_for_keypress(True)
    #exit
    #create object representing the player
    player = Object(3, 5, '@', 'player', libtcod.Color(255,0,0), blocks=True)

    game_state = 'playing'
    inventory = []

def play_game():
    #main loop
    while not libtcod.console_is_window_closed():
        #render the screen
        render_all()
        libtcod.console_flush()
        exit = handle_keys()
        if exit:
            break

libtcod.console_set_custom_font('arial12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'RPG', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
#main_menu()
new_game()
play_game()
