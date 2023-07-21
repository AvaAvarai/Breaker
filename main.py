import pygame
import random

TITLE = 'Breaker'
WIDTH = 480
HEIGHT = 640

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)

background_image = pygame.image.load('digital-texture-blue.jpg')

ball_image = pygame.image.load('red_ball.png')
pygame.display.set_icon(ball_image)

clock = pygame.time.Clock()
running = True

font = pygame.font.SysFont("impact", 32)

dt = 0
player_step = 150
ball_step = 300
score = 0
lives = 3

player_pos = pygame.rect.Rect(WIDTH / 2, HEIGHT - 50, 68, 8)
ball_pos = pygame.rect.Rect(WIDTH / 2, HEIGHT / 2, 8, 8)

ball_dir_x = 1
ball_dir_y = 1
ball_ang = 0

blocks_color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
blocks = []
x = 5
y = 25
for _ in range(5):
    for _ in range(10):
        x += 40
        blocks.append((x, y))
    y += 25
    x = 5

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("grey")
    screen.blit(background_image, (0, 0))
    
    for block in blocks:
        if ball_pos.colliderect(block[0], block[1], 35, 10):
            blocks.remove(block)
            score += 10
        if len(blocks) == 0:
            x = 5
            y = 25
            for _ in range(5):
                for _ in range(10):
                    x += 40
                    blocks.append((x, y))
                y += 25
                x = 5
            score += 250
            blocks_color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
            
    for block in blocks:
        pygame.draw.rect(screen, "black", (block[0], block[1], 35, 10), 35)
        pygame.draw.rect(screen, blocks_color, (block[0], block[1], 32, 8), 35)
        
    pygame.draw.rect(screen, "black", (player_pos.x, player_pos.y, 70, 10), 40)
    pygame.draw.rect(screen, "orange", player_pos, 38)
    
    screen.blit(ball_image, ball_pos)
    
    score_text = font.render("Score: " + str(score), True, "darkgreen")
    screen.blit(score_text, (5, HEIGHT - 40))
    lives_text = font.render("Lives: " + str(lives), True, "darkgreen")
    screen.blit(lives_text, (WIDTH - 100, HEIGHT - 40))
    
    if ball_pos.centery >= HEIGHT:
        player_pos = pygame.rect.Rect(WIDTH / 2, HEIGHT - 50, 38, 8)
        ball_pos = pygame.rect.Rect(WIDTH / 2, HEIGHT / 2, 8, 8)
        ball_dir_x = 1
        ball_dir_y = 1
        ball_ang = 0
        lives -= 1
        if lives < 0:
            lives = 3
            score = 0
            x = 5
            y = 25
            for _ in range(5):
                for _ in range(10):
                    x += 40
                    blocks.append((x, y))
                y += 25
                x = 5
            blocks_color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
    
    if ball_pos.centerx <= 0:
        ball_dir_x *= -1
    elif ball_pos.centerx >= WIDTH:
        ball_dir_x *= -1
    
    if ball_pos.top <= 0:
        ball_dir_y *= -1
    
    elif ball_pos.colliderect(player_pos):
        ball_dir_y *= -1
        if ball_pos.centerx < player_pos.centerx:
            ball_ang -= dt * abs(ball_pos.centerx - player_pos.centerx)
        elif ball_pos.centerx > player_pos.centerx:
            ball_ang += dt * abs(ball_pos.centerx - player_pos.centerx)
    
    ball_pos.centery += ball_step * dt * ball_dir_y
    ball_pos.centerx += ball_ang * dt * ball_dir_x
    
    keys = pygame.key.get_pressed()

    if keys[pygame.K_a] or keys[pygame.K_w]:
        if player_pos.centerx - player_step * dt >= 0:
            player_pos.x -= player_step * dt
    if keys[pygame.K_d] or keys[pygame.K_s]:
        if player_pos.centerx + player_step * dt <= WIDTH:
            player_pos.x += player_step * dt

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    dt = clock.tick(60) / 1000

pygame.quit()