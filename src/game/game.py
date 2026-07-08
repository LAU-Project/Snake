import sys
 
import pygame
from pygame.locals import *
 
from src.config import FPS 
from src.config import MENU, RUN, DEAD
from src.config import WIDTH, HEIGHT
from src.config import SNAKE_COLOR, SNAKE_X, SNAKE_Y, SNAKE_SIZE, SNAKE_SPEED
from src.config import BLACK, WHITE
from src.config import NB_APPLES , APPLE_SIZE, APPLE_COLOR
from src.config import SCORE_POS
from src.config import FONT_SIZE

from src.entities.snake import Snake
from src.entities.apple import generateApple

pygame.init()
pygame.display.set_caption('Snake')
 
fpsClock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', FONT_SIZE)



def deadScreen():
    txt = my_font.render("YOU ARE DEAD!", False, WHITE)
    screen.blit(txt, (WIDTH / 2 - (3 * FONT_SIZE), HEIGHT / 2 - FONT_SIZE))

class Game:

    def __init__(self):
        self.apples = [generateApple(APPLE_SIZE, APPLE_SIZE, APPLE_COLOR) for _ in range(NB_APPLES)]
        self.score = my_font.render('Score: 0', False, WHITE)
        self.state = RUN

    def checkColisions(self):
        snake_rect = pygame.Rect(*self.snake.rect)

        for i in range(len(self.apples) - 1, -1, -1):
            apple = self.apples[i]
            apple_rect = pygame.Rect(*apple.rect)
            if snake_rect.colliderect(apple_rect):
                self.apples.pop(i)
                self.snake.score += 1

    def checkSnakeOutBound(self):
        coords = self.snake.rect[0], self.snake.rect[1]

        if (coords[0] < 0 or WIDTH < coords[0]):
            self.snake.dead()
            self.state = DEAD
        if (coords[1] < FONT_SIZE or HEIGHT < coords[1]):
            self.snake.dead()
            self.state = DEAD


    def update(self):
        self.score = my_font.render('Score: ' + str(self.snake.score), False, WHITE)
        self.checkColisions()
        self.checkSnakeOutBound()
        if (self.snake.alive is True):
            self.snake.move()


    def draw(self):
        screen.fill(BLACK)

        if self.state == MENU:
            return
        elif self.state == RUN:
            pygame.draw.rect(screen, WHITE, (0, FONT_SIZE, WIDTH, 1))
            self.snake.draw(screen)
            for apple in self.apples:
                apple.draw(screen)
            screen.blit(self.score, SCORE_POS)
            return
        elif self.state == DEAD:
            deadScreen()
            return


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