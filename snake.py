import pygame
import random
import sys

# --- Constants ---
WIDTH, HEIGHT = 600, 600
CELL = 20
COLS = WIDTH // CELL
ROWS = HEIGHT // CELL
FPS = 10

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GREEN  = (50,  200, 50)
DGREEN = (30,  140, 30)
RED    = (220, 50,  50)
GRAY   = (40,  40,  40)
YELLOW = (255, 215, 0)

UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)

# --- Game ---
def draw_cell(surface, color, gx, gy, inset=1):
    rect = pygame.Rect(gx * CELL + inset, gy * CELL + inset,
                       CELL - inset * 2, CELL - inset * 2)
    pygame.draw.rect(surface, color, rect, border_radius=4)

def random_food(snake):
    while True:
        pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if pos not in snake:
            return pos

def show_text_center(surface, font, text, color, y):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    surface.blit(surf, rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("贪吃蛇")
    clock = pygame.time.Clock()

    font_big   = pygame.font.SysFont("Arial", 48, bold=True)
    font_small = pygame.font.SysFont("Arial", 24)
    font_hud   = pygame.font.SysFont("Arial", 20)

    def new_game():
        snake = [(COLS // 2, ROWS // 2)]
        direction = RIGHT
        food = random_food(snake)
        score = 0
        return snake, direction, food, score

    snake, direction, food, score = new_game()
    game_over = False
    paused = False

    while True:
        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                if game_over:
                    if event.key == pygame.K_r:
                        snake, direction, food, score = new_game()
                        game_over = False
                    continue

                if event.key == pygame.K_p:
                    paused = not paused

                if not paused:
                    if event.key in (pygame.K_UP, pygame.K_w) and direction != DOWN:
                        direction = UP
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != UP:
                        direction = DOWN
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != RIGHT:
                        direction = LEFT
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != LEFT:
                        direction = RIGHT

        # --- Update ---
        if not game_over and not paused:
            head = snake[0]
            new_head = (head[0] + direction[0], head[1] + direction[1])

            # Wall collision
            if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
                game_over = True
            # Self collision
            elif new_head in snake:
                game_over = True
            else:
                snake.insert(0, new_head)
                if new_head == food:
                    score += 10
                    food = random_food(snake)
                else:
                    snake.pop()

        # --- Draw ---
        screen.fill(BLACK)

        # Grid
        for x in range(0, WIDTH, CELL):
            pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL):
            pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

        # Food (pulsing effect)
        ticks = pygame.time.get_ticks()
        pulse = abs((ticks % 800) - 400) / 400  # 0..1..0
        food_color = (
            int(220 + 35 * pulse),
            int(50),
            int(50),
        )
        draw_cell(screen, food_color, food[0], food[1], inset=2)
        # Shine dot
        pygame.draw.circle(screen, (255, 180, 180),
                           (food[0] * CELL + 6, food[1] * CELL + 6), 3)

        # Snake
        for i, (gx, gy) in enumerate(snake):
            color = DGREEN if i == 0 else GREEN
            draw_cell(screen, color, gx, gy)
            if i == 0:  # Eyes
                ex = gx * CELL + (14 if direction[0] >= 0 else 6)
                ey = gy * CELL + (6  if direction[1] >= 0 else 14)
                if direction in (LEFT, RIGHT):
                    eye_positions = [(ex, gy * CELL + 5), (ex, gy * CELL + 14)]
                else:
                    eye_positions = [(gx * CELL + 5, ey), (gx * CELL + 14, ey)]
                for ep in eye_positions:
                    pygame.draw.circle(screen, WHITE, ep, 3)
                    pygame.draw.circle(screen, BLACK, ep, 1)

        # HUD
        score_surf = font_hud.render(f"Score: {score}", True, YELLOW)
        screen.blit(score_surf, (8, 6))
        help_surf = font_hud.render("P: Pause   ESC: Quit", True, (120, 120, 120))
        screen.blit(help_surf, (WIDTH - help_surf.get_width() - 8, 6))

        # Overlays
        if paused and not game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            show_text_center(screen, font_big,   "PAUSED",       WHITE,  HEIGHT // 2 - 30)
            show_text_center(screen, font_small, "Press P to continue", GRAY, HEIGHT // 2 + 30)

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            show_text_center(screen, font_big,   "GAME OVER",           RED,   HEIGHT // 2 - 50)
            show_text_center(screen, font_small, f"Score: {score}",      YELLOW, HEIGHT // 2 + 10)
            show_text_center(screen, font_small, "Press R to restart",   WHITE,  HEIGHT // 2 + 50)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
