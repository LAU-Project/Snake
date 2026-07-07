import pygame
from random import randint

from src.config import WIDTH, HEIGHT

def generateApple(w, h, color):
    x = randint(0, WIDTH - w)
    y = randint(0, HEIGHT - h)
    apple = Apple(x, y, w, h, color)
    return apple

class Apple:

    def __init__(self, x, y, w, h, color):
        self.rect = [x, y, w, h]
        self.color = color
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)