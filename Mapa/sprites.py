import pygame
from .mapa import *

class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self._layer = BLOCK_LAYER
        original = pygame.image.load('Mapa/Imagens/4 Stone/8.png').convert_alpha()
        self.image = pygame.transform.scale(original, (game.TILESIZE, game.TILESIZE))
        self.rect = self.image.get_rect(topleft=(x * game.TILESIZE, y * game.TILESIZE))
        game.all_sprites.add(self)
        game.blocks.add(self)

class Ground(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self._layer = GROUND_LAYER
        original = pygame.image.load('Mapa/Imagens/1 Tiles/FieldsTile_01.png').convert_alpha()
        self.image = pygame.transform.scale(original, (game.TILESIZE, game.TILESIZE))
        self.rect = self.image.get_rect(topleft=(x * game.TILESIZE, y *game.TILESIZE))
        game.all_sprites.add(self)
        game.grounds.add(self)

class CheckPoint(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self._layer = CHECKPOINT_LAYER
        original = pygame.image.load('Mapa/Imagens/CheckPoints/checkpoint.png').convert_alpha()
        self.image = pygame.transform.scale(original, (game.TILESIZE, game.TILESIZE))
        self.rect = self.image.get_rect(topleft=(x * game.TILESIZE, y *game.TILESIZE))
        game.all_sprites.add(self)
        game.check_points.add(self)

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.x = x
        self.y= y
        self.game = game
        self._layer = PLAYER_LAYER
        self.sheet_img = game.player_spritesheet.get_image(8, 10, 32, 40)
        if self.sheet_img is None:
            self.sheet_img = pygame.Surface((16, 32))
            self.sheet_img.fill((255, 0, 0))
        self.image = pygame.transform.scale(self.sheet_img, (game.TILESIZE, game.TILESIZE))
        self.rect = self.image.get_rect(topleft=(x * game.TILESIZE, y * game.TILESIZE))
        game.all_sprites.add(self)