"""
 Code will not run without adding paths, as long as the name matches the code will work
"""
import pygame
import random
from PIL import Image
import os
import sqlite3
import sys

base_dir = os.path.dirname(__file__)
asset_dir = os.path.join(base_dir, "assets")
score_dir = os.path.join(base_dir, "score")
database_path = os.path.join(score_dir, "game_score.db")
# Initialize Pygame
pygame.init()

# Initialize the mixer for music and sounds
pygame.mixer.init()

# Paths
BASE_DIR = os.path.dirname(__file__)
CAR_IMAGE_PATH = os.path.join(BASE_DIR, "assets", "car.png")
OBSTACLE_IMAGE_PATH = os.path.join(BASE_DIR, "assets", "obstacle.png")
ROAD_IMAGE_PATH = os.path.join(BASE_DIR, "assets", "road_background.png")
EXPLOSION_GIF_PATH = os.path.join(BASE_DIR, "assets", "explosion.gif")
BACKGROUND_MUSIC_PATH = os.path.join(BASE_DIR, "assets", "background_music.mp3")
EXPLOSION_SOUND_PATH = os.path.join(BASE_DIR, "assets", "explosion_sound.wav")

conn = sqlite3.connect(os.path.join(BASE_DIR, "score", 'game_scores.db'))
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        score INTEGER NOT NULL,
        date TEXT DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# Screen dimensions
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("END OF THE WORLD")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Load images
car_image = pygame.image.load(CAR_IMAGE_PATH)
CAR_WIDTH, CAR_HEIGHT = 50, 100
car_image = pygame.transform.scale(car_image, (CAR_WIDTH, CAR_HEIGHT))

obstacle_image = pygame.image.load(OBSTACLE_IMAGE_PATH)
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 50, 50
obstacle_image = pygame.transform.scale(obstacle_image, (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))

# Load scrolling road background image
road_image = pygame.image.load(ROAD_IMAGE_PATH)
road_image = pygame.transform.scale(road_image, (WIDTH, HEIGHT))

# Load explosion GIF frames
def load_gif_frames(gif_path):
    gif = Image.open(gif_path)
    frames = []
    try:
        while True:
            frame = pygame.image.fromstring(gif.tobytes(), gif.size, gif.mode)
            frames.append(frame)
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    return frames

explosion_frames = load_gif_frames(EXPLOSION_GIF_PATH)
EXPLOSION_DURATION = 30  # Duration of explosion animation in frames

# Load and play background music
pygame.mixer.music.load(BACKGROUND_MUSIC_PATH)
pygame.mixer.music.play(-1)  # -1 means loop indefinitely

# Load explosion sound effect
explosion_sound = pygame.mixer.Sound(EXPLOSION_SOUND_PATH)

# Shake effect properties
shake_intensity = 5
shake_duration = 10
shake_timer = 0

# Scrolling background properties
scroll_speed = 5
background_y = 0

# Car properties
car_x = WIDTH // 2 - CAR_WIDTH // 2
car_y = HEIGHT - CAR_HEIGHT - 10
car_speed = 6

# Obstacle properties
obstacle_speed = 2
obstacles = []

# Explosion properties
explosions = []
frame_count = 0
score_increment_interval = 20  # Increase score every 20 frames

# Game properties
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
score = 0
game_over = False

# Define game states
MAIN_MENU = 0
GAME = 1
OPTIONS = 2
GAME_OVER = 3
current_state = MAIN_MENU

def create_obstacle():
    x = random.randint(0, WIDTH - OBSTACLE_WIDTH)
    y = -OBSTACLE_HEIGHT
    return [x, y]

def draw_car(x, y):
    screen.blit(car_image, (x, y))

def draw_obstacle(obstacle):
    screen.blit(obstacle_image, (obstacle[0], obstacle[1]))

def draw_score(score):
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

def check_collision(car_x, car_y, obstacles):
    for obstacle in obstacles:
        if (car_x < obstacle[0] + OBSTACLE_WIDTH and
            car_x + CAR_WIDTH > obstacle[0] and
            car_y < obstacle[1] + OBSTACLE_HEIGHT and
            car_y + CAR_HEIGHT > obstacle[1]):
            return True
    return False

def draw_explosions():
    for explosion in explosions:
        frame = explosion['frame'] // (EXPLOSION_DURATION // len(explosion_frames))
        screen.blit(explosion_frames[frame], (explosion['x'], explosion['y']))
        explosion['frame'] += 1

    # Remove finished explosions
    explosions[:] = [explosion for explosion in explosions if explosion['frame'] < EXPLOSION_DURATION]

def apply_shake_effect():
    global shake_timer
    if shake_timer > 0:
        offset_x = random.randint(-shake_intensity, shake_intensity)
        offset_y = random.randint(-shake_intensity, shake_intensity)
        return (offset_x, offset_y)
    return (0, 0)

def save_score(score):
    cursor.execute("INSERT INTO Scores (score) VALUES (?)", (score,))
    conn.commit()

def get_high_scores(limit=5):
    cursor.execute("SELECT score, date FROM Scores ORDER BY score DESC LIMIT ?", (limit,))
    return cursor.fetchall()

def draw_high_scores():
    # Draw the title, centered at the top of the screen
    high_score_title = font.render("Leaderboard", True, WHITE)
    screen.blit(high_score_title, (WIDTH // 2 - high_score_title.get_width() // 2, HEIGHT // 2 - 120))

    # Column headers
    headers = ["Rank", "Score", "Date"]
    header_x_positions = [WIDTH // 2 - 150, WIDTH // 2, WIDTH // 2 + 150]
    
    # Draw the headers
    for i, header in enumerate(headers):
        header_text = font.render(header, True, WHITE)
        screen.blit(header_text, (header_x_positions[i] - header_text.get_width() // 2, HEIGHT // 2 - 80))

    # Get high scores from the database
    high_scores = get_high_scores()
    y_pos = HEIGHT // 2 - 40  # Start position below the headers

    # Render each high score in table format
    for rank, (score, date) in enumerate(high_scores, start=1):
        rank_text = font.render(str(rank), True, WHITE)
        score_text = font.render(str(score), True, WHITE)
        date_text = font.render(date, True, WHITE)

        # Display rank, score, and date in columns
        screen.blit(rank_text, (header_x_positions[0] - rank_text.get_width() // 2, y_pos))
        screen.blit(score_text, (header_x_positions[1] - score_text.get_width() // 2, y_pos))
        screen.blit(date_text, (header_x_positions[2] - date_text.get_width() // 2, y_pos))
        
        # Move down for the next row
        y_pos += rank_text.get_height() + 10

def draw_main_menu():
    screen.fill(BLACK)
    
    # Draw the main title at the top
    title_text = font.render("END OF THE WORLD", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 6 - title_text.get_height() // 2))
    
    # Draw the menu options on the left
    box_width, box_height = 200, 50
    left_margin = WIDTH // 4 - 100  # Move to the left side
    option_positions = [
        (left_margin, HEIGHT // 2 - 75),  # Adjusted position
        (left_margin, HEIGHT // 2 - 25),
        (left_margin, HEIGHT // 2 + 25),
    ]
    options_text = ["Start Game", "Options", "Exit"]

    for i, pos in enumerate(option_positions):
        pygame.draw.rect(screen, GRAY, (*pos, box_width, box_height), border_radius=10)
        option_text = font.render(options_text[i], True, WHITE)
        screen.blit(option_text, (pos[0] + (box_width - option_text.get_width()) // 2, pos[1] + (box_height - option_text.get_height()) // 2))

    # Draw leaderboard title and scores on the right
    high_score_title = font.render("Leaderboard", True, WHITE)
    right_margin = 3 * WIDTH // 4
    screen.blit(high_score_title, (right_margin - high_score_title.get_width() // 2, HEIGHT // 3 - 50))
    
    # Display high scores in a leaderboard format
    high_scores = get_high_scores()
    y_pos = HEIGHT // 3  # Start a bit lower than the leaderboard title
    line_height = 30

    for i, (score, date) in enumerate(high_scores):
        score_text = font.render(f"{i + 1}. {score} - {date}", True, WHITE)
        screen.blit(score_text, (right_margin - score_text.get_width() // 2, y_pos))
        y_pos += line_height

def draw_options_screen():
    screen.fill(BLACK)
    options_text = font.render("Options", True, WHITE)
    volume_text = font.render("Volume", True, WHITE)
    back_text = font.render("Back to Menu", True, WHITE)

    screen.blit(options_text, (WIDTH // 2 - options_text.get_width() // 2, HEIGHT // 3 - options_text.get_height() // 2))
    screen.blit(volume_text, (WIDTH // 2 - volume_text.get_width() // 2, HEIGHT // 2 - volume_text.get_height() // 2))
    screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT // 2 + volume_text.get_height()))

def draw_game_over_screen():
    screen.fill(BLACK)

    # Draw the game over title at the top
    game_over_text = font.render("GAME OVER", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 6 - game_over_text.get_height() // 2))

    # Draw the score on the screen
    score_text = font.render(f"Your Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 3))

    # Draw the "Retry" and "Menu" buttons inside boxes
    box_width, box_height = 200, 50
    left_margin = WIDTH // 2 - box_width // 2

    # Positions for the buttons (Retry and Menu)
    button_positions = [
        (left_margin, HEIGHT // 2 + 25),  # Retry button
        (left_margin, HEIGHT // 2 + 75),  # Menu button
    ]

    button_texts = ["Retry", "Menu"]

    for i, pos in enumerate(button_positions):
        pygame.draw.rect(screen, GRAY, (*pos, box_width, box_height), border_radius=10)
        button_text = font.render(button_texts[i], True, WHITE)
        screen.blit(button_text, (pos[0] + (box_width - button_text.get_width()) // 2, pos[1] + (box_height - button_text.get_height()) // 2))


def handle_main_menu_click(pos):
    global current_state
    # Updated left margin for button positions
    left_margin = WIDTH // 4 - 100  # Move to the left side
    box_width, box_height = 200, 50
    option_positions = [
        (left_margin, HEIGHT // 2 - 75),  # Adjusted position
        (left_margin, HEIGHT // 2 - 25),
        (left_margin, HEIGHT // 2 + 25),
    ]
    
    # Check if the click is within the bounds of the "Start Game" button
    if option_positions[0][0] < pos[0] < option_positions[0][0] + box_width and option_positions[0][1] < pos[1] < option_positions[0][1] + box_height:
        current_state = GAME
    # Check if the click is within the bounds of the "Options" button
    elif option_positions[1][0] < pos[0] < option_positions[1][0] + box_width and option_positions[1][1] < pos[1] < option_positions[1][1] + box_height:
        current_state = OPTIONS
    # Check if the click is within the bounds of the "Exit" button
    elif option_positions[2][0] < pos[0] < option_positions[2][0] + box_width and option_positions[2][1] < pos[1] < option_positions[2][1] + box_height:
        pygame.quit()
        sys.exit()

def handle_options_click(pos):
    global current_state
    # Check if the "Back to Menu" button is clicked
    if WIDTH // 2 - 75 < pos[0] < WIDTH // 2 + 75 and HEIGHT // 2 + 25 < pos[1] < HEIGHT // 2 + 75:
        current_state = MAIN_MENU

def handle_game_over_click(pos):
    global current_state, car_x, car_y, car_speed, obstacle_speed, obstacles, explosions, score, game_over
    # Check if the "Retry" button is clicked
    if WIDTH // 2 - 75 < pos[0] < WIDTH // 2 + 75 and HEIGHT // 2 + 25 < pos[1] < HEIGHT // 2 + 75:
        save_score(score)  # Save score to the database before resetting game variables
        # Reset game variables
        car_x = WIDTH // 2 - CAR_WIDTH // 2
        car_y = HEIGHT - CAR_HEIGHT - 10
        car_speed = 6
        obstacle_speed = 2
        obstacles = []
        explosions = []
        score = 0
        game_over = False
        current_state = GAME
    # Check if the "Menu" button is clicked
    elif WIDTH // 2 - 75 < pos[0] < WIDTH // 2 + 75 and HEIGHT // 2 + 75 < pos[1] < HEIGHT // 2 + 125:
        current_state = MAIN_MENU

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_score(score)
            conn.close()
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if current_state == MAIN_MENU:
                handle_main_menu_click(pos)
            elif current_state == OPTIONS:
                handle_options_click(pos)
            elif current_state == GAME_OVER:
                save_score(score)
                handle_game_over_click(pos)


    keys = pygame.key.get_pressed()

    if current_state == GAME:
        if keys[pygame.K_LEFT] and car_x > 0:
            car_x -= car_speed
        if keys[pygame.K_RIGHT] and car_x < WIDTH - CAR_WIDTH:
            car_x += car_speed

        if not game_over:
            if random.randint(1, 20) == 1:
                obstacles.append(create_obstacle())

            for obstacle in obstacles:
                obstacle[1] += obstacle_speed

            # Check if any obstacles reached the bottom of the screen
            for obstacle in obstacles:
                if obstacle[1] >= HEIGHT:
                    explosions.append({'x': obstacle[0], 'y': HEIGHT - OBSTACLE_HEIGHT, 'frame': 0})
                    explosion_sound.play()  # Play explosion sound
                    shake_timer = shake_duration  # Start shake effect

            obstacles = [obstacle for obstacle in obstacles if obstacle[1] < HEIGHT]

            if check_collision(car_x, car_y, obstacles):
                game_over = True

            frame_count += 1
            if frame_count % score_increment_interval == 0:
                score += 1

            if shake_timer > 0:
                shake_timer -= 1

        # Scroll background
        background_y += scroll_speed
        if background_y >= HEIGHT:
            background_y = 0

        # Drawing
        screen.fill(BLACK)

        # Draw scrolling road background
        screen.blit(road_image, (0, background_y))
        screen.blit(road_image, (0, background_y - HEIGHT))

        # Apply shake effect
        shake_offset = apply_shake_effect()

        # Draw car and obstacles
        draw_car(car_x + shake_offset[0], car_y + shake_offset[1])
        for obstacle in obstacles:
            draw_obstacle((obstacle[0] + shake_offset[0], obstacle[1] + shake_offset[1]))

        # Draw explosions
        draw_explosions()

        draw_score(score)

        if game_over:
            current_state = GAME_OVER

    elif current_state == MAIN_MENU:
        draw_main_menu()

    elif current_state == OPTIONS:
        draw_options_screen()

    elif current_state == GAME_OVER:
        draw_game_over_screen()

    pygame.display.flip()
    clock.tick(60)