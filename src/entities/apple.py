import pygame
from random import randint

import src.config as config


def generateApple(w, h, color):
    x = randint(0, config.WIDTH - w)
    y = randint(config.FONT_SIZE, config.HEIGHT - h)
    return Apple(x, y, w, h, color)


class Apple:
    def __init__(self, x, y, w, h, color):
        self.rect = [x, y, w, h]
        self.color = color
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)