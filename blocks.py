import pygame
import sys
import random

# --- Game settings ---
GRID_WIDTH = 10
GRID_HEIGHT = 10
CELL_SIZE = 40
GRID_OFFSET_X = 20  # pixels from left
GRID_OFFSET_Y = 20  # pixels from top
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH + GRID_OFFSET_X * 2
SCREEN_HEIGHT = CELL_SIZE * (GRID_HEIGHT + 3)  # extra space for piece preview
FPS = 60
score = 0  # initialize score
cleared_lines = []
line_clear_timer = 0
LINE_CLEAR_DURATION = 8  # frames


# --- Colors ---
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (50, 50, 255)
BLACK = (0, 0, 0)
PURPLE = (152, 29, 151)

# --- Initialize Pygame ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Block Grid Puzzle")
clock = pygame.time.Clock()

# --- Create the game grid ---
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
PREVIEW_POS = (GRID_OFFSET_X, GRID_OFFSET_Y + GRID_HEIGHT * CELL_SIZE + 20)


# --- Define shapes (as coordinate offsets) ---
SHAPES = [
    # Lines horizontal
    [(0, 0), (1, 0)],
    [(0, 0), (1, 0), (2, 0)],
    [(0, 0), (1, 0), (2, 0), (3, 0)],
    [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],

    # Lines vertical
    [(0, 0), (0, 1)],
    [(0, 0), (0, 1), (0, 2)],
    [(0, 0), (0, 1), (0, 2), (0, 3)],
    [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],

    # Square
    [(0, 0), (1, 0), (0, 1), (1, 1)],

    # L shapes (four rotations)
    [(0, 0), (1, 0), (1, 1)],
    [(0, 0), (0, 1), (1, 1)],
    [(0, 1), (1, 1), (1, 0)],
    [(0, 0), (0, 1), (1, 0)],

    # T shapes
    [(1, 0), (0, 1), (1, 1), (2, 1)],
    [(0, 0), (0, 1), (0, 2), (1, 1)],

    #Big L shape
    [(0,0), (1,0), (0,1), (0,2)],

    #S/Z
    [(1,0), (2,0), (0,1), (1,1)],

    [(0,0), (1,0), (1,1), (2,1)],
    #T
    [(1,0), (0,1), (1,1), (1,2)],
    #+
    [(1,0), (0,1), (1,1), (2,1), (1,2)],
    #Corner
    [(0,0), (0,1), (1,1), (1,2)],
    #2x3
    [(0,0), (1,0), (0,1), (1,1), (0,2), (1,2)],
    #3x3
    [(0,0), (1,0), (2,0), (0,1), (1,1), (2,1), (0,2), (1,2), (2,2)],
    #3x2
    [(0,0), (1,0), (2,0), (0,1), (1,1), (2,1)],
]

# --- Functions ---
def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(
                GRID_OFFSET_X + x * CELL_SIZE,
                GRID_OFFSET_Y + y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            pygame.draw.rect(screen, GRAY, rect, 1)
            if grid[y][x]:
                # Use same 3D-style block
                pygame.draw.rect(screen, BLUE, rect.inflate(-4, -4))
                lighter = tuple(min(255, c + 60) for c in BLUE)
                darker = tuple(max(0, c - 60) for c in BLUE)
                pygame.draw.line(screen, lighter, rect.topleft, rect.topright, 2)
                pygame.draw.line(screen, lighter, rect.topleft, rect.bottomleft, 2)
                pygame.draw.line(screen, darker, rect.bottomleft, rect.bottomright, 2)
                pygame.draw.line(screen, darker, rect.topright, rect.bottomright, 2)


def draw_shape(shape, top_left, color=BLUE):
    for dx, dy in shape:
        x = top_left[0] + dx
        y = top_left[1] + dy
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            rect = pygame.Rect(
                GRID_OFFSET_X + x * CELL_SIZE,
                GRID_OFFSET_Y + y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            # Draw base block
            pygame.draw.rect(screen, color, rect.inflate(-4, -4))

            # Faux 3D bevel effect
            lighter = tuple(min(255, c + 60) for c in color)
            darker = tuple(max(0, c - 60) for c in color)

            # Top and left highlights
            pygame.draw.line(screen, lighter, rect.topleft, rect.topright, 2)
            pygame.draw.line(screen, lighter, rect.topleft, rect.bottomleft, 2)

            # Bottom and right shadows
            pygame.draw.line(screen, darker, rect.bottomleft, rect.bottomright, 2)
            pygame.draw.line(screen, darker, rect.topright, rect.bottomright, 2)


def can_place(shape, top_left):
    for dx, dy in shape:
        x = top_left[0] + dx
        y = top_left[1] + dy
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return False
        if grid[y][x]:
            return False
    return True

def place_shape(shape, top_left):
    for dx, dy in shape:
        x = top_left[0] + dx
        y = top_left[1] + dy
        grid[y][x] = 1



def clear_full_lines():
    full_rows = []
    full_cols = []

    # Check full rows
    for y in range(GRID_HEIGHT):
        if all(grid[y][x] == 1 for x in range(GRID_WIDTH)):
            full_rows.append(y)

    # Check full columns
    for x in range(GRID_WIDTH):
        if all(grid[y][x] == 1 for y in range(GRID_HEIGHT)):
            full_cols.append(x)

    # Store positions to highlight
    cleared_positions = []

    # Clear full rows
    for y in full_rows:
        for x in range(GRID_WIDTH):
            grid[y][x] = 0
            cleared_positions.append((x, y))

    # Clear full columns
    for x in full_cols:
        for y in range(GRID_HEIGHT):
            grid[y][x] = 0
            cleared_positions.append((x, y))

    return cleared_positions


def draw_score():
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (GRID_OFFSET_X, 450))


def can_place_anywhere(shape):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if can_place(shape, (x, y)):
                return True
    return False

def draw_game_over():
    font_big = pygame.font.SysFont(None, 72)
    font_small = pygame.font.SysFont(None, 36)

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0,0))

    text1 = font_big.render("Game Over!", True, WHITE)
    text2 = font_small.render("Click to Restart", True, WHITE)

    screen.blit(text1, ((SCREEN_WIDTH - text1.get_width()) // 2, SCREEN_HEIGHT // 3))
    screen.blit(text2, ((SCREEN_WIDTH - text2.get_width()) // 2, SCREEN_HEIGHT // 2))





# --- Initialize current and next shapes ---
current_shape = random.choice(SHAPES)

# --- Main Game Loop ---
game_over = False

running = True
while running:
    screen.fill(PURPLE)
    draw_grid()
    draw_score()

    # Draw flash effect for cleared lines
    if line_clear_timer > 0:
        for x, y in cleared_lines:
            rect = pygame.Rect(
                GRID_OFFSET_X + x * CELL_SIZE,
                GRID_OFFSET_Y + y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            pygame.draw.rect(screen, (255, 255, 255), rect.inflate(-4, -4))
        line_clear_timer -= 1

    if not game_over:
        # mouse grid pos
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = (mouse_x - GRID_OFFSET_X) // CELL_SIZE
        grid_y = (mouse_y - GRID_OFFSET_Y) // CELL_SIZE


        if not game_over:
            # Get mouse position in grid
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x = (mouse_x - GRID_OFFSET_X) // CELL_SIZE
            grid_y = (mouse_y - GRID_OFFSET_Y) // CELL_SIZE

            # Always draw shape under mouse, even if invalid
            if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                is_valid = can_place(current_shape, (grid_x, grid_y))
                color = BLACK if is_valid else (255, 0, 0)  # red if invalid
                draw_shape(current_shape, (grid_x, grid_y), color=color)

    else:
        draw_game_over()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_over:
                # Reset game
                grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
                score = 0
                current_shape = random.choice(SHAPES)
                next_shape = random.choice(SHAPES)
                game_over = False
            else:
                if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                    draw_shape(current_shape, (grid_x, grid_y), color=BLACK)
                    if can_place(current_shape, (grid_x, grid_y)):
                        place_shape(current_shape, (grid_x, grid_y))
                        cleared_positions = clear_full_lines()
                        if cleared_positions:
                            cleared_lines = cleared_positions
                            line_clear_timer = LINE_CLEAR_DURATION
                            score += len(cleared_positions) * 10

                        cleared_positions = clear_full_lines()
                        if cleared_positions:
                            cleared_lines = cleared_positions
                            line_clear_timer = LINE_CLEAR_DURATION
                            score += len(set(cleared_positions)) * 10

                        current_shape = random.choice(SHAPES)
                        if not can_place_anywhere(current_shape):
                            game_over = True


    pygame.display.flip()
    clock.tick(FPS)
