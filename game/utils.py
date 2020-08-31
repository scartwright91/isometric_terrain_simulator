
import pygame as pg
import os
import re
from game.settings import *


def load_images(scale):

    img_path = 'images/'

    imgs = {}

    for img in os.listdir(img_path):

        tmp_img = read_image(img_path + img)

        img_name = img.split('.')[0]
        imgs[img_name] = read_image(img_path + img,
                                    w=tmp_img.get_width()*scale,
                                    h=tmp_img.get_height()*scale)
                                    
    return imgs


def read_image(path, w=None, h=None, create_surface=False):

    img = pg.image.load(path)

    if (w == None) and (h == None):
        pass
    elif h == None:
        scale = w / img.get_width()
        h = scale * img.get_height()
        img = pg.transform.scale(img, (int(w), int(h)))
    elif w == None:
        scale = h / img.get_height()
        w = scale * img.get_width()
        img = pg.transform.scale(img, (int(w), int(h)))
    else:
        img = pg.transform.scale(img, (int(w), int(h)))
    
    if create_surface:
        image = pg.Surface(img.get_rect().size, pg.SRCALPHA, 32)
        image.blit(img, (0, 0))
        return image
    else:
        return img


def cart_to_iso(x, y, offset):
    isox = x - y
    isoy = (x + y)/2
    return [isox + offset[0], isoy + offset[1]]


def calculate_iso_map(tiles):
    for tile in tiles:
        rect = tile['rect']
        corners = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]
        iso_corners = [cart_to_iso(pos[0], pos[1], OFFSET) for pos in corners]
        iso_topleft = [iso_corners[0][0], iso_corners[1][1]]
        tile['corners'] = corners
        tile['iso_corners'] = iso_corners
        tile['iso_topleft'] = iso_topleft
