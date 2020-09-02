
import pygame as pg
import sys
import random
from game.utils import read_image
from game.settings import *
from game.simulate_world import create_iso_world, generate_perlin_noise_2d

pg.init()
pg.mixer.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

# Create world tiles
world_surfaces = create_iso_world(screen, (150, 150), (5, 5), "radial")

#variables
tide_coming_in = True
tide_gain = 0.05
zoom_level = 0
blit_pos = [0, 0]


while True:

    clock.tick(60)

    # Events
    pressed = pg.key.get_pressed()
    event = pg.event.wait()
    game_exit = event.type == pg.QUIT

    if game_exit:
        pg.quit()
        sys.exit()

    up = pressed[pg.K_UP]
    down = pressed[pg.K_DOWN]
    left = pressed[pg.K_LEFT]
    right = pressed[pg.K_RIGHT]
    mouse_pos = pg.mouse.get_pos()
    zoom_in = pressed[pg.K_z]
    zoom_out = pressed[pg.K_x]

    if up:
        blit_pos[1] += TILE_SIZE
    if down:
        blit_pos[1] -= TILE_SIZE
    if left:
        blit_pos[0] += TILE_SIZE
    if right:
        blit_pos[0] -= TILE_SIZE

    # # Zoom feature
    if zoom_in:
        if zoom_level > 0: zoom_level -= 1
    if zoom_out:
        if zoom_level < 3: zoom_level += 1

    # Draw section
    screen.fill((255, 255, 255))

    screen.blit(world_surfaces[zoom_level], blit_pos)

    pg.display.flip()
