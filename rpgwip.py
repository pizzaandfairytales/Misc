#!/usr/bin/python

import libtcodpy as libtcod
import math
import shelve
from pygame import mixer

class Map:
    def __init__(self, width, height, tiles, warps, music, triggers):
        self.width = width
        self.height = height
        self.tiles = tiles
        self.warps = warps
        self.music = music
        self.triggers = triggers

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

    def draw(self):
        #set the color and then draw the character that represents this object at its position
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, view_x/2, view_y/2, self.char, libtcod.BKGND_SET)

    def warp(self):
        dest = ""
        dest_x = 0
        dest_y = 0
        old_music = map.music
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
            if map.music != old_music:
                    if map.music != "none":
                        mixer.music.load(map.music)
                        mixer.music.play(-1)
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
            check_trigger(dest_x, dest_y, "interaction")

    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_SET)

class Player(Object):
    def __init__(self, x, y, char, name, color, party, items, blocks=False, dir="none"):
        Object.__init__(self, x, y, char, name, color, blocks, dir)
        self.party = party
        self.items = items

class Monster:
    def __init__(self, species, level, ev, iv, exp):
        self.species = species
        self.level = level
        self.ev = ev
        self.iv = iv
        self.exp = exp
        f = open("/monsters/" + species.lower() + ".txt")
        skipline(13)
        base_hp = f.readline()[1]
        base_attack = f.readline()[1]
        base_defense = f.readline()[1]
        base_sp_atk = f.readline()[1]
        base_sp_defense = f.readline()[1]
        base_speed = f.readline()[1]
        f.close()

    def calc_stats():
        self.hp = (((self.base_hp + self.iv[0])*2+(math.sqrt(self.ev[0])/4)*self.level)/100) + self.level + 10
        self.attack = (((self.base_attack + self.iv[1]) * 2 + (math.sqrt(self.ev[1])/4)*self.level)/100) + 5
        self.defense = (((self.base_defense + self.iv[2]) * 2 + (math.sqrt(self.ev[2])/4)*self.level)/100) + 5
        self.sp_atk = (((elf.base_sp_atk + self.iv[3]) * 2 + (math.sqrt(self.ev[3])/4)*self.level)/100) + 5
        self.sp_defense = (((self.base_sp_defense + self.iv[4]) * 2 + (math.sqrt(self.ev[4])/4)*self.level)/100) + 5
        self.speed = (((elf.base_speed + self.iv[5]) * 2 + (math.sqrt(self.ev[5])/4)*self.level)/100) + 5

class Trigger:
    def __init__(self, x, y, style, action, argument):
        self.x = x
        self.y = y
        self.action = action
        self.argument = argument
        self.style = style

def trigger(action, argument):
    if action == "display_text":
        display_text(argument)
    if action == "warp":
        argumentList = argument.split()
        warp_to(argumentList[0], int(argumentList[2]), int(argumentList[4]))

def warp_to(map, x, y):
    parsemap(map)
    player.x = x
    player.y = y

def check_trigger(x, y, style):
    for entry in map.triggers:
        if entry.style == style:
            if entry.x == x and entry.y == y:
                trigger(entry.action, entry.argument)

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
    global music_paused
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
            choice = menu("Menu", ["Save", "Load", "MainMenu", "Cancel"])
            if choice == 0:
                save_game()
            if choice == 1:
                try:
                    load_game()
                except:
                    display_text("No save file found!")
            if choice == 2:
                new_game()
        elif chr(key.c) == 'x':
            player.warp()
        elif chr(key.c) == 'z':
            player.interact()
        elif chr(key.c) == 'q':
            vol = mixer.music.get_volume()
            if vol >= .1:
                mixer.music.set_volume(vol - .1)
        elif chr(key.c) == 'w':
            vol = mixer.music.get_volume()
            if vol <= .9:
                mixer.music.set_volume(vol + .1)
        elif chr(key.c) == 'e':
            if not music_paused:
                mixer.music.pause()
                music_paused = True
            else:
                mixer.music.unpause()
                music_paused = False
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
    if map.music != "none":
        mixer.music.load(map.music)
        mixer.music.play(-1)
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
    skipline(f)
    song = (f.readline()).rstrip()
    if song == "none":
        song_path = song
    else:
        song_path = game_dir + "/sound/music/" + song
    # Read Location Triggers
    skipline(f)
    triggers = []
    numLocTriggers = int(f.readline())
    for x in range (numLocTriggers):
        trigger = (f.readline()).split()
        triggerArg = f.readline()
        triggers.append(Trigger(int(trigger[1]), int(trigger[3]), "location", trigger[5], triggerArg))
    # Read Interaction Triggers
    skipline(f)
    interactTriggers = []
    numInteractTriggers = int(f.readline())
    for x in range (numInteractTriggers):
        trigger = (f.readline()).split()
        triggerArg = f.readline()
        triggers.append(Trigger(int(trigger[1]), int(trigger[3]), "interaction", trigger[5], triggerArg))
    f.close()
    map = Map(width, height, tiles, warps, song_path, triggers)

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
    # Until the user picks a valid menu option (not navigation)
    while choice == -1:
        x_pos = 0
        y_pos = 0
        clearscreen()
        # Display menu caption at the top
        for char in caption:
            libtcod.console_put_char(con, x_pos, y_pos, char, libtcod.BKGND_SET)
            x_pos += 1
        y_pos += 1
        x_pos = 0
        # Display a page of options
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
        # As long as we're not at the first page, we want to have a back button
        if page != 0:
            y_pos = view_y - 2
            libtcod.console_put_char(con, x_pos, y_pos, '9', libtcod.BKGND_SET)
            x_pos += 1
            libtcod.console_put_char(con, x_pos, y_pos, ' ', libtcod.BKGND_SET)
            x_pos += 1
            for char in "Prev":
                libtcod.console_put_char(con, x_pos, y_pos, char, libtcod.BKGND_SET)
                x_pos += 1
        # As long as we're not at the last page, we want to have a forwards button
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
        # Render all of that to the screen
        libtcod.console_blit(con, 0, 0, view_x, view_y, 0, 0, 0)
        libtcod.console_flush()
        # Wait for input
        key = libtcod.console_wait_for_keypress(True)
        # These are the ascii codes for 1-9
        if int(key.c) >= 48 and int(key.c) <= 57:
            # If the inputted number is a valid option:
            if int(chr(key.c)) > 0 and int(chr(key.c)) <= options_per_page:
                try_choice = page*options_per_page + (int(chr(key.c)) - 1)
                if try_choice < len(options):
                    # Then the user has successfully made a choice.
                    choice = try_choice
            # Navigate to previous page
            elif int(chr(key.c)) == 9 and page != 0:
                page -= 1
            # Navigate to next page
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
    global player, inventory, party, game_state, map, view_x, view_y, con, game_dir, text_color, music_paused
    music_paused = False
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
    map = (f.readline()).rstrip()
    skipline(f)
    start_x = int(f.readline())
    start_y = int(f.readline())
    skipline(f)
    player_color = libtcod.Color(int(f.readline()), int(f.readline()), int(f.readline()))
    f.close()
    parsemap(map)
    # Boilerplate to set up the window
    LIMIT_FPS = 20  #20 frames-per-second maximum
    libtcod.console_set_custom_font('dejavu16x16_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(view_x, view_y, 'RPG', False)
    libtcod.sys_set_fps(LIMIT_FPS)
    con = libtcod.console_new(view_x, view_y)
    libtcod.console_set_default_background(con,libtcod.Color(red, green, blue))
    continue_game = menu("File:", ["New", "Continue"])
    mixer.init()
    if continue_game == 1:
        try:
            load_game()
        except:
            display_text("No save file found! Starting new game...")
            continue_game = 0
    if not continue_game:
        display_text(welcome_text)
        # Initialize the player -
        player = Player(start_x, start_y, '@', 'player', player_color, [], [], blocks=True, dir="up")
    print map.music
    if map.music != "none":
        mixer.music.load(map.music)
        mixer.music.set_volume(.5)
        mixer.music.play(-1)
    game_state = 'playing'

def play_game():
    # Game loop
    while not libtcod.console_is_window_closed():
        # Draw the screen
        render_all()
        libtcod.console_flush()
        # Check for Location Trigger activation
        # Player input
        exit = handle_keys()
        if exit:
            break
        check_trigger(player.x, player.y, "location")

# Program entry point:
new_game()
play_game()
