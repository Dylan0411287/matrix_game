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

trail_colour = (130, 255, 40)
pale_falloff = 2

def mix(a, b, f): # blending a to b with fraction f
    return tuple(round(a[i] + (b[i] - a[i]) * f) for i in range(3)) # rgb values for fade

def colour_shade(t):
    colour = mix(trail_colour, near_colour, t ** pale_falloff)
    brightness = min(1, t * 1.15)
    return mix((0,0,0), colour, brightness)

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

def make_window(fullscreen):
    if fullscreen:
        screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN) # make window fullscreen
    else:
        screen = pygame.display.set_mode((1280,720), pygame.RESIZABLE) # 1280 x 720 window
    pygame.mouse.set_visible(not fullscreen)
    return screen

def build(screen, char_size, prefill = False):
    # create everything that depends on screen and character size so we can regenrate for
    #diff settings
    font = pygame.font.Font(str(font_path), char_size)
    
    width, height = screen.get_size()
    cell_w = int(char_size * 0.8) # toggle the width and height of cell until the effect looks good
    cell_h = int(char_size * 1.15)
    cols = (width // cell_w) + 1
    rows = (height // cell_h) + 2 # extra rows and column for the ones that are cut off

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

    scanlines = build_scan(width, height)
    vignette = build_vignette(width, height)

    if prefill:
        for drop in drops:
            drop.y = random.uniform(-(0.3 * rows + 2), rows + drop.length)

    return font, cell_w, cell_h, cols, rows, grid, drops, glyph_cache, scanlines, vignette

def build_scan(width, height): # scan lines on crt monitors
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(0, height, 3):
        pygame.draw.line(surf, (0,0,0,200), (0, y+2), (width, y+2))
    return surf

def build_vignette(width, height): # viginette on crt monitor
    w, h = 160, 90 # make it smaller and then scale up depending on screen size
    small_vig = pygame.Surface((w, h), pygame.SRCALPHA)
    for x in range(w):
        for y in range(h):
            dx = (x - (w/2)) / (w-2) # distance from center (width)
            dy = (y - (h/2)) / (h-2) # distance from center (height)
            d = math.sqrt((dx * dx) + (dy * dy)) # radial distance
            strength = max(0, min(1, (d - 0.55) / 0.85)) # capped at 0 and 1
            small_vig.set_at((x, y), (0, 0, 0, int(strength * 190)))
    return pygame.transform.smoothscale(small_vig, (width, height))

# ------- setup -------

pygame.init()
clock = pygame.time.Clock()

fullscreen = False
speed_mult = 1
paused = False
crt_on = True

screen = make_window(fullscreen)# depending on screen size:
font, cell_w, cell_h, cols, rows, grid, drops, glyph_cache, scanlines, vignette = build(screen, char_size)

# -------- Pygame loop --------

while True:
    dt = clock.tick(60) / 1000 # seconds since last frame
    dt = min(dt, 0.05)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN: # now including speed up/down, space to pause, text size
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            elif event.key in (pygame.K_f, pygame.K_F11):
                fullscreen = not fullscreen
                screen = make_window(fullscreen)
                font, cell_w, cell_h, cols, rows, grid, drops, glyph_cache, scanlines, vignette = build(screen, char_size, prefill = True)
            elif event.key == pygame.K_SPACE:
                paused = not paused

            elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                speed_mult = min(4, speed_mult * 1.25)

            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                speed_mult = max(0.15, speed_mult / 1.25)

            elif event.key == pygame.K_RIGHTBRACKET:
                char_size = min(40, char_size + 2) # 2 size increase each time
                font, cell_w, cell_h, cols, rows, grid, drops, glyph_cache, scanlines, vignette = build(screen, char_size, prefill = True)

            elif event.key == pygame.K_LEFTBRACKET:
                char_size = max(10, char_size - 2)
                font, cell_w, cell_h, cols, rows, grid, drops, glyph_cache, scanlines, vignette = build(screen, char_size, prefill = True)

            elif event.key == pygame.K_c:
                crt_on = not crt_on

    if not paused:
        for drop in drops:
            before = math.floor(drop.y)
            drop.y += drop.speed * speed_mult * dt
            after = math.floor(drop.y)

            if after != before:
                if 0 <= after < rows:
                    grid[drop.col][after] = random.choice(glyphs)

            if drop.y - drop.length > rows:
                drop.reset(fresh = False)

        for _ in range(int(cols * rows * 0.005 * speed_mult) + 1): # glitches in random places for 0.5% of grid
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

    if crt_on:
        w,h = screen.get_size()
        small = pygame.transform.smoothscale(screen, (w // 6, h // 6)) # scale down to 1/6
        small = pygame.transform.smoothscale(small, (w // 12, h // 12)) # then down to 1/12 # steps is cleaner scale rather than too pixelated
        blur = pygame.transform.smoothscale(small, (w,h))
        screen.blit(blur, (0,0), special_flags=pygame.BLEND_ADD)

        screen.blit(scanlines, (0,0))
        screen.blit(vignette, (0,0))

    pygame.display.flip()
    pygame.display.set_caption(f"Digital Rain - {clock.get_fps():.0f} fps - speed x{speed_mult:.2f} - size {char_size}")
