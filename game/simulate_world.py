
import pygame as pg
import numpy as np
import math
import random
from game.settings import *
from game.utils import cart_to_iso, load_images


def create_iso_world(screen, shape, res):

    # Import images
    scale = 1
    scale_factor = 0.5
    images = load_images(scale)

    # Simulate sea level
    sea_level_world = generate_tile_values(shape, res)

    # Calculate max sea level
    max_sea_level = np.amax(sea_level_world)

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

            if sea_level_val < 0:
                tile_type = 'water_tile_NE'
            else:
                tile_type = 'cliff_block_rock_NE'

            tiles.append({
                        'pos': [x * TILE_SIZE, y * TILE_SIZE],
                        'sea_level_val': sea_level_val,
                        'tile_type': tile_type,
                        'rect': rect,
                        'corners': corners,
                        'iso_corners': iso_corners,
                        'sea_level_val': sea_level_val,
                        'iso_topleft': iso_topleft,
                        'iso_bottomright': iso_bottomright})

    maxx, minx = max([tile['iso_bottomright'][0] for tile in tiles]), min([tile['iso_topleft'][0] for tile in tiles])
    maxy, miny = max([tile['iso_bottomright'][1] for tile in tiles]), min([tile['iso_topleft'][1] for tile in tiles])

    # Change tile based on which direction they face
    shore_tiles = tile_facing(tiles)

    # Create a beach
    create_beach(tiles, shore_tiles)
    tile_facing(tiles)

    # Create rivers
    create_rivers(tiles, max_sea_level)

    # Modify blitting position
    for tile in tiles:
        # Correct blitting height
        tile['iso_topleft'][1] -= abs(images[tile['tile_type']].get_height() - images['water_tile_NE'].get_height())
        tile['iso_bottomright'][1] -= abs(images[tile['tile_type']].get_height() - images['water_tile_NE'].get_height())
        # Correct blitting height
        tile['iso_topleft'][0] -= abs(images[tile['tile_type']].get_width() - images['water_tile_NE'].get_width())
        tile['iso_bottomright'][0] -= abs(images[tile['tile_type']].get_width() - images['water_tile_NE'].get_width())

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
            world_surf.blit(images[tile['tile_type']], (tile['iso_topleft']))

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

def generate_tile_values(shape, res):

    sea_level_perlin = generate_perlin_noise_2d(shape, res)

    center_x, center_y = shape[0]//2, shape[1]//2
    max_distance = math.sqrt(center_x**2 + center_y**2)

    # Determining sea level
    for x in range(shape[0]):
        for y in range(shape[1]):

            # Calculate distance from midpoint
            distx = abs(x - center_x)
            disty = abs(y - center_y)
            # calculate percentage distance from corners
            dist = (max_distance - math.sqrt(distx*distx + disty*disty)) / max_distance

            sea_level_perlin[x][y] = dist + sea_level_perlin[x][y]/5 - 0.45  

    return sea_level_perlin
    
def tile_facing(tiles):

    """ Record which isometric direction the tile is facing"""

    shore_tiles = []

    for tile in tiles:

        if tile['tile_type'] == 'cliff_block_rock_NE':
            # Find adjacent tiles
            tile_pos = tile['pos']

            adj_tile_pos_se = [tile_pos[0] + TILE_SIZE, tile_pos[1]]

            # Find SE tiles
            for adj_tile in tiles:
                if adj_tile['pos'] == adj_tile_pos_se:
                    rand = random.randint(1, 10)
                    if adj_tile['tile_type'] == ['water_tile_NE', 'sand_tile_NE', 'ground_grass_NE']:
                        
                        if rand < 4:
                            tile['tile_type'] = 'cliff_blockSlope_rock_SE'
                        elif rand < 5:
                            tile['tile_type'] = 'cliff_blockCave_rock_SE'

                        shore_tiles.append(tile)

    for tile in tiles:

        if tile['tile_type'] == 'cliff_block_rock_NE':
            # Find adjacent tiles
            tile_pos = tile['pos']

            adj_tile_pos_sw = [tile_pos[0], tile_pos[1] + TILE_SIZE]

            # Find SE tiles
            for adj_tile in tiles:
                if adj_tile['pos'] == adj_tile_pos_sw:
                    rand = random.randint(1, 10)
                    if adj_tile['tile_type'] in ['water_tile_NE', 'sand_tile_NE', 'ground_grass_NE']:
                        
                        if rand < 4:
                            tile['tile_type'] = 'cliff_blockSlope_rock_SW'
                        elif rand < 5:
                            tile['tile_type'] = 'cliff_blockCave_rock_SW'

                        shore_tiles.append(tile)

    return shore_tiles

def create_beach(tiles, shore_tiles, beaches=4, beach_area=800):

    for ind in range(beaches):

        sand_tile = random.choice(shore_tiles)
        sand_pos = sand_tile['pos']
        
        # Look for adj sand tiles
        for adj_tile in tiles:
            if adj_tile['tile_type'] in ['cliff_blockSlope_rock_SW', 'cliff_blockCave_rock_SW', 'cliff_blockSlope_rock_SE', 'cliff_blockCave_rock_SE', 'cliff_block_rock_NE']:
                if (abs(adj_tile['pos'][0] - sand_pos[0]) < beach_area) and (abs(adj_tile['pos'][1] - sand_pos[1]) < beach_area) and \
                    (adj_tile['sea_level_val'] < 0.2):
                    adj_tile['tile_type'] = 'sand_tile_NE'

def create_rivers(tiles, max_sea_level):

    river_pathing = True
    river_tiles = []

    # Choose highest point
    for tile in tiles:
        if tile['sea_level_val'] == max_sea_level:
            river_pos = tile['pos']
            #tile['tile_type'] = 'ground_riverStraight_NE'
            tile['tile_type'] = 'ground_riverOpen_SW'
            river_tiles.append(tile)
            break

    while river_pathing:

        adj_river_tiles = []

        for tile in tiles:
            if tile['pos'] in [
                [river_pos[0] - TILE_SIZE, river_pos[1]],
                [river_pos[0] + TILE_SIZE, river_pos[1]],
                [river_pos[0], river_pos[1] - TILE_SIZE],
                [river_pos[0], river_pos[1] + TILE_SIZE]]:
                if tile['tile_type'] not in ['ground_riverStraight_NE', 'ground_riverStraight_NW', 'ground_riverOpen_SW']:
                    adj_river_tiles.append(tile)

        # Calculate lowest sea level
        if len(adj_river_tiles) == 0:
            river_pathing = False
        else:
            min_adj_river_tile = min([adj_river_tile['sea_level_val'] for adj_river_tile in adj_river_tiles])

            for adj_river_tile in adj_river_tiles:
                if adj_river_tile['sea_level_val'] == min_adj_river_tile:

                    if adj_river_tile['tile_type'] == 'water_tile_NE':
                        river_pathing = False
                        break

                    if not adj_river_tile['tile_type'] == "sand_tile_NE":
                        # Choose river tiles based on consecutive positions
                        adj_river_tile['iso_topleft'][1] -= 79
                        adj_river_tile['iso_bottomright'][1] -= 79

                    #adj_river_tile['tile_type'] = 'ground_riverStraight_NE'
                    adj_river_tile['tile_type'] = 'ground_riverOpen_SW'
                    river_pos = adj_river_tile['pos']
                    river_tiles.append(adj_river_tile)


    # river_pos = river_tiles[0]['pos']

    # for river_tile in river_tiles:

    #     if river_tile['pos'][0] != river_pos[0]:
    #         river_tile['tile_type'] = 'ground_riverStraight_NW'
    #         river_pos = river_tile['pos']
