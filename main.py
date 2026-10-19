import sys
import pygame
from pathlib import Path
import random
import math

# ------- Settings -------

base_dir = Path(__file__).parent
font_path = base_dir / "assets" / "fonts" / "NotoSansJP-Regular.ttf"

char_size = 18
katakana = "ｦｱｳｴｵｶｷｹｺｻｼｽｾｿﾀﾂﾃﾅﾆﾇﾈﾊﾋﾎﾏﾐﾑﾒﾓﾔﾕﾗﾘﾜ"
glyphs = list(katakana * 2 + "0123456789" + 'Z:・."=*+-<>¦|')

background = (0,3,0)
dim_green = (0,90,30)
highlighted = (230,255,220)
near_colour = (157, 255, 170)

speed_min, speed_max = 8, 22
length_min, length_max = 6, 34

show_grid = False
steps = 24 # turn the scores into a brightness level from 0 to 24

# ------- functions -------

def colour_shade(t):
    # corresponding colour for brightness t
    r = 20 * t * t # minimal red, max when t = 1
    g = 90 + 165 * t # green values, max when t = 1
    b = 20 + 20 * t # ranges from 40 to 80
    k = min(1, t * 1.15)
    return (round(r * k), round(g*k), round(b*k))

class Drop:
    def __init__(self, col, rows):
        self.col = col
        self.rows = rows
        self.reset(fresh = True)

    def reset(self, fresh):
        if fresh:
            self.y = (-random.random() * self.rows) * 1.5
        else: # once drop is off screen, repeat it but spawns lower so buffer isnt too long
            self.y = ((-random.random() * self.rows) * 0.6) - 2 
        self.speed = random.uniform(speed_min, speed_max)
        self.length = random.randint(length_min, max(length_min + 1, min(length_max, int(self.rows * 0.7))))
# self length is between min length, and max which is chosen from min length + 1, 
# or the minimum of max length and 70% of # of rows

# ------- setup -------

pygame.init()
screen = pygame.display.set_mode((1280,720)) # 1280 x 720 window
clock = pygame.time.Clock()
font = pygame.font.Font(str(font_path), char_size)

colours = []
for i in range(steps + 1):
    colours.append(colour_shade(i / steps))
colours.append(near_colour)
colours.append(highlighted)

glyph_cache = {} # store character and brightness level
for ch in set(glyphs):
    for level, colour in enumerate(colours):
        image = font.render(ch, True, colour).convert_alpha()
        glyph_cache[(ch, level)] = pygame.transform.flip(image, True, False)


width, height = screen.get_size()
cell_w = int(char_size * 0.8) # toggle the width and height of cell until the effect looks good
cell_h = int(char_size * 1.15)
cols = (width // cell_w) + 1
rows = (height // cell_h) + 2 # extra rows and column for the ones that are cut off

# create grid (OUTSIDE THE LOOP SO ONLY ONE UNIQUE GRID IS CREATED)
# if inside loop, basically the characters will keep changing every second

grid = [] # empty list for grid, selects a row, generates a random glyph for each row, appends
          # to the column list, so we have (# of columns) lists of (# of rows) glyphs, #
          # append to grid list, so grid[0] is 0th column/first one, grid[0][3]-4th char in col 0
for col in range(cols):
    column = []
    for row in range(rows):
        column.append(random.choice(glyphs))
    grid.append(column)

drops = []
for col in range(cols):
    count = 1 + (random.random() < 0.45) + (random.random() < 0.15)
    # every column gets one drop, 45% chance of 2 and 15% chance for 3
    for _ in range(count):
        drops.append(Drop(col, rows)) # create drop object for each count, append to drops list

# -------- Pygame loop --------

while True:
    dt = clock.tick(60) / 1000 # seconds since last frame
    dt = min(dt, 0.05)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()

    for drop in drops:
        before = math.floor(drop.y)
        drop.y += drop.speed * dt
        after = math.floor(drop.y)

        if after != before:
            if 0 <= after < rows:
                grid[drop.col][after] = random.choice(glyphs)

        if drop.y - drop.length > rows:
            drop.reset(fresh = False)

    for _ in range(int(cols * rows * 0.005) + 1): # glitches in random places for 0.5% of grid
        c = random.randrange(cols)
        r = random.randrange(rows)
        grid[c][r] = random.choice(glyphs) # replace some char in grid with another random char

    lit = {}
    for drop in drops:
        head_row = math.floor(drop.y)
        for k in range(drop.length):
            row = head_row - k
            if row < 0 or row >= rows:
                continue
            if k == 0:
                score = 3
            elif k == 1:
                score = 2
            else:
                t = 1 - (k / drop.length)
                score = (0.95 * t * t) + (0.05 * t)
                if score < 0.03:
                    continue

# ensure that only the brighter drops stay when drops overlap.
            key = (drop.col, row)
            if score > lit.get(key,0):
                lit[key] = score

    screen.fill(background)

    blits = []
    for (col,row), score in lit.items():
        if score == 3:
            level = steps + 2 # brightest
        elif score == 2:
            steps + 1 # one off brightest
        else:
            level = round(score * steps) # convert decimal scores into a integer step
        image = glyph_cache[(grid[col][row], level)]
        x = (col * cell_w) - (cell_w - image.get_width()) // 2 # centering the characters in cell
        y = (row * cell_h) - (cell_h - image.get_height()) // 2
        blits.append((image, (x, y)))
    screen.blits(blits, doreturn=False)

    pygame.display.flip()
    pygame.display.set_caption(f"Digital Rain - {clock.get_fps():.0f} fps")
