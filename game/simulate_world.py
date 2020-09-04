
import pygame as pg
import numpy as np
import math
import random
from game.settings import *
from game.utils import cart_to_iso, load_images


def create_iso_world(screen, shape, res, gradient='radial'):

    # Import images
    scale = 1
    scale_factor = 0.5
    images = load_images(scale)

    # Simulate sea level
    sea_level_world = generate_radial_gradient(shape, res)

    # Simulate temperature
    temp_world = generate_temperature_gradient(shape, res)

    # Create isometric tiles
    tiles = []
    for x in range(shape[0]):
        for y in range(shape[1]):

            surf = pg.Surface((TILE_SIZE, TILE_SIZE))
            rect = surf.get_rect(topleft = (x*TILE_SIZE, y*TILE_SIZE))
            corners = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]
            iso_corners = [cart_to_iso(pos[0], pos[1], OFFSET) for pos in corners]

            minx = min([corner[0] for corner in iso_corners])
            miny = min([corner[1] for corner in iso_corners])
            maxx = max([corner[0] for corner in iso_corners])
            maxy = max([corner[1] for corner in iso_corners])

            iso_topleft = [minx, miny]
            iso_bottomright = [maxx, maxy]

            sea_level_val = sea_level_world[x][y]
            temp_val = temp_world[x][y]

            if sea_level_val < 40:
                if random.randint(1, 100) == 1:
                    tile_type = 'deep_water_rock_tile_NE'
                else:
                    tile_type = 'deep_water_tile_NE'
            elif sea_level_val < 50:
                tile_type = 'water_tile_NE'
            elif sea_level_val < 60:
                rand = random.randint(1, 100)
                if rand < 97:
                    tile_type = 'sand_tile_NE'
                else:
                    tile_type = 'tree_palm_NE'
            elif sea_level_val < 80:
                rand = random.randint(1, 100)
                if rand < 95:
                    tile_type = 'ground_grass_NE'
                elif rand < 97:
                    tile_type = 'tree_plateau_dark_NE'
                else:
                    tile_type = 'tree_pineTallD_NW'
            else:
                rand = random.randint(1, 100)
                if rand < 85:
                    tile_type = 'ground_grass_NE'
                elif rand < 90:
                    tile_type = 'tree_plateau_dark_NE'
                else:
                    tile_type = 'tree_pineTallD_NW'

            tiles.append({
                        'pos': [x, y],
                        'orig_tile_type': tile_type,
                        'new_tile_type': tile_type,
                        'rect': rect,
                        'corners': corners,
                        'iso_corners': iso_corners,
                        'sea_level_val': sea_level_val,
                        'iso_topleft': iso_topleft,
                        'iso_bottomright': iso_bottomright})

    maxx, minx = max([tile['iso_bottomright'][0] for tile in tiles]), min([tile['iso_topleft'][0] for tile in tiles])
    maxy, miny = max([tile['iso_bottomright'][1] for tile in tiles]), min([tile['iso_topleft'][1] for tile in tiles])

    # Modify blitting position
    for tile in tiles:
        # Correct blitting height
        tile['iso_topleft'][1] -= abs(images[tile['new_tile_type']].get_height() - images['water_tile_NE'].get_height())
        tile['iso_bottomright'][1] -= abs(images[tile['new_tile_type']].get_height() - images['water_tile_NE'].get_height())
        # Correct blitting height
        tile['iso_topleft'][0] -= abs(images[tile['new_tile_type']].get_width() - images['water_tile_NE'].get_width())
        tile['iso_bottomright'][0] -= abs(images[tile['new_tile_type']].get_width() - images['water_tile_NE'].get_width())

    # Define different world surfaces at 4 zoom levels
    world_surfaces = {}
    for zoom_level in [0, 1, 2]:

        if zoom_level > 0:

            # Platforms
            for tile in tiles:
                dx = (screen.get_width()/2 - tile['iso_topleft'][0]) * -scale_factor
                dy = (screen.get_height()/2 - tile['iso_topleft'][1]) * -scale_factor

                tile['iso_topleft'][0] -= dx
                tile['iso_topleft'][1] -= dy
                tile['iso_bottomright'][0] -= dx
                tile['iso_bottomright'][1] -= dy

            scale = scale * (1 - scale_factor)
        
        else:
            scale = 1

        images = load_images(scale)

        maxx, minx = max([tile['iso_bottomright'][0] for tile in tiles]), min([tile['iso_topleft'][0] for tile in tiles])
        maxy, miny = max([tile['iso_bottomright'][1] for tile in tiles]), min([tile['iso_topleft'][1] for tile in tiles])
        rangex = int(maxx - minx)
        rangey = int(maxy - miny)

        world_surf = pg.Surface((rangex, rangey))

        # Blit all tiles
        for tile in tiles:
            if minx < 0:
                tile['iso_topleft'][0] += abs(minx)
                tile['iso_bottomright'][0] += abs(minx)
            else:
                tile['iso_topleft'][0] -= abs(minx)
                tile['iso_bottomright'][0] -= abs(minx)
            if miny < 0:
                tile['iso_topleft'][1] += abs(miny)
                tile['iso_bottomright'][1] += abs(miny)
            else:
                tile['iso_topleft'][1] -= abs(miny)
                tile['iso_bottomright'][1] -= abs(miny)
            world_surf.blit(images[tile['new_tile_type']], (tile['iso_topleft']))

        world_surfaces[zoom_level] = world_surf

    return world_surfaces

def generate_perlin_noise_2d(shape, res, tileable=(False, False)):
    def f(t):
        return 6*t**5 - 15*t**4 + 10*t**3

    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    grid = np.mgrid[0:res[0]:delta[0],0:res[1]:delta[1]].transpose(1, 2, 0) % 1
    # Gradients
    angles = 2*np.pi*np.random.rand(res[0]+1, res[1]+1)
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    if tileable[0]:
        gradients[-1,:] = gradients[0,:]
    if tileable[1]:
        gradients[:,-1] = gradients[:,0]
    gradients = gradients.repeat(d[0], 0).repeat(d[1], 1)
    g00 = gradients[    :-d[0],    :-d[1]]
    g10 = gradients[d[0]:     ,    :-d[1]]
    g01 = gradients[    :-d[0],d[1]:     ]
    g11 = gradients[d[0]:     ,d[1]:     ]
    # Ramps
    n00 = np.sum(np.dstack((grid[:,:,0]  , grid[:,:,1]  )) * g00, 2)
    n10 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1]  )) * g10, 2)
    n01 = np.sum(np.dstack((grid[:,:,0]  , grid[:,:,1]-1)) * g01, 2)
    n11 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1]-1)) * g11, 2)
    # Interpolation
    t = f(grid)
    n0 = n00*(1-t[:,:,0]) + t[:,:,0]*n10
    n1 = n01*(1-t[:,:,0]) + t[:,:,0]*n11
    return np.sqrt(2)*((1-t[:,:,1])*n0 + t[:,:,1]*n1)

def generate_radial_gradient(shape, res):

    sea_level_perlin = generate_perlin_noise_2d(shape, res)

    center_x, center_y = shape[0] // 2, shape[1] // 2
    circle_grad = []
    circle_obs = []

    for x in range(shape[0]):
        circle_grad.append([])
        for y in range(shape[1]):
            distx = abs(x - center_x)
            disty = abs(y - center_y)
            dist = math.sqrt(distx*distx + disty*disty)
            circle_grad[x].append(dist)
            circle_obs.append(dist)

    circle_grad_max = np.max(circle_obs)

    for x in range(shape[0]):
        for y in range(shape[1]):
            noise = sea_level_perlin[x][y] * 30
            circle_grad[x][y] = ( circle_grad_max - circle_grad[x][y] + noise )

    return circle_grad

def generate_temperature_gradient(shape, res):

    temp_perlin = generate_perlin_noise_2d(shape, res)

    temp_grad = []
    temp_obs = []

    for x in range(shape[0]):
        temp_grad.append([])
        for y in range(shape[1]):
            disty = abs(y - shape[1]//2)
            temp_grad[x].append(disty)
            temp_obs.append(disty)

    max_temp = max(temp_obs)

    for x in range(shape[0]):
        for y in range(shape[1]):
            noise = temp_perlin[x][y] * 30
            temp_grad[x][y] = max_temp - temp_grad[x][y] + noise - 25

    return temp_grad
    
