import pygame
import random

FPS = 60
WIDTH = 480
HEIGHT = 640

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Breaker')

background_image = pygame.image.load('background.jpg')
ball_image = pygame.image.load('red_ball.png')
pygame.display.set_icon(ball_image)

clock = pygame.time.Clock()
running = True

fg_font = pygame.font.SysFont("impact", 32)
bg_font = pygame.font.SysFont("impact", 32)
bg_color = (255, 255, 255)

dt = 0
player_step = 150
ball_step = 300
score = 0
lives = 3

player_pos = pygame.rect.Rect(WIDTH / 2 - 68 / 2, HEIGHT - 50, 68, 8)
ball_pos = pygame.rect.Rect(WIDTH / 2 - 8 / 2, HEIGHT / 2, 8, 8)

ball_dir_x = 1
ball_dir_y = 1
ball_ang = 0

brick_color = [0, 0, 0]
def create_bricks() -> list:
    level = []
    x = 5
    y = 25
    for _ in range(5):
        brick_color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        for _ in range(10):
            x += 40
            level.append((x, y, brick_color))
        y += 25
        x = 5
    return level

bricks = create_bricks()


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("grey")
    screen.blit(background_image, (0, 0))
    pygame.draw.rect(screen, (75, 75, 75), pygame.Rect(0, HEIGHT - 40, WIDTH, 6))
    
    for block in bricks:
        if ball_pos.colliderect(block[0], block[1], 35, 10):
            bricks.remove(block)
            score += 10
            ball_dir_y *= -1
        if len(bricks) == 0: # new level
            bricks = create_bricks()
            score += 250
            player_pos = pygame.rect.Rect(WIDTH / 2 - 68 / 2, HEIGHT - 50, 68, 8)
            ball_pos = pygame.rect.Rect(WIDTH / 2 - 8 / 2, HEIGHT / 2, 8, 8)
            ball_dir_x = 1
            ball_dir_y = 1
            ball_ang = 0
            
    for block in bricks:
        brick_color = block[2]
        pygame.draw.rect(screen, "black", (block[0], block[1], 35, 10), 35)
        pygame.draw.rect(screen, brick_color, (block[0], block[1], 32, 8), 35)
        
    pygame.draw.rect(screen, "black", (player_pos.x, player_pos.y, 70, 10), 20)
    pygame.draw.rect(screen, "orange", player_pos, 17)
    
    screen.blit(ball_image, ball_pos)
    
    score_text = bg_font.render("Score: " + str(score), True, "black")
    screen.blit(score_text, (5 + 2, HEIGHT - 40 + 2))
    lives_text = bg_font.render("Lives: " + str(lives), True, "black")
    screen.blit(lives_text, (WIDTH - 100 + 2, HEIGHT - 40 + 2))
    
    score_text = fg_font.render("Score: " + str(score), True, "green")
    screen.blit(score_text, (5, HEIGHT - 40))
    lives_text = fg_font.render("Lives: " + str(lives), True, "green")
    screen.blit(lives_text, (WIDTH - 100, HEIGHT - 40))
    
    if ball_pos.centery >= HEIGHT: # dead
        player_pos = pygame.rect.Rect(WIDTH / 2 - 68 / 2, HEIGHT - 50, 68, 8)
        ball_pos = pygame.rect.Rect(WIDTH / 2 - 8 / 2, HEIGHT / 2, 8, 8)
        ball_dir_x = 1
        ball_dir_y = 1
        ball_ang = 0
        lives -= 1
        if lives < 0:
            lives = 3
            score = 0
            bricks = create_bricks()
    
    if ball_pos.centerx <= 0:
        ball_dir_x *= -1
    elif ball_pos.centerx >= WIDTH:
        ball_dir_x *= -1
    
    if ball_pos.top <= 0:
        ball_dir_y *= -1
    
    elif ball_pos.colliderect(player_pos):
        ball_dir_y *= -1
        if ball_pos.centerx < player_pos.centerx:
            ball_ang -= dt * ball_step * (player_pos.centerx - ball_pos.centerx)
        elif ball_pos.centerx > player_pos.centerx:
            ball_ang += dt * ball_step * (ball_pos.centerx - player_pos.centerx)
    
    ball_pos.centery += ball_step * dt * ball_dir_y
    ball_pos.centerx += ball_ang * dt * ball_dir_x
    
    keys = pygame.key.get_pressed()

    if keys[pygame.K_a] or keys[pygame.K_w] or keys[pygame.K_LEFT] or keys[pygame.K_UP]:
        if player_pos.centerx - player_step * dt >= 0:
            player_pos.x -= player_step * dt
    if keys[pygame.K_d] or keys[pygame.K_s] or keys[pygame.K_RIGHT] or keys[pygame.K_DOWN]:
        if player_pos.centerx + player_step * dt <= WIDTH:
            player_pos.x += player_step * dt

    pygame.display.flip() # bufferswap
    dt = clock.tick(FPS) / 1000 # limit fps

pygame.quit()