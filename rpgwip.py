#!/usr/bin/python

import libtcodpy as libtcod
import math
import shelve

view_x = 10
view_y = 9

LIMIT_FPS = 20  #20 frames-per-second maximum

class Map:
    def __init__(self, width, height, tiles, warps):
        self.width = width
        self.height = height
        self.tiles = tiles
        self.warps = warps

    def draw(self, player_x, player_y, view_x, view_y):
        horizontal = int(view_x / 2)
        vertical = int(view_y / 2)
        for y in range(view_y):
            for x in range(view_x):
                if ((player_x - horizontal) + x < 0) or ((player_x - horizontal) + x >= self.width) or ((player_y - vertical) + y < 0) or ((player_y - vertical) + y >= self.height):
                    tile = Tile("blank", ' ', 0, 0, 0, False, [])
                else:
                    col = (player_x - horizontal) + x
                    row = (player_y - vertical) + y
                    tile = self.tiles[col][row]
                libtcod.console_set_default_foreground(con, tile.color)
                libtcod.console_put_char(con, x, y, tile.char, libtcod.BKGND_SET)

class Tile:
    #a tile of the map and its properties
    def __init__(self, name, char, red, green, blue, blocking, interact_text):
        self.name = name
        self.char = char
        self.color = libtcod.Color(red, green, blue)
        self.blocking = blocking
        self.interact_text = interact_text

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
    def __init__(self, x, y, char, name, color, blocks=False, dir="none"):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks
        self.dir = dir

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
        libtcod.console_put_char(con, view_x/2, view_y/2, self.char, libtcod.BKGND_SET)

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

    def interact(self):
        dest_x = self.x
        dest_y = self.y
        if self.dir == "up":
            dest_y -= 1
        elif self.dir == "down":
            dest_y += 1
        elif self.dir == "left":
            dest_x -= 1
        elif self.dir == "right":
            dest_x += 1
        if not oob(dest_x, dest_y):
            interact_list = map.tiles[dest_x][dest_y].interact_text
            if interact_list != []:
                display_text(interact_list[0])

    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_SET)

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
    map.draw(player.x, player.y, view_x, view_y)
    player.draw()
    libtcod.console_blit(con, 0, 0, view_x, view_y, 0, 0, 0)

def handle_keys():
    key = libtcod.console_wait_for_keypress(True)
    if key.vk == libtcod.KEY_ESCAPE:
        return True  #exit game
    if game_state == 'playing':
        if key.vk == libtcod.KEY_UP:
            player.dir = "up"
            player.move(0, -1)
        elif key.vk == libtcod.KEY_DOWN:
            player.dir = "down"
            player.move(0, 1)
        elif key.vk == libtcod.KEY_LEFT:
            player.dir = "left"
            player.move(-1, 0)
        elif key.vk == libtcod.KEY_RIGHT:
            player.dir = "right"
            player.move(1, 0)
        elif key.vk == libtcod.KEY_ENTER:
            choice = menu("Menu", ["Save", "Load", "Cancel"])
            if choice == 0:
                save_game()
            if choice == 1:
                try:
                    load_game()
                except:
                    display_text("No save file found!")
        elif chr(key.c) == '.':
            player.warp()
        elif chr(key.c) == 'z':
            player.interact()
        #print player.dir

def save_game():
    f = shelve.open('save', 'n')
    f['map'] = map
    f['player'] = player
    f.close()

def load_game():
    global map, player
    f = shelve.open('save', 'r')
    map = f['map']
    player = f['player']
    f.close()

def clearscreen():
    for x in range(view_x):
        for y in range(view_y):
            libtcod.console_put_char(con, x, y, ' ', libtcod.BKGND_SET)

def parsemap(file):
    global map
    f = open ((game_dir + "/maps/" + file), "r")
    skipline(f)
    width = int(f.readline())
    height = int(f.readline())
    skipline(f)
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
            path = game_dir + "/tiles/" + expanded_2d[y][x] + ".txt"
            f2 = open(path, "r")
            skipline(f2)
            char = (f2.readline())[0]
            skipline(f2)
            red = int(f2.readline())
            green = int(f2.readline())
            blue = int(f2.readline())
            skipline(f2)
            blocking = f2.readline()
            skipline(f2)
            interact_num = int(f2.readline())
            interact_text = []
            for a in range (interact_num):
                interact_text.append(f2.readline())
            f2.close()
            if blocking == "yes" or blocking == "yes\n":
                blocking = True
            else:
                blocking = False
            tile = Tile(expanded_2d[y][x], char, red, green, blue, blocking, interact_text)
            tilerow.append(tile)
        tiles.append(tilerow)
    skipline(f)
    warps = []
    numWarps = int(f.readline())
    for x in range(numWarps):
        z = (f.readline()).split()
        warp = Warp(z[0], int(z[2]), int(z[3]), int(z[5]), int(z[6]))
        warps.append(warp)
    f.close()
    map = Map(width, height, tiles, warps)

# I made this function just to make it clearer what's going on when I call readline but don't store the value.
# This will also make it easier to find / remove those calls, if I decide to remove comment lines from the file formats.
def skipline(file, numlines=1):
    for x in range(numlines):
        file.readline()

def menu(caption, options):
    clearscreen()
    libtcod.console_set_default_foreground(con, text_color)
    page = 0
    choice = -1
    # The caption takes up a row, and the next-previous page options also each take 1, hence the 3
    options_per_page = view_y - 3
    # We want to select options with the num keys, so, saving room for a next and previous key, we can have at most 8 options per page
    if options_per_page > 8:
        options_per_page = 8
    num_pages = int(math.ceil(len(options) / options_per_page))
    while choice == -1:
        x_pos = 0
        y_pos = 0
        clearscreen()
        for char in caption:
            libtcod.console_put_char(con, x_pos, y_pos, char, libtcod.BKGND_SET)
            x_pos += 1
        y_pos += 1
        x_pos = 0
        for x in range(options_per_page):
            current_option = page*options_per_page + x
            if not current_option >= len(options):
                libtcod.console_put_char(con, x_pos, y_pos, str(x + 1), libtcod.BKGND_SET)
                x_pos += 1
                libtcod.console_put_char(con, x_pos, y_pos, ' ', libtcod.BKGND_SET)
                x_pos += 1
                for char in options[page*options_per_page + x]:
                    libtcod.console_put_char(con, x_pos, y_pos, char, libtcod.BKGND_SET)
                    x_pos += 1
            y_pos += 1
            x_pos = 0
        if page != 0:
            y_pos = view_y - 2
            libtcod.console_put_char(con, x_pos, y_pos, '9', libtcod.BKGND_SET)
            x_pos += 1
            libtcod.console_put_char(con, x_pos, y_pos, ' ', libtcod.BKGND_SET)
            x_pos += 1
            for char in "Prev":
                libtcod.console_put_char(con, x_pos, y_pos, char, libtcod.BKGND_SET)
                x_pos += 1
        if page < num_pages:
            x_pos = 0
            y_pos = view_y - 1
            libtcod.console_put_char(con, x_pos, y_pos, '0', libtcod.BKGND_SET)
            x_pos += 1
            libtcod.console_put_char(con, x_pos, y_pos, ' ', libtcod.BKGND_SET)
            x_pos += 1
            for char in "Next":
                libtcod.console_put_char(con, x_pos, y_pos, char, libtcod.BKGND_SET)
                x_pos += 1
        libtcod.console_blit(con, 0, 0, view_x, view_y, 0, 0, 0)
        libtcod.console_flush()
        key = libtcod.console_wait_for_keypress(True)
        if int(key.c) >=48 and int(key.c) <= 57:
            if int(chr(key.c)) > 0 and int(chr(key.c)) <= options_per_page:
                try_choice = page*options_per_page + (int(chr(key.c)) - 1)
                if try_choice < len(options):
                    choice = try_choice
            elif int(chr(key.c)) == 9 and page != 0:
                page -= 1
            elif int(chr(key.c)) == 0 and page < num_pages - 1:
                page += 1
    return choice

def display_text(text):
    clearscreen()
    libtcod.console_set_default_foreground(con, text_color)
    x_pos = 0
    y_pos = 0
    wordlist = text.split()
    for word in wordlist:
        # If the word can fit on the current line, display it
        if word == "\\":
            y_pos += 2
            x_pos = 0
            if y_pos == view_y:
                libtcod.console_blit(con, 0, 0, view_x, view_y, 0, 0, 0)
                libtcod.console_flush()
                key = libtcod.console_wait_for_keypress(True)
                clearscreen()
                y_pos = 0
        elif len(word) <= view_x - x_pos:
            for char in word:
                libtcod.console_put_char(con, x_pos, y_pos, char, libtcod.BKGND_SET)
                x_pos += 1
            if x_pos < view_x - 1:
                libtcod.console_put_char(con, x_pos, y_pos, ' ', libtcod.BKGND_SET)
                x_pos += 1
        # If the word is too big to fit on even a blank line, we'll need to break it up across several using dashes.
        elif len(word) > view_x:
            curr = 0
            while curr < len(word):
                if x_pos < view_x - 1:
                    libtcod.console_put_char(con, x_pos, y_pos, word[curr], libtcod.BKGND_SET)
                    x_pos += 1
                    curr += 1
                else:
                    libtcod.console_put_char(con, x_pos, y_pos, '-', libtcod.BKGND_SET)
                    y_pos += 1
                    x_pos = 0
                # If we've used up the whole screen, wait for the user to press a key, then start a new page
                if y_pos == view_y:
                    libtcod.console_blit(con, 0, 0, view_x, view_y, 0, 0, 0)
                    libtcod.console_flush()
                    key = libtcod.console_wait_for_keypress(True)
                    clearscreen()
                    y_pos = 0
            if x_pos < view_x - 1:
                libtcod.console_put_char(con, x_pos, y_pos, ' ', libtcod.BKGND_SET)
                x_pos += 1
        # The last option is a word that can't fit on the current line, but could fit on an empty one.
        # In that case, we want to go to a new line (or new page if needed), then copy the logic from the "it already fits" case.
        else:
            # newline
            y_pos += 1
            if y_pos == view_y:
                libtcod.console_blit(con, 0, 0, view_x, view_y, 0, 0, 0)
                libtcod.console_flush()
                key = libtcod.console_wait_for_keypress(True)
                clearscreen()
                y_pos = 0
            x_pos = 0
            for char in word:
                libtcod.console_put_char(con, x_pos, y_pos, char, libtcod.BKGND_SET)
                x_pos += 1
            if x_pos < view_x - 1:
                libtcod.console_put_char(con, x_pos, y_pos, ' ', libtcod.BKGND_SET)
                x_pos += 1
        # Uncomment these to make the player have to step through by word instead of by page.
        #libtcod.console_blit(con, 0, 0, view_x, view_y, 0, 0, 0)
        #libtcod.console_flush()
        #key = libtcod.console_wait_for_keypress(True)
    # Finally, we want the player to press a key to exit the text.
    libtcod.console_blit(con, 0, 0, view_x, view_y, 0, 0, 0)
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

def new_game():
    global player, inventory, party, game_state, map, view_x, view_y, con, game_dir, text_color
    f = open("./init.txt", "r")
    skipline(f)
    game_dir = (f.readline())
    f.close()
    # We need to get the screen size (and eventually we'll get other game data here as well)
    f = open(game_dir + "/init.txt", "r")
    # game name is line 2 of these, in case I want to do something with it
    skipline(f, 3)
    welcome_text = f.readline()
    skipline(f)
    red = int(f.readline())
    green = int(f.readline())
    blue = int(f.readline())
    skipline(f)
    text_color = libtcod.Color(int(f.readline()), int(f.readline()), int(f.readline()))
    skipline(f)
    view_x = int(f.readline())
    view_y = int(f.readline())
    skipline(f)
    map = (f.readline())[:-1]
    skipline(f)
    start_x = int(f.readline())
    start_y = int(f.readline())
    f.close()
    parsemap(map)
    # Boilerplate to set up the window
    libtcod.console_set_custom_font('dejavu16x16_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(view_x, view_y, 'RPG', False)
    libtcod.sys_set_fps(LIMIT_FPS)
    con = libtcod.console_new(view_x, view_y)
    libtcod.console_set_default_background(con,libtcod.Color(red, green, blue))
    display_text(welcome_text)
    # Initialize the player -
    player = Object(start_x, start_y, '@', 'player', libtcod.Color(255,0,0), blocks=True, dir="up")
    game_state = 'playing'
    inventory = []

def play_game():
    # Game loop
    while not libtcod.console_is_window_closed():
        # Draw the screen
        render_all()
        libtcod.console_flush()
        # Player input
        exit = handle_keys()
        if exit:
            break

# Program entry point:
new_game()
play_game()
