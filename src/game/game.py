import sys
 
import pygame
from pygame.locals import *
 
from src.config import WIDTH, HEIGHT, FPS, SNAKE_COLOR, SNAKE_X, SNAKE_Y, SNAKE_SIZE, SNAKE_SPEED, BLACK, NB_APPLES , APPLE_SIZE, APPLE_COLOR, WHITE, SCORE_POS

from src.entities.snake import Snake
from src.entities.apple import generateApple

pygame.init()
 
fpsClock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 50)

class Game:

    def __init__(self):
        self.apples = [generateApple(APPLE_SIZE, APPLE_SIZE, APPLE_COLOR) for _ in range(NB_APPLES)]
        self.score = my_font.render('Score: 0', False, WHITE)

    def checkColisions(self):
        snake_rect = pygame.Rect(*self.snake.rect)

        for i in range(len(self.apples) - 1, -1, -1):
            apple = self.apples[i]
            apple_rect = pygame.Rect(*apple.rect)
            if snake_rect.colliderect(apple_rect):
                self.apples.pop(i)
                self.snake.score += 1


    def update(self):
        """
        INPUT: snake : Snake
        OUTPUT: none
        Update the game
        """
        self.score = my_font.render('Score: ' + str(self.snake.score), False, WHITE)
        self.checkColisions()

    def draw(self):
        screen.fill(BLACK)
        self.snake.draw(screen)
        for apple in self.apples:
            apple.draw(screen)
        screen.blit(self.score, SCORE_POS)

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