import pygame
import sys
import random
import tkinter as tk
from tkinter import messagebox
import math

pygame.init()
clock = pygame.time.Clock()

# Základní nastavení
width, height = 1800, 900
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Flappy Bird - 3 hráči")
is_fullscreen = False

# Barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (230, 230, 0)
DARK_YELLOW = (200, 200, 0)

# Herní konstanty
gravity = 0.5
jump_strength = 10
pipe_width = 100
pipe_gap = 300
pipe_frequency = 1500
pipe_speed = 5
pipe_lip_width = pipe_width + 20
pipe_lip_height = 10

# Hráči
background_image = pygame.image.load("background.png").convert()
background_offset = 0
players = [
    pygame.Rect(100, 400, 80, 60),
    pygame.Rect(200, 400, 80, 60),
    pygame.Rect(300, 400, 80, 60),
]
# Načtení obrázků hráčů
player_images = [
    pygame.image.load("player1.png").convert_alpha(),
    pygame.image.load("player2.png").convert_alpha(),
    pygame.image.load("player3.png").convert_alpha(),
]
player_velocities = [0, 0, 0]
scores = [0, 0, 0]
alive = [True, True, True]

# Trubky
pipes = []
last_pipe = pygame.time.get_ticks()
scored_pipes = [set() for _ in range(3)]

paused = False

# Funkce pro vykreslení hráčů
def draw_window(player_rect, player_image, scale_x, scale_y):
    scaled_image = pygame.transform.scale(player_image, (int(player_rect.width * scale_x), int(player_rect.height * scale_y)))
    screen.blit(scaled_image, (player_rect.x * scale_x, player_rect.y * scale_y))

def draw_background(offset, screen_width, screen_height):
    bg_width, bg_height = background_image.get_size()
    scale_factor = screen_width / bg_width
    new_width = int(bg_width * scale_factor)
    new_height = int(bg_height * scale_factor)
    scaled_bg = pygame.transform.scale(background_image, (new_width, new_height))
    if new_height < screen_height:
        scale_factor = screen_height / bg_height
        new_width = int(bg_width * scale_factor)
        new_height = int(bg_height * scale_factor)
        scaled_bg = pygame.transform.scale(background_image, (new_width, new_height))
    start_x = offset % new_width - new_width
    end_x = screen_width + new_width
    x = start_x
    y = screen_height - new_height
    while x < end_x:
        screen.blit(scaled_bg, (x, y))
        x += new_width
    return new_width

# Funkce pro vykreslení trubek
def draw_pipes(scale_x, scale_y):
    for pipe in pipes:
        top_scaled = pygame.Rect(
            pipe['top'].x * scale_x, pipe['top'].y * scale_y,
            pipe['top'].width * scale_x, pipe['top'].height * scale_y
        )
        bottom_scaled = pygame.Rect(
            pipe['bottom'].x * scale_x, pipe['bottom'].y * scale_y,
            pipe['bottom'].width * scale_x, pipe['bottom'].height * scale_y
        )
        pygame.draw.rect(screen, YELLOW, top_scaled)
        pygame.draw.rect(screen, YELLOW, bottom_scaled)
        top_lip_bottom = pygame.Rect(
            (pipe['top'].x - (pipe_lip_width - pipe_width) / 2) * scale_x,
            (pipe['top'].y + pipe['top'].height - pipe_lip_height) * scale_y,
            pipe_lip_width * scale_x, pipe_lip_height * scale_y
        )
        top_lip_top = pygame.Rect(
            (pipe['top'].x - (pipe_lip_width - pipe_width) / 2) * scale_x,
            pipe['top'].y * scale_y,
            pipe_lip_width * scale_x, pipe_lip_height * scale_y
        )
        bottom_lip_top = pygame.Rect(
            (pipe['bottom'].x - (pipe_lip_width - pipe_width) / 2) * scale_x,
            pipe['bottom'].y * scale_y,
            pipe_lip_width * scale_x, pipe_lip_height * scale_y
        )
        bottom_lip_bottom = pygame.Rect(
            (pipe['bottom'].x - (pipe_lip_width - pipe_width) / 2) * scale_x,
            (pipe['bottom'].y + pipe['bottom'].height - pipe_lip_height) * scale_y,
            pipe_lip_width * scale_x, pipe_lip_height * scale_y
        )
        pygame.draw.rect(screen, DARK_YELLOW, top_lip_bottom)
        pygame.draw.rect(screen, DARK_YELLOW, top_lip_top)
        pygame.draw.rect(screen, DARK_YELLOW, bottom_lip_top)
        pygame.draw.rect(screen, DARK_YELLOW, bottom_lip_bottom)

# Vytvoření trubky
def create_pipe(screen_width, screen_height):
    min_pipe_height = 50
    max_top_pipe_height = height - pipe_gap - min_pipe_height

    if max_top_pipe_height <= min_pipe_height:
        top_height = min_pipe_height
    else:
        top_height = random.randint(min_pipe_height, max_top_pipe_height)

    bottom_y = top_height + pipe_gap
    bottom_height = height - bottom_y

    top = pygame.Rect(width, 0, pipe_width, top_height)
    bottom = pygame.Rect(width, bottom_y, pipe_width, bottom_height)
    return {'top': top, 'bottom': bottom, 'id': random.randint(100000, 999999)}

def reset_game():
    global players, player_velocities, scores, alive, pipes, last_pipe, scored_pipes, paused, background_offset

    players = [
        pygame.Rect(100, 400, 80, 60),
        pygame.Rect(200, 400, 80, 60),
        pygame.Rect(300, 400, 80, 60),
    ]
    player_velocities = [0, 0, 0]
    scores = [0, 0, 0]
    alive = [True, True, True]

    pipes = []
    last_pipe = pygame.time.get_ticks()
    scored_pipes = [set() for _ in range(3)]

    paused = False
    background_offset = 0

def prepare_game_start():
    global paused
    screen.fill(WHITE)
    screen_width, screen_height = pygame.display.get_surface().get_size()
    scale_x = screen_width / width
    scale_y = screen_height / height

    draw_background(background_offset, screen_width, screen_height)

    font = pygame.font.Font(None, int(36 * scale_y))
    controls = ['A', 'V', 'M']
    for i in range(3):
        if alive[i]:
            draw_window(players[i], player_images[i], scale_x, scale_y)
            control_text = font.render(f"Hop: {controls[i]}", True, BLACK)
            text_rect = control_text.get_rect(center=(players[i].centerx * scale_x, (players[i].bottom + 20) * scale_y))
            screen.blit(control_text, text_rect)

    draw_pipes(scale_x, scale_y)
    font_large = pygame.font.Font(None, int(74 * scale_y))
    instruction_text = font_large.render("Stiskněte ESC pro start hry", True, BLACK)
    text_rect = instruction_text.get_rect(center=(screen_width / 2, screen_height / 4))
    screen.blit(instruction_text, text_rect)

    pygame.display.flip()
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                root = tk.Tk()
                root.withdraw()
                odpoved = messagebox.askyesno("Ukončit", "Opravdu chcete hru ukončit?")
                root.destroy()
                if odpoved:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = False
        clock.tick(10)

def show_leaderboard():
    global running, background_offset
    screen_width, screen_height = pygame.display.get_surface().get_size()
    scale_x = screen_width / width
    scale_y = screen_height / height

    max_score = max(scores)
    winner_indexes = [i for i, score in enumerate(scores) if score == max_score]

    # Initialize player rectangles and velocities for winners, centered vertically
    winner_rects = [pygame.Rect(100 + idx * 100, height / 2 - 30, 80, 60) for idx in range(len(winner_indexes))]
    winner_velocities = [0] * len(winner_indexes)

    while True:
        screen.fill(WHITE)
        # Draw moving background
        background_offset -= pipe_speed
        bg_width = draw_background(background_offset, screen_width, screen_height)
        if background_offset <= -bg_width:
            background_offset += bg_width

        for idx, winner_idx in enumerate(winner_indexes):
            winner_velocities[idx] += gravity
            winner_rects[idx].y += winner_velocities[idx]
            if winner_rects[idx].y > height / 2 + 100:
                winner_velocities[idx] = -jump_strength
            if winner_rects[idx].bottom > height:
                winner_rects[idx].bottom = height
                winner_velocities[idx] = 0
            draw_window(winner_rects[idx], player_images[winner_idx], scale_x, scale_y)
        font = pygame.font.Font(None, int(74 * scale_y))
        if len(winner_indexes) == 1:
            text = font.render(f"Vítěz je Hráč {winner_indexes[0] + 1} s {max_score} body!", True, BLACK)
        else:
            winner_str = " a ".join([f"Hráč {i+1}" for i in winner_indexes])
            text = font.render(f"Remíza mezi {winner_str} s {max_score} body!", True, BLACK)
        text_rect = text.get_rect(topleft=(20, 20))
        screen.blit(text, text_rect)

        leaderboard = sorted([(i + 1, score) for i, score in enumerate(scores)], key=lambda x: x[1], reverse=True)
        font_small = pygame.font.Font(None, int(48 * scale_y))
        for i, (player_num, score) in enumerate(leaderboard):
            text = font_small.render(f"Hráč {player_num}: {score} bodů", True, BLACK)
            screen.blit(text, (20, 100 + i * 50))

        instruction_text = font_small.render("Stiskněte X pro ukončení, Z pro novou hru", True, BLACK)
        screen.blit(instruction_text, (20, screen_height - 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                root = tk.Tk()
                root.withdraw()
                odpoved = messagebox.askyesno("Ukončit", "Opravdu chcete hru ukončit?")
                root.destroy()
                if odpoved:
                    running = False
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    running = False
                    return
                elif event.key == pygame.K_z:
                    reset_game()
                    prepare_game_start()
                    return

        clock.tick(60)

# Pauza
def pause_menu():
    global paused, last_pipe, running
    paused = True
    pause_start = pygame.time.get_ticks()
    print("== HRA POZASTAVENA ==\n[Esc] Pokračovat\n")
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                root = tk.Tk()
                root.withdraw()
                odpoved = messagebox.askyesno("Ukončit", "Opravdu chcete hru ukončit?")
                root.destroy()
                if odpoved:
                    running = False
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = False
        clock.tick(10)
    pause_duration = pygame.time.get_ticks() - pause_start
    last_pipe += pause_duration

# Hlavní smyčka
running = True

try:
    screen_width, screen_height = pygame.display.get_surface().get_size()
    scale_x = screen_width / width
    scale_y = screen_height / height

    prepare_game_start()
    
    while running:
        screen_width, screen_height = pygame.display.get_surface().get_size()
        scale_x = screen_width / width
        scale_y = screen_height / height

        min_w, min_h = 400, 300
        if screen_width < min_w or screen_height < min_h:
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning("Malé okno", f"Okno je příliš malé!\nObnovuji původní velikost {width}x{height}.")
            root.destroy()
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            screen_width, screen_height = width, height

        scale_x = screen_width / width
        scale_y = screen_height / height

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                root = tk.Tk()
                root.withdraw()
                odpoved = messagebox.askyesno("Ukončit", "Opravdu chcete hru ukončit?")
                root.destroy()
                if odpoved:
                    running = False
                    pygame.quit()
                    sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_menu()

                elif event.key == pygame.K_RETURN and (pygame.key.get_mods() & pygame.KMOD_ALT):
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

                elif event.key == pygame.K_a and alive[0]:
                    player_velocities[0] = -jump_strength
                elif event.key == pygame.K_v and alive[1]:
                    player_velocities[1] = -jump_strength
                elif event.key == pygame.K_m and alive[2]:
                    player_velocities[2] = -jump_strength

        for i in range(3):
            if alive[i]:
                player_velocities[i] += gravity
                players[i].y += player_velocities[i]
                if players[i].top < 0:
                    players[i].top = 0
                    player_velocities[i] = 0
                if players[i].bottom > height:
                    alive[i] = False

        if pygame.time.get_ticks() - last_pipe > pipe_frequency:
            pipes.append(create_pipe(screen_width, screen_height))
            last_pipe = pygame.time.get_ticks()

        for pipe in pipes[:]:
            pipe['top'].x -= pipe_speed
            pipe['bottom'].x -= pipe_speed

            if pipe['top'].x + pipe_width < 0:
                pipes.remove(pipe)

            for i in range(3):
                if alive[i] and (players[i].colliderect(pipe['top']) or players[i].colliderect(pipe['bottom'])):
                    alive[i] = False

                if alive[i] and pipe['top'].x + pipe_width < players[i].x and pipe['id'] not in scored_pipes[i]:
                    scores[i] += 1
                    scored_pipes[i].add(pipe['id'])

        background_offset -= pipe_speed
        bg_width = draw_background(background_offset, screen_width, screen_height)
        if background_offset <= -bg_width:
            background_offset += bg_width

        screen.fill(WHITE)
        draw_background(background_offset, screen_width, screen_height)
        for i in range(3):
            if alive[i]:
                draw_window(players[i], player_images[i], scale_x, scale_y)

        draw_pipes(scale_x, scale_y)

        font = pygame.font.Font(None, int(36 * scale_y))
        for i, score in enumerate(scores):
            txt = font.render(f"Player {i+1}: {score}", True, BLACK)
            screen.blit(txt, (i * (screen_width // 3) + 20, 20))

        pygame.display.flip()
        clock.tick(60)

        if not any(alive):
            show_leaderboard()

except Exception as e:
    print(f"Nastala chyba: {e}")

finally:
    pygame.quit()
    sys.exit()