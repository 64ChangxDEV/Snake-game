# space_defender.py
import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Defender")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)

# Clock & FPS
clock = pygame.time.Clock()
FPS = 60

# Fonts
font = pygame.font.SysFont("Arial", 36)
small_font = pygame.font.SysFont("Arial", 24)

# Player
player_size = 50
player_pos = [WIDTH // 2, HEIGHT - 2 * player_size]
player_speed = 7
player_health = 100

# Bullet
bullet_size = 5
bullet_speed = 15
bullets = []

# Enemy
enemy_size = 40
enemy_speed = 3
enemies = []

# Score
score = 0

# Game states
GAME_OVER = False
START_SCREEN = True

# Sounds (optional - will skip if file not found)
try:
    shoot_sound = pygame.mixer.Sound("shoot.wav")
    hit_sound = pygame.mixer.Sound("hit.wav")
except:
    shoot_sound = hit_sound = None

# Functions
def draw_player():
    pygame.draw.polygon(screen, BLUE,
                        [(player_pos[0], player_pos[1] + player_size),
                         (player_pos[0] - player_size//2, player_pos[1] - player_size//2),
                         (player_pos[0] + player_size//2, player_pos[1] - player_size//2)])

def draw_bullet(bullet):
    pygame.draw.circle(screen, YELLOW, (int(bullet[0]), int(bullet[1])), bullet_size)

def draw_enemy(enemy):
    pygame.draw.rect(screen, RED, (enemy[0], enemy[1], enemy_size, enemy_size))

def draw_health_bar():
    pygame.draw.rect(screen, RED, (20, 20, 200, 20))
    pygame.draw.rect(screen, GREEN, (20, 20, player_health * 2, 20))
    health_text = small_font.render(f"Health: {player_health}", True, WHITE)
    screen.blit(health_text, (20, 45))

def spawn_enemy():
    x = random.randint(0, WIDTH - enemy_size)
    y = -enemy_size
    enemies.append([x, y])

def show_start_screen():
    screen.fill(BLACK)
    title = font.render("SPACE DEFENDER", True, WHITE)
    start_text = small_font.render("Press SPACE to Start", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
    screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, 300))
    pygame.display.flip()

def show_game_over():
    screen.fill(BLACK)
    over_text = font.render("GAME OVER", True, RED)
    score_text = small_font.render(f"Score: {score}", True, WHITE)
    restart_text = small_font.render("Press R to Restart", True, WHITE)
    screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, 200))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 280))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 340))
    pygame.display.flip()

# Main Game Loop
running = True
enemy_spawn_timer = 0

while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if START_SCREEN and event.key == pygame.K_SPACE:
                START_SCREEN = False
                # Reset game
                player_pos = [WIDTH // 2, HEIGHT - 2 * player_size]
                player_health = 100
                score = 0
                bullets.clear()
                enemies.clear()
                enemy_spawn_timer = 0

            if GAME_OVER and event.key == pygame.K_r:
                # Restart
                START_SCREEN = True
                GAME_OVER = False
                continue

            if not START_SCREEN and not GAME_OVER and event.key == pygame.K_SPACE:
                # Shoot
                bullet_x = player_pos[0]
                bullet_y = player_pos[1] - player_size // 2
                bullets.append([bullet_x, bullet_y])
                if shoot_sound:
                    shoot_sound.play()

    if START_SCREEN:
        show_start_screen()
        clock.tick(30)
        continue

    if GAME_OVER:
        show_game_over()
        clock.tick(30)
        continue

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player_pos[0] -= player_speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player_pos[0] += player_speed
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        player_pos[1] -= player_speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        player_pos[1] += player_speed

    # Keep player in bounds
    player_pos[0] = max(player_size//2, min(WIDTH - player_size//2, player_pos[0]))
    player_pos[1] = max(player_size//2, min(HEIGHT - player_size//2, player_pos[1]))

    # Spawn enemies
    enemy_spawn_timer += 1
    if enemy_spawn_timer > 60:  # every 1 second
        spawn_enemy()
        enemy_spawn_timer = 0

    # Update bullets
    for bullet in bullets[:]:
        bullet[1] -= bullet_speed
        if bullet[1] < 0:
            bullets.remove(bullet)

    # Update enemies
    for enemy in enemies[:]:
        enemy[1] += enemy_speed
        if enemy[1] > HEIGHT:
            enemies.remove(enemy)
            player_health -= 10
            if player_health <= 0:
                GAME_OVER = True

    # Collision: bullet vs enemy
    for bullet in bullets[:]:
        bullet_rect = pygame.Rect(bullet[0]-bullet_size, bullet[1]-bullet_size, bullet_size*2, bullet_size*2)
        for enemy in enemies[:]:
            enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy_size, enemy_size)
            if bullet_rect.colliderect(enemy_rect):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 10
                if hit_sound:
                    hit_sound.play()
                break

    # Collision: enemy vs player
    player_rect = pygame.Rect(player_pos[0]-player_size//2, player_pos[1]-player_size//2, player_size, player_size)
    for enemy in enemies[:]:
        enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy_size, enemy_size)
        if player_rect.colliderect(enemy_rect):
            enemies.remove(enemy)
            player_health -= 20
            if player_health <= 0:
                GAME_OVER = True

    # Draw everything
    draw_player()
    for bullet in bullets:
        draw_bullet(bullet)
    for enemy in enemies:
        draw_enemy(enemy)

    # HUD
    score_text = small_font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH - 150, 20))
    draw_health_bar()

    # Game over check
    if player_health <= 0 and not GAME_OVER:
        GAME_OVER = True

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()