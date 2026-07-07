import pygame

from src.config import WIDTH, HEIGHT

class Snake:

    def __init__(self, color, x, y, w, h, speed=1):
        self.alive = True
        self.color = color
        self.rect = [x, y, w, h]
        self.speed = speed

    def move_left(self):
        if (self.rect[0] - self.speed > 0):
            self.rect[0] -= self.speed

    def move_right(self):
        if (self.rect[0] + self.speed < WIDTH - self.rect[2]):
            self.rect[0] += self.speed

    def move_up(self):
        if (self.rect[1] - self.speed > 0):
            self.rect[1] -= self.speed

    def move_down(self):
        if (self.rect[1] + self.speed < HEIGHT - self.rect[3]):
            self.rect[1] += self.speed

    def health(self):
        print("The snake is " + ("alive" if self.isAlive() == True else "dead") + ".")

    def isAlive(self):
        return self.alive
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)