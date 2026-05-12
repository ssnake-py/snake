import pygame
import random
import sys
import os

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()

GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

block = 20

font = pygame.font.SysFont(None, 30)
big_font = pygame.font.SysFont(None, 60)

BEST_FILE = "best_score.txt"


# ---------------- BEST ----------------
def load_best():
    if os.path.exists(BEST_FILE):
        with open(BEST_FILE, "r") as f:
            return int(f.read() or 0)
    return 0


def save_best(score):
    with open(BEST_FILE, "w") as f:
        f.write(str(score))


def text(msg, color, x, y, f=font):
    screen.blit(f.render(msg, True, color), (x, y))


# ---------------- AI ----------------
def safe(nx, ny, snake):
    return 0 <= nx < WIDTH and 0 <= ny < HEIGHT and [nx, ny] not in snake


def ai_move(x, y, fx, fy, snake, dx, dy):
    moves = [(block,0),(-block,0),(0,block),(0,-block)]

    best = None
    best_dist = 999999

    for mx, my in moves:
        nx = x + mx
        ny = y + my

        if not safe(nx, ny, snake):
            continue

        dist = abs(nx - fx) + abs(ny - fy)

        if dist < best_dist:
            best_dist = dist
            best = (mx, my)

    if best is None:
        return dx, dy

    return best


# ---------------- APPLES ----------------
def spawn_apples(current):
    new = []

    # ALWAYS 1–2 apples (never 0)
    amount = random.randint(1, 2)

    for _ in range(amount):
        if len(current) + len(new) < 5:
            new.append([
                random.randrange(0, WIDTH, block),
                random.randrange(0, HEIGHT, block)
            ])

    return new


# ---------------- START SCREEN ----------------
def start_screen():

    code = ""
    typing = False

    while True:
        screen.fill(BLACK)

        text("SNAKE GAME", GREEN, 270, 120, big_font)
        text("All time best saved", WHITE, 260, 200)

        text("ENTER = start game", WHITE, 270, 300)
        text("SPACE = secret input", WHITE, 270, 340)

        pygame.draw.rect(screen, WHITE, (250, 400, 300, 50), 2)

        shown = "*" * len(code) if typing else ""
        text(shown, RED, 260, 415)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN and not typing:
                    return False

                if event.key == pygame.K_SPACE:
                    typing = True
                    code = ""

                if typing:
                    if event.key == pygame.K_BACKSPACE:
                        code = code[:-1]

                    elif event.key == pygame.K_RETURN:
                        return code == "2012"

                    else:
                        if event.unicode.isdigit():
                            code += event.unicode


# ---------------- GAME ----------------
def game(ai_mode, best_score):

    x = WIDTH // 2
    y = HEIGHT // 2

    dx = block
    dy = 0

    snake = [[x, y]]
    length = 5

    apples = [
        [random.randrange(0, WIDTH, block),
         random.randrange(0, HEIGHT, block)]
    ]

    score = 0

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not ai_mode:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and dx == 0:
                        dx, dy = -block, 0
                    elif event.key == pygame.K_RIGHT and dx == 0:
                        dx, dy = block, 0
                    elif event.key == pygame.K_UP and dy == 0:
                        dx, dy = 0, -block
                    elif event.key == pygame.K_DOWN and dy == 0:
                        dx, dy = 0, block

        # AI
        if ai_mode:
            target = min(apples, key=lambda a: abs(a[0]-x)+abs(a[1]-y))
            dx, dy = ai_move(x, y, target[0], target[1], snake, dx, dy)

        x += dx
        y += dy

        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            break

        screen.fill(BLACK)

        snake.append([x, y])
        if len(snake) > length:
            del snake[0]

        # draw snake
        for s in snake:
            pygame.draw.rect(screen, GREEN, (s[0], s[1], block, block))

        # draw apples
        for a in apples:
            pygame.draw.rect(screen, RED, (a[0], a[1], block, block))

        # eat logic
        new_apples = []
        eaten = False

        for ax, ay in apples:
            if x == ax and y == ay:
                length += 1
                score += 1
                eaten = True
            else:
                new_apples.append([ax, ay])

        # FIXED SPAWN RULE
        if eaten or len(apples) == 0:
            if len(new_apples) < 5:
                new_apples += spawn_apples(new_apples)

        apples = new_apples[:5]

        text(f"Score: {score}", WHITE, 10, 10)

        pygame.display.update()
        clock.tick(10)

    if not ai_mode and score > best_score:
        save_best(score)

    while True:
        screen.fill(BLACK)
        text("YOU LOST", RED, 320, 200, big_font)
        text("ENTER = Restart | Q = Quit", WHITE, 220, 280)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_RETURN:
                    run()


# ---------------- RUN ----------------
def run():
    best = load_best()
    ai = start_screen()
    game(ai, best)


run()
