
import pygame as pg
import sys
import random
from game.utils import load_images, read_image
from game.settings import *
from game.simulate_world import create_iso_world, generate_perlin_noise_2d

# Create world tiles
tiles = create_iso_world((256, 256), (8, 8), "radial")

pg.init()
pg.mixer.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

#variables
tide_coming_in = True
tide_gain = 0.05
scale = 1
scale_factor = 0.5
images = load_images(scale)

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
        for tile in tiles:
            tile['iso_topleft'][1] += TILE_SIZE
    if down:
        for tile in tiles:
            tile['iso_topleft'][1] -= TILE_SIZE
    if left:
        for tile in tiles:
            tile['iso_topleft'][0] += TILE_SIZE
    if right:
        for tile in tiles:
            tile['iso_topleft'][0] -= TILE_SIZE

    # Zoom in feature
    if zoom_in:

        # Platforms
        for tile in tiles:
            dx = (screen.get_width()/2 - tile['iso_topleft'][0]) * scale_factor
            dy = (screen.get_height()/2 - tile['iso_topleft'][1]) * scale_factor

            tile['iso_topleft'][0] -= dx
            tile['iso_topleft'][1] -= dy

        scale = scale * (1 + scale_factor)
        images = load_images(scale)

    # zoom out feature
    if zoom_out:

        # Platforms
        for tile in tiles:
            dx = (screen.get_width()/2 - tile['iso_topleft'][0]) * -scale_factor
            dy = (screen.get_height()/2 - tile['iso_topleft'][1]) * -scale_factor

            tile['iso_topleft'][0] -= dx
            tile['iso_topleft'][1] -= dy

        scale = scale * (1 - scale_factor)
        images = load_images(scale)

    # Draw section
    screen.fill((255, 255, 255))

    for tile in tiles:

        blit_pos = tile['iso_topleft'].copy()
        tile_image = tile['new_tile_type']

        screen.blit(images[tile_image], blit_pos)

    pg.display.flip()
