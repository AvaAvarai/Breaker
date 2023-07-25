import pygame
import pickle
import random

import sys, os

FPS_TARGET = 60
WIN_WIDTH = 480
WIN_HEIGHT = 640
UI_HEIGHT = 45

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def default_player_pos() -> pygame.rect.Rect:
    return pygame.rect.Rect(WIN_WIDTH * 0.5 - 30, WIN_HEIGHT - 55, 60, 15)

def default_ball_pos() -> pygame.rect.Rect:
    return pygame.rect.Rect(WIN_WIDTH * 0.5 - 4, WIN_HEIGHT * 0.5, 8, 8)

def color_dist(color1: tuple[int, int, int], color2: tuple[int, int, int]) -> int:
    distance: int = 0
    for index, c1 in enumerate(color1):
        c2: int = color2[index]
        distance += (c2 - c1) ** 2
    return distance ** 0.5

def gen_colors(n: int) -> list[tuple[int, int, int]]:
    variance: int = 150
    colors: list[tuple[int, int, int]] = [(25, 25, 25)]
    while len(colors) != (n+1):
        bad: bool = False
        new_color: tuple[int, int, int] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        for color in colors:
            if color_dist(color, new_color) < variance:
                bad = True
                break
        if not bad:
            colors.append(new_color)
    return colors[1::]

def create_bricks(level_number: int) -> list[list]:
    colors: list[tuple[int, int, int]] = gen_colors(6)
    level: list[list] = []
    x: int = 7
    y: int = UI_HEIGHT + 75
    for i in range(6): # y
        brick_color = colors[i]
        for _ in range(13): # x
            density: int = 1
            if i > 0:
                if random.randrange(0, 10 - level_number) == 0:
                    density = 2 
            else:
                density = 2
            level.append([x, y, brick_color, density])
            x += 36
        y += 17
        x = 7
    return level

def play_level_music(level_number: int) -> None:
    pygame.mixer.music.load(resource_path(r'assets\audio\level' + str(((level_number-1) % 5) + 1) + '.ogg'))
    pygame.mixer.music.play(-1)

class game:
    def __init__(self, screen) -> None:
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True
        self.screen = screen
        play_level_music(1)
        
        self.background_image: pygame.surface.Surface = pygame.image.load(resource_path(r'assets\image\background.jpg'))
        self.frame_image: pygame.surface.Surface = pygame.image.load(resource_path(r'assets\image\frame.png'))
        self.ball_image: pygame.surface.Surface = pygame.image.load(resource_path(r'assets\image\ball.png'))
        self.paddle_image: pygame.surface.Surface = pygame.image.load(resource_path(r'assets\image\paddle.png'))
        self.paddle_icon_image: pygame.surface.Surface = pygame.image.load(resource_path(r'assets\image\paddle_icon.png'))
        self.powerup1_image: pygame.surface.Surface = pygame.image.load(resource_path(r'assets\image\powerup1.png')) # B
        self.powerup2_image: pygame.surface.Surface = pygame.image.load(resource_path(r'assets\image\powerup2.png')) # L
        
        self.fg_font: pygame.font.Font = pygame.font.SysFont(pygame.font.match_font("cascadiamonoregular"), 32)
        self.fg_font_color1: tuple[int, int, int] = (255, 0, 0)
        self.fg_font_color2: tuple[int, int, int] = (255, 255, 255)

        self.ball_dir_x: int = 1
        self.ball_dir_y: int = 1
        self.ball_ang = 0
        
        self.dt = 0
        self.player_step: int = 300
        self.ball_step: int = 350

        self.level: int = 1
        self.score: int = 0
        self.bonus: int = 1
        self.lives: int = 3

        try: # existing file
            file = open('highscore', 'rb')
            self.highscore: int = pickle.load(file)['highscore']
            file.close()
        except: # new file
            self.highscore: int = 5000
            file = open('highscore', 'wb')
            save: dict = {'highscore': self.highscore}
            pickle.dump(save, file)
            file.close()
        
        self.player_pos: pygame.rect.Rect = default_player_pos()
        self.ball_pos: pygame.rect.Rect = default_ball_pos()
        self.bricks: list[list] = create_bricks(1)
        self.powerups: list[list] = []

    def start(self):
        while self.running:
            # --- CHECK EXIT ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # --- INTERFACE DRAW ---
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.background_image, (5, UI_HEIGHT + 5))

            pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(0, 0, WIN_WIDTH, UI_HEIGHT)) # UI

            lives_text = self.fg_font.render("SCORE", True, self.fg_font_color1)
            self.screen.blit(lives_text, (WIN_WIDTH - 3 * WIN_WIDTH / 4 - len("SCORE") / 2, 5))
            lives_text = self.fg_font.render(str(self.score), True, self.fg_font_color2)
            self.screen.blit(lives_text, (WIN_WIDTH - 3 * WIN_WIDTH / 4 + 25, 25))
            
            score_text = self.fg_font.render("HIGH SCORE", True, self.fg_font_color1)
            self.screen.blit(score_text, (WIN_WIDTH - 2 * WIN_WIDTH / 4 - len("HIGH SCORE") / 2, 5))
            score_number_text = self.fg_font.render(str(self.highscore), True, self.fg_font_color2)
            self.screen.blit(score_number_text, (WIN_WIDTH - 2 * WIN_WIDTH / 4 + 25, 25))
            
            # --- BRICK COLLIDE ---
            for block in self.bricks:
                if self.ball_pos.colliderect(block[0], block[1], 36, 15):
                    pygame.mixer.Sound.play(pygame.mixer.Sound(resource_path(r'assets\audio\ping.wav')))
                    if random.randint(1, 10) == 10: # 10%
                        self.powerups.append([block[0], block[1]+10, 1])
                    if random.randint(1, 20) == 20: # 5%
                        self.powerups.append([block[0], block[1]+10, 2])
                    if block[3] == 1:
                        self.bricks.remove(block)
                    else:
                        block[3] -= 1
                    self.score += 10 * self.level
                    self.ball_dir_y *= -1
                    if len(self.bricks) == 0: # new level
                        self.level += 1
                        play_level_music(self.level)
                        self.bricks = create_bricks(self.level)
                        self.score += 250 * self.level
                        self.player_pos = default_player_pos()
                        self.ball_pos = default_ball_pos()
                        self.player_step: int = 300
                        self.ball_step: int = 350
                        self.ball_dir_x = 1
                        self.ball_dir_y = 1
                        self.ball_ang = 0
                    if self.score > self.highscore: # new highscore
                        highscore = self.score
                        file = open('highscore', 'wb')
                        save = {'highscore': highscore}
                        pickle.dump(save, file)
                        file.close()
                    if self.score >= 2500 * self.bonus: # life bonus
                        self.lives += 1
                        self.bonus += 1

            # --- BRICK DRAW ---
            for block in self.bricks:
                brick_color = block[2]
                if block[3] == 1:
                    pygame.draw.rect(self.screen, "black", (block[0]-1, block[1]-1, 36, 17))
                    pygame.draw.rect(self.screen, brick_color, (block[0], block[1], 34, 15))
                elif block[3] == 2:
                    pygame.draw.rect(self.screen, "white", (block[0]-2, block[1]-2, 36, 17))
                    pygame.draw.rect(self.screen, "black", (block[0]-1, block[1]-1, 36, 17))
                    pygame.draw.rect(self.screen, brick_color, (block[0], block[1], 34, 14))

            for powerup in self.powerups:
                if powerup[2] == 1:
                    self.screen.blit(self.powerup1_image, (powerup[0], powerup[1]))
                elif powerup[2] == 2:
                    self.screen.blit(self.powerup2_image, (powerup[0], powerup[1]))
                if powerup[1] > WIN_HEIGHT:
                    self.powerups.remove(powerup)
                if self.player_pos.colliderect((powerup[0], powerup[1], 25, 10)):
                    if powerup[2] == 1:
                        self.ball_step = int(1.25 * self.ball_step)
                    elif powerup[2] == 2:
                        self.lives += 1
                    self.powerups.remove(powerup)
                powerup[1] += 100 * self.dt

            # --- PLAYER\BALL DRAW ---
            self.screen.blit(self.ball_image, self.ball_pos)
            self.screen.blit(self.paddle_image, self.player_pos)
            
            for life_number in range(self.lives):
                self.screen.blit(self.paddle_icon_image, (10 + life_number * 35, WIN_HEIGHT - 15, 30, 8))

            # --- BALL PHYSICS ---
            if self.ball_pos.centery > WIN_HEIGHT: # dead
                if self.lives > 0:
                    pygame.mixer.Sound.play(pygame.mixer.Sound(resource_path(r'assets\audio\drop.wav')))
                    self.lives -= 1
                    self.player_pos = default_player_pos()
                    self.ball_pos = default_ball_pos()
                    self.player_step: int = 300
                    self.ball_step: int = 350
                    self.ball_dir_x = 1
                    self.ball_dir_y = 1
                    self.ball_ang = 0
                else:
                    pygame.mixer.Sound.play(pygame.mixer.Sound(resource_path(r'assets\audio\crash.wav')))
                    self.__init__(self.screen)

            if self.ball_pos.centerx < 15:
                self.ball_dir_x *= -1
            elif self.ball_pos.centerx > WIN_WIDTH - 15:
                self.ball_dir_x *= -1
            
            if self.ball_pos.centery < UI_HEIGHT + 10:
                self.ball_dir_y *= -1
            
            # --- BALL\PLAYER COLLIDE ---
            if self.ball_pos.colliderect(self.player_pos):
                self.ball_dir_y = -1
                self.ball_dir_x = 1
                if self.ball_pos.centerx < self.player_pos.centerx:
                    self.ball_ang = -(self.player_pos.centerx - self.ball_pos.centerx)
                elif self.ball_pos.centerx > self.player_pos.centerx:
                    self.ball_ang = (self.ball_pos.centerx - self.player_pos.centerx)
                    
            # --- BALL UPDATE ---
            y = self.ball_step * self.dt * self.ball_dir_y
            x = 10 * self.ball_ang * self.dt * self.ball_dir_x
            self.ball_pos = self.ball_pos.move(x, y)
            
            # --- INPUT ---
            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_a] or keys[pygame.K_w] or keys[pygame.K_LEFT] or keys[pygame.K_UP]: # left
                if self.player_pos.right - 5 - (self.player_step * self.dt) >= 0:
                    self.player_pos = self.player_pos.move((-1 * self.player_step * self.dt, 0))
            elif keys[pygame.K_d] or keys[pygame.K_s] or keys[pygame.K_RIGHT] or keys[pygame.K_DOWN]: # right
                if self.player_pos.left + 5 + (self.player_step * self.dt) <= WIN_WIDTH:
                    self.player_pos = self.player_pos.move((self.player_step * self.dt, 0))
            elif keys[pygame.K_ESCAPE]:
                self.running = False
            
            # --- DRAW FRAME ---
            self.screen.blit(self.frame_image, (0, UI_HEIGHT))
            
            # --- END FRAME ---
            pygame.display.flip() # bufferswap
            self.dt = self.clock.tick(FPS_TARGET) / 1000 # limit fps

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption('Breaker')
    pygame.display.set_icon(pygame.image.load(resource_path(r'assets\image\ball.ico')))
    screen: pygame.surface.Surface = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    new_game = game(screen)
    new_game.start()
    pygame.quit()
