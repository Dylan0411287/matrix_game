import sys
import pygame
from pathlib import Path

# Stage 1: Setting up the window

pygame.init()
screen = pygame.display.set_mode((1280,720)) # 1280 x 720 window
pygame.display.set_caption("Digital Rain")
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((0,3,0))
    pygame.display.flip()
    clock.tick(60)
