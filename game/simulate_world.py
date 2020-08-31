
import pygame as pg
import numpy as np
import math
import random
from game.settings import *
from game.utils import cart_to_iso


def create_iso_world(shape, res, sealevelp=30, gradient='radial'):

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

            iso_topleft = [minx, miny]

            sea_level_val = sea_level_world[x][y]
            temp_val = temp_world[x][y]

            if sea_level_val < 40:
                if random.randint(1, 100) == 1:
                    tile_type = 'water_rock_tile'
                else:
                    tile_type = 'deep_water_tile'
            elif sea_level_val < 50:
                if temp_val < 0:
                    tile_type = 'deep_water_tile'
                else:
                    tile_type = 'water_tile'
            elif sea_level_val < 60:
                if temp_val < 0:
                    tile_type = 'snow_tile'
                else:
                    tile_type = 'sand_tile'
            else:
                if temp_val < 0:
                    tile_type = 'snow_tile'
                else:
                    if random.randint(1, 15) == 1:
                        tile_type = 'tree_tile'
                    else:
                        tile_type = 'grass_tile'

            tiles.append({
                        'pos': [x, y],
                        'orig_tile_type': tile_type,
                        'new_tile_type': tile_type,
                        'rect': rect,
                        'corners': corners,
                        'iso_corners': iso_corners,
                        'sea_level_val': sea_level_val,
                        'iso_topleft': iso_topleft})

    # Modify blitting position
    for tile in tiles:
        if tile['new_tile_type'] == 'tree_tile':
            tile['iso_topleft'][1] -= 50
        if tile['new_tile_type'] == 'water_rock_tile':
            tile['iso_topleft'][1] -= 14

    return tiles

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
    