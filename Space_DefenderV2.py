"""
Space Defender v2.0.0
A classic space shooter built with Pygame.
GitHub: https://github.com/yourusername/space-defender

MIT License | © 2025
"""

import pygame
import json
import os
import sys
from datetime import datetime

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# === CONFIGURATION ===
CONFIG_FILE = "config.json"
HIGHSCORE_FILE = "highscore.json"
ASSETS_DIR = "assets"

# Load config
def load_config():
    default = {
        "window_width": 800,
        "window_height": 600,
        "fps": 60,
        "player_speed": 7,
        "bullet_speed": 12,
        "enemy_spawn_rate": 90,
        "enemy_speed": 3,
        "max_health": 100,
        "volume": 0.5
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return {**default, **json.load(f)}
    return default

config = load_config()

# Screen
WIDTH, HEIGHT = config["window_width"], config["window_height"]
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Defender v2.0")

# Clock
clock = pygame.time.Clock()
FPS = config["fps"]

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 80, 80)
GREEN = (80, 255, 80)
YELLOW = (255, 220, 0)
BLUE = (0, 150, 255)

# Fonts
FONT_LARGE = pygame.font.SysFont("consolas", 48, bold=True)
FONT_MED = pygame.font.SysFont("consolas", 36)
FONT_SMALL = pygame.font.SysFont("consolas", 24)

# === ASSET LOADER ===
def load_asset(filename, size=None):
    path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(path):
        return None
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img

def load_sound(filename):
    path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(path):
        return None
    sound = pygame.mixer.Sound(path)
    sound.set_volume(config["volume"])
    return sound

# Load assets
player_img = load_asset("player.png", (60, 60))
enemy_img = load_asset("enemy.png", (50, 50))
bullet_img = load_asset("bullet.png", (8, 16))
shoot_sound = load_sound("shoot.wav")
hit_sound = load_sound("hit.wav")

# === HIGH SCORE SYSTEM ===
def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as f:
            data = json.load(f)
            return data.get("score", 0), data.get("date", "")
    return 0, ""

def save_highscore(score):
    data = {
        "score": score,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    with open(HIGHSCORE_FILE, "w") as f:
        json.dump(data, f, indent=2)

high_score, high_date = load_highscore()

# === GAME OBJECTS ===
player_pos = [WIDTH // 2, HEIGHT - 100]
player_health = config["max_health"]
bullets = []
enemies = []
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)) for _ in range(120)]

# Game state
score = 0
paused = False
muted = False
game_over = False
start_screen = True

# === FUNCTIONS ===
def reset_game():
    global player_pos, player_health, score, bullets, enemies
    player_pos = [WIDTH // 2, HEIGHT - 100]
    player_health = config["max_health"]
    score = 0
    bullets.clear()
    enemies.clear()

def spawn_enemy():
    x = random.randint(30, WIDTH - 80)
    y = -60
    enemies.append([x, y, config["enemy_speed"] + random.uniform(-1, 1)])

def draw_stars():
    for i, (x, y, size) in enumerate(stars):
        y = (y + size * 0.5) % HEIGHT
        stars[i] = (x, y, size)
        pygame.draw.circle(screen, WHITE, (x, int(y)), size)

def draw_player():
    x, y = player_pos
    if player_img:
        screen.blit(player_img, (x - 30, y - 30))
    else:
        points = [(x, y + 30), (x - 25, y - 25), (x + 25, y - 25)]
        pygame.draw.polygon(screen, BLUE, points)

def draw_bullet(b):
    if bullet_img:
        screen.blit(bullet_img, (b[0] - 4, b[1] - 8))
    else:
        pygame.draw.rect(screen, YELLOW, (b[0] - 3, b[1] - 10, 6, 20))

def draw_enemy(e):
    if enemy_img:
        screen.blit(enemy_img, (e[0], e[1]))
    else:
        pygame.draw.rect(screen, RED, (e[0], e[1], 50, 50), border_radius=10)

def draw_hud():
    # Health
    bar_w = 250
    fill = (player_health / config["max_health"]) * bar_w
    pygame.draw.rect(screen, (40, 40, 40), (20, 20, bar_w, 20))
    pygame.draw.rect(screen, GREEN if player_health > 30 else RED, (20, 20, fill, 20))
    health_text = FONT_SMALL.render(f"HP: {int(player_health)}", True, WHITE)
    screen.blit(health_text, (20, 45))

    # Score
    score_text = FONT_SMALL.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH - 160, 20))

    # High Score
    hs_text = FONT_SMALL.render(f"High: {high_score}", True, YELLOW)
    screen.blit(hs_text, (WIDTH - 160, 50))

def show_start():
    screen.fill((5, 5, 20))
    draw_stars()
    title = FONT_LARGE.render("SPACE DEFENDER", True, (0, 200, 255))
    start = FONT_MED.render("Press SPACE to Start", True, WHITE)
    info = FONT_SMALL.render("WASD/Arrows: Move | SPACE: Shoot | P: Pause | M: Mute", True, (180, 180, 180))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 180))
    screen.blit(start, (WIDTH//2 - start.get_width()//2, 280))
    screen.blit(info, (WIDTH//2 - info.get_width()//2, 350))
    pygame.display.flip()

def show_pause():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    pause = FONT_LARGE.render("PAUSED", True, YELLOW)
    resume = FONT_SMALL.render("Press P to Resume", True, WHITE)
    screen.blit(pause, (WIDTH//2 - pause.get_width()//2, HEIGHT//2 - 50))
    screen.blit(resume, (WIDTH//2 - resume.get_width()//2, HEIGHT//2 + 20))

def show_game_over():
    screen.fill((10, 0, 15))
    draw_stars()
    over = FONT_LARGE.render("GAME OVER", True, RED)
    final = FONT_MED.render(f"Score: {score}", True, WHITE)
    if score > high_score:
        final = FONT_MED.render(f"NEW HIGH SCORE: {score}!", True, YELLOW)
        save_highscore(score)
    restart = FONT_SMALL.render("Press R to Restart", True, WHITE)
    screen.blit(over, (WIDTH//2 - over.get_width()//2, 180))
    screen.blit(final, (WIDTH//2 - final.get_width()//2, 260))
    screen.blit(restart, (WIDTH//2 - restart.get_width()//2, 340))
    pygame.display.flip()

# === MAIN LOOP ===
import random  # moved here to avoid top-level

running = True
spawn_timer = 0

while running:
    screen.fill((5, 5, 20))
    draw_stars()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if start_screen and event.key == pygame.K_SPACE:
                start_screen = False
                reset_game()

            if game_over and event.key == pygame.K_r:
                start_screen = True
                game_over = False
                continue

            if event.key == pygame.K_p:
                if not start_screen and not game_over:
                    paused = not paused

            if event.key == pygame.K_m:
                muted = not muted
                vol = 0 if muted else config["volume"]
                for sound in (shoot_sound, hit_sound):
                    if sound:
                        sound.set_volume(vol)

            if not start_screen and not game_over and not paused and event.key == pygame.K_SPACE:
                bullets.append([player_pos[0], player_pos[1] - 30])
                if shoot_sound and not muted:
                    shoot_sound.play()

    if start_screen:
        show_start()
        clock.tick(30)
        continue

    if game_over:
        show_game_over()
        clock.tick(30)
        continue

    if paused:
        show_pause()
        pygame.display.flip()
        clock.tick(30)
        continue

    # === PLAYER MOVEMENT ===
    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= config["player_speed"]
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += config["player_speed"]
    if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= config["player_speed"]
    if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += config["player_speed"]

    player_pos[0] = max(30, min(WIDTH - 30, player_pos[0] + dx))
    player_pos[1] = max(50, min(HEIGHT - 50, player_pos[1] + dy))

    # === SPAWN ENEMIES ===
    spawn_timer += 1
    if spawn_timer >= config["enemy_spawn_rate"]:
        spawn_enemy()
        spawn_timer = 0

    # === UPDATE BULLETS ===
    for b in bullets[:]:
        b[1] -= config["bullet_speed"]
        if b[1] < -20:
            bullets.remove(b)

    # === UPDATE ENEMIES ===
    for e in enemies[:]:
        e[1] += e[2]
        if e[1] > HEIGHT:
            enemies.remove(e)
            player_health -= 15

    # === COLLISIONS ===
    player_rect = pygame.Rect(player_pos[0]-30, player_pos[1]-30, 60, 60)
    for b in bullets[:]:
        br = pygame.Rect(b[0]-4, b[1]-8, 8, 16)
        for e in enemies[:]:
            er = pygame.Rect(e[0], e[1], 50, 50)
            if br.colliderect(er):
                bullets.remove(b)
                enemies.remove(e)
                score += 10
                if hit_sound and not muted:
                    hit_sound.play()
                break

    for e in enemies[:]:
        er = pygame.Rect(e[0], e[1], 50, 50)
        if player_rect.colliderect(er):
            enemies.remove(e)
            player_health -= 25

    # === DRAW ===
    draw_player()
    for b in bullets: draw_bullet(b)
    for e in enemies: draw_enemy(e)
    draw_hud()

    if player_health <= 0 and not game_over:
        game_over = True
        if score > high_score:
            save_highscore(score)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()