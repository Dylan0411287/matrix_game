import sys
import pygame
from pathlib import Path

# Stage 1: Setting up the window

base_dir = Path(__file__).parent
font_path = base_dir / "assets" / "fonts" / "NotoSansJP-Regular.ttf"

background = (0,3,0)
green = (0,255,70)

pygame.init()
screen = pygame.display.set_mode((1280,720)) # 1280 x 720 window
pygame.display.set_caption("Digital Rain")
clock = pygame.time.Clock()

font = pygame.font.Font(str(font_path), 48)
char_image = font.render("ｱ", True, green) # already have background colour
# char_string = font.render("ｦｱｳｴｵ", True, green)

while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(background)
    screen.blit(char_image, (600, 300))
    for index, char in enumerate("ｦｱｳｴｵ"): # get the index
        char_string = font.render(char, True, green) # turn each char into image
        screen.blit(char_string, (300, 300 + (index * 50))) # draw each image, 50 pix gap
    pygame.display.flip()
    clock.tick(60)
