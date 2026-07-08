import sys
import threading

import pygame
import pygame_menu
import requests

from pygame.locals import *

from src.config import FPS
from src.config import MENU, RUN, DEAD
from src.config import WIDTH, HEIGHT
from src.config import SNAKE_COLOR, BODY_COLOR, SNAKE_X, SNAKE_Y, SNAKE_SIZE, SNAKE_SPEED
from src.config import BLACK, WHITE
from src.config import NB_APPLES, APPLE_SIZE, APPLE_COLOR
from src.config import SCORE_POS
from src.config import FONT_SIZE
from src.config import FIREBASE_URL
from src.config import MUSIC

from src.entities.snake import Snake
from src.entities.apple import generateApple


class Game:

    def __init__(self):
        self.apples = [generateApple(APPLE_SIZE, APPLE_SIZE, APPLE_COLOR) for _ in range(NB_APPLES)]
        self.score_value = 0
        self.score = my_font.render('Score: 0', False, WHITE)
        self.state = RUN
        self.leaderboard = []
        self.score_submitted = False
        self.name = "Marvin"

    def reset(self):
        self.snake = Snake(SNAKE_COLOR, BODY_COLOR, SNAKE_X, SNAKE_Y, SNAKE_SIZE, SNAKE_SIZE, SNAKE_SPEED)
        self.apples = [generateApple(APPLE_SIZE, APPLE_SIZE, APPLE_COLOR) for _ in range(NB_APPLES)]
        self.score_value = 0
        self.score = my_font.render('Score: 0', False, WHITE)
        self.state = RUN
        self.score_submitted = False
        pygame.mixer.music.stop()

    def checkColisions(self):
        snake_rect = pygame.Rect(*self.snake.rect)

        for i in range(len(self.apples) - 1, -1, -1):
            apple = self.apples[i]
            if snake_rect.colliderect(apple.rect):
                self.apples.pop(i)
                self.snake.score += 1
                self.apples.append(generateApple(APPLE_SIZE, APPLE_SIZE, APPLE_COLOR))

    def checkSnakeOutBound(self):
        x, y = self.snake.rect[0], self.snake.rect[1]

        if (x < 0 or WIDTH < x) or (y < FONT_SIZE or HEIGHT < y):
            self.snake.dead()
            self.state = DEAD
            if not self.score_submitted:
                self.score_submitted = True
                threading.Thread(target=self.fetchLeaderboard, daemon=True).start()

    def fetchLeaderboard(self):
        submit_score(self.name, self.snake.score)
        self.leaderboard = get_leaderboard(10)

    def update(self):
        if self.state == MENU:
            return
        elif self.state == RUN:
            if self.snake.score != self.score_value:
                self.score_value = self.snake.score
                self.score = my_font.render('Score: ' + str(self.score_value), False, WHITE)
            self.checkColisions()
            self.checkSnakeOutBound()
            if self.snake.alive:
                self.snake.move()
                self.snake.update_body()
        elif self.state == DEAD:
            return

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
            deadScreen(self.leaderboard)
            return

    def handleKeys(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

        if self.state == MENU:
            return
        elif self.state == DEAD:
            if keys[pygame.K_r]:
                self.reset()
            if keys[pygame.K_BACKSPACE]:
                self.reset()
                menu.mainloop(screen)
        elif self.state == RUN:
            if keys[pygame.K_LEFT]:
                self.snake.move_left()
            elif keys[pygame.K_RIGHT]:
                self.snake.move_right()
            elif keys[pygame.K_UP]:
                self.snake.move_up()
            elif keys[pygame.K_DOWN]:
                self.snake.move_down()
            return

    def gameLoop(self):
        pygame.mixer.music.play()
        self.snake = Snake(SNAKE_COLOR, BODY_COLOR, SNAKE_X, SNAKE_Y, SNAKE_SIZE, SNAKE_SIZE, SNAKE_SPEED)
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

    def setVolume(self, value):
        self.volume = value
        pygame.mixer.music.set_volume(value / 100)

    def setName(self, name):
        self.name = name


def submit_score(name, score):
    """Envoie un score au leaderboard distant"""
    data = {"name": name, "score": score}
    try:
        requests.post(FIREBASE_URL, json=data, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Erreur envoi score: {e}")


def get_leaderboard(top_n=10):
    """Récupère le top N des scores, triés"""
    try:
        response = requests.get(FIREBASE_URL, timeout=5)
        raw = response.json()
        if not raw:
            return []
        scores = list(raw.values())
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:top_n]
    except requests.exceptions.RequestException as e:
        print(f"Erreur récupération leaderboard: {e}")
        return []


def deadScreen(leaderboard):
    txt = my_font.render("YOU ARE DEAD!", False, WHITE)
    screen.blit(txt, (WIDTH / 2 - (3 * FONT_SIZE), HEIGHT / 2 - FONT_SIZE))
    txt = my_font.render("PRESS R TO RESTART", False, WHITE)
    screen.blit(txt, (WIDTH / 2 - (4 * FONT_SIZE), HEIGHT - (FONT_SIZE * 4)))

    y = 50
    title = my_font.render("LEADERBOARD", True, (255, 255, 255))
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, y))

    for i, entry in enumerate(leaderboard):
        y += 40
        line = f"{i+1}. {entry['name']} - {entry['score']}"
        text = my_font.render(line, True, (255, 255, 255))
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, y))


pygame.init()
pygame.display.set_caption('Snake')

fpsClock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', FONT_SIZE)

game = Game()

menu_theme = pygame_menu.themes.THEME_DARK.copy()
menu_theme.title_font_size = 80
menu_theme.widget_font_size = 48
menu_theme.widget_height = 70
menu_theme.widget_width = 400

menu = pygame_menu.Menu('Snake', WIDTH, HEIGHT, theme=menu_theme)

menu.add.text_input('Name :', default='', onchange=game.setName)
menu.add.button('Play', game.gameLoop)
menu.add.selector(
    'Music :',
    [(f'{v}', v) for v in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]],
    onchange=lambda selected, value: game.setVolume(value)
)
menu.add.button('Quit', pygame_menu.events.EXIT)

pygame.mixer.init()
pygame.mixer.music.load(MUSIC)
pygame.mixer.music.set_volume(0.1)

menu.mainloop(screen)