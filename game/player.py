
import pygame as pg
from utils import read_image, cart_to_iso
from settings import *


class Player(pg.sprite.Sprite):

    def __init__(self, pos):
        pg.sprite.Sprite.__init__(self)
        self.player_image = read_image('images/player.png')
        self.image = pg.Surface((TILE_SIZE/2, TILE_SIZE/2))
        self.image.fill((0, 150, 255))
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        
        pressed = pg.key.get_pressed()
        event = pg.event.wait()
        keydown = event.type == pg.KEYDOWN
        game_exit = event.type == pg.QUIT

        if game_exit:
            pg.quit()
            sys.exit()

        up = pressed[pg.K_UP]
        down = pressed[pg.K_DOWN]
        left = pressed[pg.K_LEFT]
        right = pressed[pg.K_RIGHT]

        if not keydown:
            if up:
                self.rect.y -= TILE_SIZE
            if down:
                self.rect.y += TILE_SIZE
            if left:
                self.rect.x -= TILE_SIZE
            if right:
                self.rect.x += TILE_SIZE

    def draw(self, screen):
        # Draw isometric position
        corners = [self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft]
        iso_corners = [cart_to_iso(pos[0], pos[1], OFFSET) for pos in corners]
        # pg.draw.polygon(screen, (0, 150, 255), iso_corners)

        minx = min([corner[0] for corner in iso_corners]) - 15
        miny = min([corner[1] for corner in iso_corners]) - 65

        screen.blit(self.player_image, (minx, miny))
        #Draw cartesion positon
        # screen.blit(self.image, self.rect.topleft)