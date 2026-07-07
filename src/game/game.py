import sys
 
import pygame
from pygame.locals import *
 
from src.config import WIDTH, HEIGHT, FPS, SNAKE_COLOR, SNAKE_X, SNAKE_Y, SNAKE_SIZE, SNAKE_SPEED, BLACK
from src.entities.snake import Snake

pygame.init()
 
fpsClock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

class Game:

    def __init__(self):
        pass

    def update(self):
        """
        INPUT: snake : Snake
        OUTPUT: none
        Update the game
        """
        pass

    def draw(self):
        self.snake.draw(screen)

    def handleKeys(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

        if keys[pygame.K_LEFT]:
            self.snake.move_left()
        elif keys[pygame.K_RIGHT]:
            self.snake.move_right()
        elif keys[pygame.K_UP]:
            self.snake.move_up()
        elif keys[pygame.K_DOWN]:
            self.snake.move_down()

    def gameLoop(self):
        self.snake = Snake(SNAKE_COLOR, SNAKE_X, SNAKE_Y, SNAKE_SIZE, SNAKE_SIZE, SNAKE_SPEED)

        while True:
            screen.fill(BLACK)
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            
            self.handleKeys()
            self.update()
            self.draw()
            
            pygame.display.flip()
            fpsClock.tick(FPS)

game = Game()
game.gameLoop()