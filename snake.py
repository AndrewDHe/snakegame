import pygame
import random
import sys

# --- 1. Initialize Pygame ---
pygame.init()

# --- 2. Game Window and Grid Settings ---
WIDTH, HEIGHT = 600, 400  # Game area width and height
INFO_BAR_HEIGHT = 50      # Height of the bottom info bar
SCREEN_WIDTH, SCREEN_HEIGHT = WIDTH, HEIGHT + INFO_BAR_HEIGHT # Total window size
GRID_SIZE = 20            # Side length of each game block (pixels)

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Snake (Improved)") # Window title

# --- 3. Color Definitions (using RGB values, more generic) ---
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
DARKGRAY = (100, 100, 100) # For walls
DARKRED = (139, 0, 0)     # For snake
LIGHTBLUE = (173, 216, 230) # For info bar text
FOOD_COLORS = [(46, 139, 87), (199, 21, 133), (25, 25, 112), (255, 215, 0)] # Food colors, keeping original logic

# --- 4. Game Variables and Initial State ---
SNAKE_INITIAL_LENGTH = 5
SNAKE_WIDTH = GRID_SIZE # Snake width matches grid size for alignment
SNAKE_HEIGHT = GRID_SIZE

FOOD_WIDTH = GRID_SIZE  # Food width matches grid size
FOOD_HEIGHT = GRID_SIZE # Food height matches grid size

snake_pos = [] # List of snake body segments, each element is an [x, y] coordinate (top-left)
for i in range(SNAKE_INITIAL_LENGTH):
    snake_pos.append([100 - i * GRID_SIZE, 50]) # Initial position moving right, head at [100, 50]

snake_direction = "RIGHT"  # Initial movement direction of the snake
change_to = snake_direction # Temporary variable to store the intended direction change

food_list = [] # List of food items, each element is [x, y, type]
WALL_LIST = [] # List of wall obstacles

score = 0
level = 1 # Game difficulty/speed level
INITIAL_SPEED = 10.0 # Initial speed (frames per second)

# Font settings
# Using None lets Pygame choose the default font (most reliable)
font_small = pygame.font.SysFont(None, 20)
font_medium = pygame.font.SysFont(None, 30) # For the info bar
font_large = pygame.font.SysFont(None, 50) # For game over text


clock = pygame.time.Clock() # Pygame Clock object

# --- 5. Drawing Functions ---

def draw_background():
    """Draws the game area background and the bottom info bar."""
    # Draw game area (white background)
    pygame.draw.rect(SCREEN, WHITE, (0, 0, WIDTH, HEIGHT))
    # Draw bottom info bar (black background)
    pygame.draw.rect(SCREEN, BLACK, (0, HEIGHT, SCREEN_WIDTH, INFO_BAR_HEIGHT))

def draw_wall():
    """Draws wall obstacles."""
    for xy in WALL_LIST:
        pygame.draw.rect(SCREEN, DARKGRAY, (xy[0], xy[1], GRID_SIZE, GRID_SIZE))

def draw_snake():
    """Draws the snake's head and body."""
    # Draw snake head (circle)
    head_center_x = snake_pos[0][0] + SNAKE_WIDTH // 2
    head_center_y = snake_pos[0][1] + SNAKE_HEIGHT // 2
    pygame.draw.circle(SCREEN, DARKRED, (head_center_x, head_center_y), SNAKE_WIDTH // 2)

    # Draw snake body (rectangle)
    for xy in snake_pos[1:]:
        pygame.draw.rect(SCREEN, DARKRED, (xy[0], xy[1], SNAKE_WIDTH, SNAKE_HEIGHT))

def draw_food():
    """Draws food items."""
    for xyz in food_list:
        food_color = FOOD_COLORS[xyz[2]-1]
        pygame.draw.rect(SCREEN, food_color, (xyz[0], xyz[1], FOOD_WIDTH, FOOD_HEIGHT))

def draw_context():
    """Displays score and snake length in the bottom info bar."""
    score_text = font_medium.render(f"Score: {score} | Length: {len(snake_pos)}", True, LIGHTBLUE)
    SCREEN.blit(score_text, (10, HEIGHT + 10)) # Draw text in the top-left of the info bar

def draw_pause():
    """Draws the pause screen."""
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180)) # Semi-transparent black overlay
    SCREEN.blit(s, (0, 0))
    pause_text = font_large.render('PAUSE', True, WHITE)
    text_rect = pause_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    SCREEN.blit(pause_text, text_rect)

def draw_dead():
    """Draws the game over screen."""
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 200)) # Semi-transparent black overlay
    SCREEN.blit(s, (0, 0))
    dead_text = font_large.render('GAME OVER!', True, RED)
    score_text = font_large.render(f"Final Score: {score}", True, WHITE)
    dead_rect = dead_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40))
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40))
    SCREEN.blit(dead_text, dead_rect)
    SCREEN.blit(score_text, score_rect)

# --- 6. Helper/Logic Functions ---

def get_random_grid_pos(area_width, area_height):
    """Generates a random grid-aligned coordinate."""
    x = random.randrange(0, area_width // GRID_SIZE) * GRID_SIZE
    y = random.randrange(0, area_height // GRID_SIZE) * GRID_SIZE
    return [x, y]

def add_food():
    """Adds food at a random position, ensuring it doesn't overlap with snake or walls."""
    while True:
        food_x, food_y = get_random_grid_pos(WIDTH, HEIGHT) # Use WIDTH, HEIGHT for game area
        food_type = random.choice([1, 2, 3, 4]) # Food type

        # Check for overlap with snake body
        if [food_x, food_y] in snake_pos:
            continue
        # Check for overlap with walls
        if [food_x, food_y] in WALL_LIST:
            continue
        
        food_list.append([food_x, food_y, food_type])
        break # Exit loop once a suitable position is found

def check_collision(obj1_pos, obj2_pos, obj_width, obj_height):
    """
    Checks if two objects collide (based on top-left coordinates and width/height).
    obj1_pos, obj2_pos: [x, y] lists
    obj_width, obj_height: width and height
    """
    rect1 = pygame.Rect(obj1_pos[0], obj1_pos[1], obj_width, obj_height)
    rect2 = pygame.Rect(obj2_pos[0], obj2_pos[1], obj_width, obj_height)
    return rect1.colliderect(rect2) # Pygame's built-in rectangle collision detection


# --- 7. Game Main Loop ---
if __name__ == "__main__":
    running = True
    pause = False
    dead = False

    # Initially add food (ensuring food is present at game start)
    for _ in range(3): # Add 3 food items initially
        add_food()

    # Add initial walls (if desired)
    # Example walls (ensure they are aligned with GRID_SIZE)
    WALL_LIST.append([200, 100])
    WALL_LIST.append([200, 120])
    WALL_LIST.append([300, 200])
    WALL_LIST.append([320, 200])


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN: # Mouse click to pause/resume
                pause = not pause
            elif event.type == pygame.KEYDOWN: # Keyboard key press to change direction
                if not pause and not dead: # Only change direction if not paused and not dead
                    if event.key == pygame.K_UP and snake_direction != "DOWN":
                        change_to = "UP"
                    elif event.key == pygame.K_DOWN and snake_direction != "UP":
                        change_to = "DOWN"
                    elif event.key == pygame.K_LEFT and snake_direction != "RIGHT":
                        change_to = "LEFT"
                    elif event.key == pygame.K_RIGHT and snake_direction != "LEFT":
                        change_to = "RIGHT"

        # Game logic update (only execute if not paused and not dead)
        if not pause and not dead:
            # Update actual snake direction
            snake_direction = change_to

            # Calculate new snake head position
            head_x, head_y = snake_pos[0][0], snake_pos[0][1]
            if snake_direction == "UP":
                head_y -= GRID_SIZE
            elif snake_direction == "DOWN":
                head_y += GRID_SIZE
            elif snake_direction == "LEFT":
                head_x -= GRID_SIZE
            elif snake_direction == "RIGHT":
                head_x += GRID_SIZE

            new_head_pos = [head_x, head_y]
            snake_pos.insert(0, new_head_pos) # Insert new head segment

            # Check if food is eaten
            food_eaten = False
            for i, food_item in enumerate(food_list):
                if check_collision(new_head_pos, food_item, SNAKE_WIDTH, SNAKE_HEIGHT):
                    score += food_item[2] * 10 # Food type determines score
                    # Snake grows, no need to remove tail
                    # Increase snake speed based on food type (e.g., +0.25 per type)
                    INITIAL_SPEED += food_item[2] * 0.25
                    del food_list[i] # Remove eaten food
                    add_food() # Immediately add a new food item
                    food_eaten = True
                    break # Break after eating one food item

            if not food_eaten:
                snake_pos.pop() # If no food eaten, remove tail (keep snake length constant)

            # Check for game over conditions
            # 1. Colliding with walls (boundary conditions adjusted to prevent snake from visually going "into" walls)
            if (new_head_pos[0] < 0 or                           # Left boundary
                new_head_pos[0] >= WIDTH or                       # Right boundary (snake head top-left reaches boundary)
                new_head_pos[1] < 0 or                           # Top boundary
                new_head_pos[1] >= HEIGHT):                       # Bottom boundary (snake head top-left reaches boundary)
                dead = True
            # 2. Colliding with wall obstacles
            for wall_xy in WALL_LIST:
                if check_collision(new_head_pos, wall_xy, SNAKE_WIDTH, SNAKE_HEIGHT):
                    dead = True
                    break
            # 3. Colliding with its own body (check from the third segment to avoid self-collision immediately after moving)
            for body_part in snake_pos[2:]:
                if check_collision(new_head_pos, body_part, SNAKE_WIDTH, SNAKE_HEIGHT):
                    dead = True
                    break

        # --- Drawing Section ---
        draw_background() # Draw background
        draw_wall()       # Draw walls
        draw_food()       # Draw food
        draw_snake()      # Draw snake
        draw_context()    # Draw score and length

        # Draw pause/game over screens
        if pause and not dead:
            draw_pause()
        if dead:
            draw_dead()
            pygame.time.wait(2000) # Show game over screen for 2 seconds, then quit
            running = False # End main loop

        # Refresh screen display
        pygame.display.flip()

        # Control frame rate
        clock.tick(INITIAL_SPEED) # Use INITIAL_SPEED for frame rate control

    # --- 8. Game Exit ---
    pygame.quit()
    sys.exit()
