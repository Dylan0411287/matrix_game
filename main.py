import sys
import pygame
from pathlib import Path
import random
import math

# Setting up the window

base_dir = Path(__file__).parent
font_path = base_dir / "assets" / "fonts" / "NotoSansJP-Regular.ttf"

char_size = 18
background = (0,3,0)
green = (0, 255, 70)
dim_green = (0,90,30)
highlighted = (230,255,240)

drop_col = 32 # pull these both out to test
drop_speed = 12


katakana = "ｦｱｳｴｵｶｷｹｺｻｼｽｾｿﾀﾂﾃﾅﾆﾇﾈﾊﾋﾎﾏﾐﾑﾒﾓﾔﾕﾗﾘﾜ"
glyphs = list(katakana * 2 + "0123456789" + 'Z:・."=*+-<>¦|')

pygame.init()
screen = pygame.display.set_mode((1280,720)) # 1280 x 720 window
clock = pygame.time.Clock()

font = pygame.font.Font(str(font_path), char_size)

width, height = screen.get_size()
cell_w = int(char_size * 0.75) # toggle the width and height of cell until the effect looks good
cell_h = int(char_size * 1.05)
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
    if drop_y >= rows:
        drop_y = 0

    screen.fill(background)

    # display the grid
    for col in range(cols):
        for row in range(rows):
            char = grid[col][row]
            image = font.render(char, True, dim_green) # render grid
            screen.blit(image, (col*cell_w, row*cell_h)) # display each in correct col/row
    # still rendering in the loop which is not efficient, for eah character need to render
    # 60 times per second

    head_row = math.floor(drop_y)
    head_char = grid[drop_col][head_row]
    head_image = font.render(head_char, True, highlighted)
    screen.blit(head_image, (drop_col * cell_w, head_row * cell_h))

    pygame.display.flip()
    pygame.display.set_caption(f"Digital Rain - {clock.get_fps():.0f} fps")
