import pygame
import random

FPS = 60
WIDTH = 480
HEIGHT = 640
UI_HEIGHT = 55

pygame.init()
screen: pygame.surface.Surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Breaker')

background_image = pygame.image.load('background.jpg')
frame_image = pygame.image.load('frame.png')
ball_image = pygame.image.load('ball.png')
pygame.display.set_icon(ball_image)

clock = pygame.time.Clock()
running = True

fg_font: pygame.font.Font = pygame.font.SysFont("arial", 28)
fg_font_color1 = (255, 0, 0)
fg_font_color2 = (255, 255, 255)

dt = 0
player_step = 300
ball_step = 350

score = 0
lives = 3

player_pos = pygame.rect.Rect(WIDTH / 2 - 68 / 2, HEIGHT - 55, 70, 8)
ball_pos = pygame.rect.Rect(WIDTH / 2 - 8 / 2, HEIGHT / 2, 8, 8)

ball_dir_x = 1
ball_dir_y = 1
ball_ang = 0

brick_color = [0, 0, 0]
def create_bricks() -> list:
    level = []
    x = -22
    y = UI_HEIGHT + 50
    for _ in range(6):
        brick_color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        for _ in range(13):
            x += 35
            level.append((x, y, brick_color))
        y += 15
        x = -22
    return level

bricks = create_bricks()

while running:
    # --- CHECK EXIT ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- INTERFACE DRAW ---
    screen.fill("grey")
    screen.blit(background_image, (0, UI_HEIGHT))

    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, 0, WIDTH, UI_HEIGHT)) # UI

    lives_text = fg_font.render("Lives", True, fg_font_color1)
    screen.blit(lives_text, (WIDTH / 3 - len("Lives") / 3, 0))
    lives_text = fg_font.render(str(lives), True, fg_font_color2)
    screen.blit(lives_text, (WIDTH / 3 - len("Lives") / 3 + 20, 23))
    
    score_text = fg_font.render("Score", True, fg_font_color1)
    screen.blit(score_text, (WIDTH / 2 - len("Score") / 2, 0))
    score_number_text = fg_font.render(str(score), True, fg_font_color2)
    screen.blit(score_number_text, (WIDTH / 2 - len("Score") / 2 + 20, 23))
    
    # --- BRICK COLLIDE ---
    for block in bricks:
        if ball_pos.colliderect(block[0], block[1], 35, 15):
            bricks.remove(block)
            score += 10
            ball_dir_y *= -1
            if len(bricks) == 0: # new level
                bricks = create_bricks()
                score += 250
                player_pos = pygame.rect.Rect(WIDTH / 2 - 68 / 2, HEIGHT - 55, 70, 8)
                ball_pos = pygame.rect.Rect(WIDTH / 2 - 8 / 2, HEIGHT / 2, 8, 8)
                ball_dir_x = 1
                ball_dir_y = 1
                ball_ang = 0

    # --- BRICK DRAW ---
    for block in bricks:
        brick_color = block[2]
        pygame.draw.rect(screen, "black", (block[0]-1, block[1]-1, 35, 15))
        pygame.draw.rect(screen, brick_color, (block[0], block[1], 33, 13))

    # --- PLAYER/BALL DRAW ---
    screen.blit(ball_image, ball_pos)
    pygame.draw.rect(screen, "orange", (player_pos.x, player_pos.y, 70, 10), 20)
    pygame.draw.rect(screen, "grey", (player_pos.x+2, player_pos.y, 66, 10), 16)

    # --- BALL PHYSICS ---
    if ball_pos.centery >= HEIGHT: # dead
        player_pos = pygame.rect.Rect(WIDTH / 2 - 68 / 2, HEIGHT - 55, 70, 8)
        ball_pos = pygame.rect.Rect(WIDTH / 2 - 8 / 2, HEIGHT / 2, 8, 8)
        ball_dir_x = 1
        ball_dir_y = 1
        ball_ang = 0
        lives -= 1
        if lives < 0:
            lives = 3
            score = 0
            bricks = create_bricks()
    
    if ball_pos.centerx < 12:
        ball_dir_x *= -1
    elif ball_pos.centerx > WIDTH - 12:
        ball_dir_x *= -1
    
    if ball_pos.top <= UI_HEIGHT + 10:
        ball_dir_y *= -1
    
    # --- BALL/PLAYER COLLIDE ---
    if ball_pos.colliderect(player_pos):
        ball_dir_y *= -1
        if ball_pos.centerx < player_pos.centerx:
            ball_ang -= dt * ball_step * (player_pos.centerx - ball_pos.centerx)
        elif ball_pos.centerx > player_pos.centerx:
            ball_ang += dt * ball_step * (ball_pos.centerx - player_pos.centerx)
    
    # --- BALL UPDATE ---
    ball_pos.centery += int(ball_step * dt * ball_dir_y)
    ball_pos.centerx += int(ball_ang * dt * ball_dir_x)
    
    # --- INPUT ---
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_a] or keys[pygame.K_w] or keys[pygame.K_LEFT] or keys[pygame.K_UP]: # left
        if player_pos.centerx - (player_step * dt) >= 0:
            player_pos = player_pos.move((-1 * player_step * dt, 0))
    elif keys[pygame.K_d] or keys[pygame.K_s] or keys[pygame.K_RIGHT] or keys[pygame.K_DOWN]: # right
        if player_pos.centerx + (player_step * dt) <= WIDTH:
            player_pos = player_pos.move((player_step * dt, 0))
    
    # --- DRAW FRAME ---
    screen.blit(frame_image, (0, UI_HEIGHT))
    
    # --- END FRAME ---
    pygame.display.flip() # bufferswap
    dt = clock.tick(FPS) / 1000 # limit fps

pygame.quit()