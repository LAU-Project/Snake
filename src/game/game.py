import sys
import threading

import pygame
import pygame_menu
import requests

from pygame.locals import *

import src.config as config

from src.config import FPS
from src.config import MENU, RUN, DEAD
from src.config import SNAKE_COLOR, BODY_COLOR, SNAKE_X, SNAKE_Y, SNAKE_SIZE, SNAKE_SPEED
from src.config import BLACK, WHITE
from src.config import NB_APPLES, APPLE_SIZE, APPLE_COLOR
from src.config import SCORE_POS
from src.config import FIREBASE_URL
from src.config import MUSIC
from src.config import WIDTH, HEIGHT
from src.config import FONT_SIZE

from src.entities.snake import Snake
from src.entities.apple import generateApple


RESOLUTIONS = [
    ('800x600', (800, 600)),
    ('1280x720', (1280, 720)),
    ('1600x900', (1600, 900)),
    ('1920x1080', (1920, 1080)),
]
VOLUMES = [(f'{v}', v) for v in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]]

_font_cache = {}


def get_cached_font(name, size, bold=False):
    key = (name, size, bold)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont(name, size, bold=bold)
    return _font_cache[key]


class Game:

    def __init__(self):
        self.apples = []
        self.score_value = 0
        self.state = RUN
        self.leaderboard = []
        self.score_submitted = False
        self.name = "Marvin"
        self.volume = 10
        self.pending_resize = False
        self.score = None
        # Tant que True, les callbacks onchange déclenchés par la construction
        # des widgets (comportement pygame_menu 4.5.2) sont ignorés.
        self.suppress_events = False

    def spawnApples(self):
        self.apples = [generateApple(APPLE_SIZE, APPLE_SIZE, APPLE_COLOR) for _ in range(NB_APPLES)]

    def getSnakeStartPos(self):
        return (config.WIDTH // 2, config.HEIGHT // 2)

    def reset(self):
        x, y = self.getSnakeStartPos()
        self.snake = Snake(SNAKE_COLOR, BODY_COLOR, x, y, SNAKE_SIZE, SNAKE_SIZE, SNAKE_SPEED)
        self.spawnApples()
        self.score = my_font.render('Score: 0', False, WHITE)
        self.score_value = 0
        self.state = RUN
        self.score_submitted = False
        pygame.mixer.music.stop()

    def checkColisions(self):
        snake_rect = pygame.Rect(*self.snake.rect)
        for i in range(len(self.apples) - 1, -1, -1):
            apple = self.apples[i]
            apple_rect = pygame.Rect(*apple.rect)
            if snake_rect.colliderect(apple_rect):
                self.apples.pop(i)
                self.snake.score += 1
                self.apples.append(generateApple(APPLE_SIZE, APPLE_SIZE, APPLE_COLOR))

    def checkSnakeOutBound(self):
        x, y, w, h = self.snake.rect
        if (x < 0 or x + w > config.WIDTH) or (y < FONT_SIZE or y + h > config.HEIGHT):
            self.snake.dead()
            self.state = DEAD
            if not self.score_submitted:
                self.score_submitted = True
                threading.Thread(target=self.fetchLeaderboard, daemon=True).start()

    def fetchLeaderboard(self):
        submit_score(self.name, self.snake.score)
        self.leaderboard = get_leaderboard(10)

    def update(self):
        if self.state != RUN:
            return
        if self.snake.score != self.score_value:
            self.score_value = self.snake.score
            self.score = my_font.render('Score: ' + str(self.snake.score), False, WHITE)
        self.checkColisions()
        self.checkSnakeOutBound()
        if self.snake.alive is True:
            self.snake.move()
            self.snake.update_body()

    def draw(self):
        screen.fill(BLACK)
        if self.state == RUN:
            pygame.draw.rect(screen, WHITE, (0, FONT_SIZE, config.WIDTH, 1))
            self.snake.draw(screen)
            for apple in self.apples:
                apple.draw(screen)
            screen.blit(self.score, SCORE_POS)
        elif self.state == DEAD:
            deadScreen(self.leaderboard, self.snake.score, self.name)

    def handleMovementKeys(self):
        keys = pygame.key.get_pressed()
        if self.state != RUN:
            return
        if keys[pygame.K_LEFT]:
            self.snake.move_left()
        elif keys[pygame.K_RIGHT]:
            self.snake.move_right()
        elif keys[pygame.K_UP]:
            self.snake.move_up()
        elif keys[pygame.K_DOWN]:
            self.snake.move_down()

    def gameLoop(self):
        pygame.mixer.music.play()
        x, y = self.getSnakeStartPos()
        self.snake = Snake(SNAKE_COLOR, BODY_COLOR, x, y, SNAKE_SIZE, SNAKE_SIZE, SNAKE_SPEED)

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if self.state == DEAD:
                        if event.key == K_r:
                            self.reset()
                        elif event.key == K_BACKSPACE:
                            self.reset()
                            return  # rend la main au menu.mainloop() déjà actif

            self.handleMovementKeys()
            self.update()
            self.draw()

            pygame.display.flip()
            fpsClock.tick(FPS)

    def setVolume(self, value):
        if self.suppress_events:
            return
        self.volume = value
        pygame.mixer.music.set_volume(value / 100)

    def setName(self, name):
        if self.suppress_events:
            return
        self.name = name

    def setScreenSize(self, value):
        if self.suppress_events:
            return
        global screen
        if tuple(value) == (config.WIDTH, config.HEIGHT):
            return
        config.WIDTH, config.HEIGHT = value
        screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        refresh_font()
        self.reset()
        self.pending_resize = True
        menu.disable()  # sort proprement de menu.mainloop(), pas d'appel imbriqué


def get_font_size():
    return max(24, config.HEIGHT // 20)


def refresh_font():
    global my_font
    my_font = pygame.font.SysFont('Comic Sans MS', get_font_size())


def submit_score(name, score):
    data = {"name": name, "score": score}
    try:
        requests.post(FIREBASE_URL, json=data, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Erreur envoi score: {e}")


def get_leaderboard(top_n=10):
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


def deadScreen(leaderboard, score=0, player_name=""):
    margin = max(10, config.HEIGHT // 40)

    title_size = max(28, config.HEIGHT // 14)
    text_size = max(16, config.HEIGHT // 26)
    row_size = max(14, config.HEIGHT // 32)

    title_font = get_cached_font('Comic Sans MS', title_size, bold=True)
    text_font = get_cached_font('Comic Sans MS', text_size)
    row_font = get_cached_font('Comic Sans MS', row_size)

    footer_line_h = text_size + 6
    footer_h = footer_line_h * 2 + margin
    footer_top = config.HEIGHT - footer_h

    y = margin

    title_surf = title_font.render("YOU ARE DEAD!", True, (220, 60, 60))
    screen.blit(title_surf, (config.WIDTH // 2 - title_surf.get_width() // 2, y))
    y += title_surf.get_height() + margin // 2

    score_surf = text_font.render(f"{player_name} - Score final : {score}", True, WHITE)
    screen.blit(score_surf, (config.WIDTH // 2 - score_surf.get_width() // 2, y))
    y += score_surf.get_height() + margin

    lb_title_surf = text_font.render("LEADERBOARD", True, WHITE)
    screen.blit(lb_title_surf, (config.WIDTH // 2 - lb_title_surf.get_width() // 2, y))
    y += lb_title_surf.get_height() + margin // 2

    row_h = row_font.get_height() + 4
    available_h = max(0, footer_top - y)
    max_rows = available_h // row_h
    rows_to_show = leaderboard[:max_rows]

    for i, entry in enumerate(rows_to_show):
        name = entry.get('name', '?')
        entry_score = entry.get('score', '?')
        line = f"{i + 1}. {name} - {entry_score}"
        row_surf = row_font.render(line, True, WHITE)
        screen.blit(row_surf, (config.WIDTH // 2 - row_surf.get_width() // 2, y))
        y += row_h

    restart_surf = text_font.render("PRESS R TO RESTART", True, WHITE)
    screen.blit(restart_surf, (config.WIDTH // 2 - restart_surf.get_width() // 2, footer_top))

    menu_surf = text_font.render("PRESS BACKSPACE FOR MENU", True, WHITE)
    screen.blit(menu_surf, (config.WIDTH // 2 - menu_surf.get_width() // 2, footer_top + footer_line_h))


pygame.init()
pygame.display.set_caption('Snake')

fpsClock = pygame.time.Clock()
screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))

pygame.font.init()
refresh_font()
my_font = pygame.font.SysFont('Comic Sans MS', get_font_size())


def build_menu(default_name='', default_volume=10, default_resolution=None):
    if default_resolution is None:
        default_resolution = (config.WIDTH, config.HEIGHT)

    game.suppress_events = True  # ignore les onchange déclenchés pendant la construction

    menu_theme = pygame_menu.themes.THEME_DARK.copy()
    menu_theme.title_font_size = max(40, config.WIDTH // 24)
    menu_theme.widget_font_size = max(24, config.WIDTH // 40)
    menu_theme.widget_height = max(50, config.HEIGHT // 15)
    menu_theme.widget_width = max(250, config.WIDTH // 4)

    new_menu = pygame_menu.Menu('Snake', config.WIDTH, config.HEIGHT, theme=menu_theme)

    new_menu.add.text_input('Name :', default=default_name, onchange=game.setName)
    new_menu.add.button('Play', game.gameLoop)

    volume_index = next((i for i, (_, v) in enumerate(VOLUMES) if v == default_volume), 1)
    new_menu.add.selector(
        'Music :', VOLUMES, default=volume_index,
        onchange=lambda selected, value: game.setVolume(value)
    )

    res_index = next((i for i, (_, v) in enumerate(RESOLUTIONS) if v == tuple(default_resolution)), 0)
    new_menu.add.selector(
        'Screen Size :', RESOLUTIONS, default=res_index,
        onchange=lambda selected, value: game.setScreenSize(value)
    )
    new_menu.add.button('Quit', pygame_menu.events.EXIT)

    game.suppress_events = False
    return new_menu


game = Game()
game.reset()

pygame.mixer.init()
pygame.mixer.music.load(MUSIC)
pygame.mixer.music.set_volume(0.1)

menu = build_menu(default_name=game.name, default_volume=game.volume)

while True:
    menu.mainloop(screen)
    if game.pending_resize:
        game.pending_resize = False
        menu = build_menu(
            default_name=game.name,
            default_volume=game.volume,
            default_resolution=(config.WIDTH, config.HEIGHT)
        )
    else:
        break