import pygame

from src.config import WIDTH, HEIGHT


class Snake:
    def __init__(self, color, body_color, x, y, w, h, speed=1):
        self.alive = True
        self.color = color
        self.body_color = body_color
        self.rect = [x, y, w, h]
        self.speed = speed
        self.score = 0
        self.speedx = speed
        self.speedy = 0
        self.body = []
        self.body_spacing = w
        self.travelled = 0

    def move_left(self):
        if (self.rect[0] - self.speed > 0) and (self.speedx != self.speed):
            self.speedx = -self.speed
            self.speedy = 0

    def move_right(self):
        if (self.rect[0] + self.speed < WIDTH - self.rect[2]) and (self.speedx != -self.speed):
            self.speedx = self.speed
            self.speedy = 0

    def move_up(self):
        if (self.rect[1] - self.speed > 0) and (self.speedy != self.speed):
            self.speedy = -self.speed
            self.speedx = 0

    def move_down(self):
        if (self.rect[1] + self.speed < HEIGHT - self.rect[3]) and (self.speedy != -self.speed):
            self.speedy = self.speed
            self.speedx = 0

    def move(self):
        self.rect[0] += self.speedx
        self.rect[1] += self.speedy
        self.travelled += abs(self.speedx) + abs(self.speedy)

    def update_body(self):
        if self.travelled >= self.body_spacing:
            self.body.append(self.rect.copy())
            self.travelled = 0
            if len(self.body) > self.score:
                del self.body[0]

    def draw(self, screen):
        for cell in self.body:
            pygame.draw.rect(screen, self.body_color, cell)
        pygame.draw.rect(screen, self.color, self.rect)

    def dead(self):
        self.alive = False