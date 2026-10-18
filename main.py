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
highlighted = (230,255,240)
near_colour = (157, 255, 191)

drop_col = 32 # pull these both out to test
drop_speed = 12
drop_length = 25 # how many cells are lit at once 

show_grid = False

# ------- functions -------

def colour_shade(t):
    # corresponding colour for brightness t
    r = 20 * t * t # minimal red, max when t = 1
    g = 90 + 165 * t # green values, max when t = 1
    b = 40 + 40 * t # ranges from 40 to 80
    k = min(1, t * 1.15)
    return (round(r * k), round(g*k), round(b*k))

# ------- setup -------

pygame.init()
screen = pygame.display.set_mode((1280,720)) # 1280 x 720 window
clock = pygame.time.Clock()
font = pygame.font.Font(str(font_path), char_size)

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

drop_y = 0 # start highlighted at the top

# -------- Pygame loop --------

while True:
    dt = clock.tick(60) / 1000 # seconds since last frame
    dt = min(dt, 0.05)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()

    drop_y += drop_speed * dt # this gives us a drop that looks the same on devices running 
    # at 60 fps and at ones running maybe at 30 if slower, then drop_y will increase by more 
    # to keep the effect looking the same
    if drop_y - drop_length > rows: 
        drop_y = 0

    # draw background
    screen.fill(background)

    # display the grid
    if show_grid:
        for col in range(cols):
            for row in range(rows):
                char = grid[col][row] # grid is our data, we need to pull each entry and display it
                image = font.render(char, True, dim_green) # render grid
                screen.blit(image, (col*cell_w, row*cell_h)) # display each in correct col/row
        # still rendering in the loop which is not efficient, for eah character need to render
        # 60 times per second

    head_row = math.floor(drop_y)
    for k in range(drop_length):
        row = head_row - k
        if row < 0 or row >= rows:
            continue
        if k == 0:
            colour = highlighted # brightest
        if k == 1:
            colour = near_colour # one off brightest
        else:
            t = 1 - (k / drop_length) # use colourshade function to get colours for remaining rows
            colour = colour_shade((0.95 * t * t) + (0.05 * t)) # so the drop off is more abrupt
        image = font.render(grid[drop_col][row], True, colour)
        screen.blit(image, (drop_col*cell_w, row*cell_h))

    pygame.display.flip()
    pygame.display.set_caption(f"Digital Rain - {clock.get_fps():.0f} fps")
