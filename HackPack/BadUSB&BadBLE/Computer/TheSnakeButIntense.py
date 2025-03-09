import tkinter as tk
import random
import json
from tkinter import simpledialog, colorchooser, messagebox
import webbrowser

ROWS = 25
COLS = 25
TILE_SIZE = 25

# Default game settings
SETTINGS = {
    "snake_color": "lime green",
    "controls": {"up": "w", "down": "s", "left": "a", "right": "d"},
    "theme": "dark"
}

# Game window
window = tk.Tk()
window.title("TheSnake")
window.attributes("-fullscreen", True)

# Canvas setup
canvas = tk.Canvas(window, bg="black", borderwidth=0, highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Game variables
snake = None
food = None
velocityX = 0
velocityY = 0
snake_body = []
game_over = False
score = 0
high_score = 0
game_speed = 100
timer_id = None

# Functions for settings
def save_settings():
    """Save settings to a JSON file."""
    settings_data = {
        "snake_color": SETTINGS["snake_color"],
        "controls": SETTINGS["controls"],
        "theme": SETTINGS["theme"],
        "high_score": high_score  # Save the high score
    }
    with open("settings.json", "w") as f:
        json.dump(settings_data, f)

def load_settings():
    """Load settings from a JSON file."""
    global SETTINGS, high_score
    try:
        with open("settings.json", "r") as f:
            settings_data = json.load(f)
            SETTINGS["snake_color"] = settings_data.get("snake_color", "lime green")
            SETTINGS["controls"] = settings_data.get("controls", {"up": "w", "down": "s", "left": "a", "right": "d"})
            SETTINGS["theme"] = settings_data.get("theme", "dark")
            high_score = settings_data.get("high_score", 0)  # Load high score
    except FileNotFoundError:
        pass  # If the settings file doesn't exist, do nothing

# Functions for theme application
def apply_theme():
    """Apply the chosen theme."""
    if SETTINGS["theme"] == "dark":
        canvas.config(bg="black")
    else:
        canvas.config(bg="white")

# Functions for game management
def reset_game():
    """Reset game state to initial values."""
    global snake, food, velocityX, velocityY, snake_body, game_over, score, timer_id
    if timer_id is not None:
        window.after_cancel(timer_id)
    snake = Tile(TILE_SIZE * 5, TILE_SIZE * 5)
    food = Tile(random.randint(0, COLS - 1) * TILE_SIZE, random.randint(0, ROWS - 1) * TILE_SIZE)
    velocityX = 0
    velocityY = 0
    snake_body.clear()
    game_over = False
    score = 0
    draw()

# Tile class
class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Functions for controlling movement
def change_direction(e):
    """Change the direction of the snake based on key presses."""
    global velocityX, velocityY
    controls = SETTINGS["controls"]
    if e.keysym == controls["up"] and velocityY != 1:
        velocityX = 0
        velocityY = -1
    elif e.keysym == controls["down"] and velocityY != -1:
        velocityX = 0
        velocityY = 1
    elif e.keysym == controls["left"] and velocityX != 1:
        velocityX = -1
        velocityY = 0
    elif e.keysym == controls["right"] and velocityX != -1:
        velocityX = 1
        velocityY = 0

def move():
    """Move the snake and check for collisions with walls, food, or itself."""
    global snake, food, snake_body, game_over, score, high_score
    if game_over:
        return

    # Check if the snake hits the boundaries of the canvas
    if snake.x < 0 or snake.x >= canvas.winfo_width() or snake.y < 0 or snake.y >= canvas.winfo_height():
        game_over = True
        return

    # Check if the snake hits its own body
    for tile in snake_body:
        if snake.x == tile.x and snake.y == tile.y:
            game_over = True
            return

    # Check if the snake eats the food
    if snake.x == food.x and snake.y == food.y:
        snake_body.append(Tile(food.x, food.y))
        food.x = random.randint(0, COLS - 1) * TILE_SIZE
        food.y = random.randint(0, ROWS - 1) * TILE_SIZE
        score += 1
        if score > high_score:
            high_score = score  # Update high score if the current score is higher

    # Move the snake body
    for i in range(len(snake_body) - 1, -1, -1):
        tile = snake_body[i]
        if i == 0:
            tile.x = snake.x
            tile.y = snake.y
        else:
            prev_tile = snake_body[i - 1]
            tile.x = prev_tile.x
            tile.y = prev_tile.y

    # Move the snake head
    snake.x += velocityX * TILE_SIZE
    snake.y += velocityY * TILE_SIZE

def draw():
    """Draw the game state (snake, food, score, etc.)."""
    global snake, food, snake_body, game_over, score, high_score, timer_id
    move()
    canvas.delete("all")

    # Draw food
    canvas.create_rectangle(food.x, food.y, food.x + TILE_SIZE, food.y + TILE_SIZE, fill='red')

    # Draw snake with eyes and tongue
    if velocityX == 1:  # Moving right
        eye1 = (snake.x + 5, snake.y + 5, snake.x + 10, snake.y + 10)
        eye2 = (snake.x + 15, snake.y + 5, snake.x + 20, snake.y + 10)
        tongue = (snake.x + TILE_SIZE, snake.y + TILE_SIZE // 2, snake.x + TILE_SIZE + 5, snake.y + TILE_SIZE // 2)
    elif velocityX == -1:  # Moving left
        eye1 = (snake.x + 15, snake.y + 5, snake.x + 20, snake.y + 10)
        eye2 = (snake.x + 5, snake.y + 5, snake.x + 10, snake.y + 10)
        tongue = (snake.x - 5, snake.y + TILE_SIZE // 2, snake.x, snake.y + TILE_SIZE // 2)
    elif velocityY == 1:  # Moving down
        eye1 = (snake.x + 5, snake.y + 15, snake.x + 10, snake.y + 20)
        eye2 = (snake.x + 15, snake.y + 15, snake.x + 20, snake.y + 20)
        tongue = (snake.x + TILE_SIZE // 2, snake.y + TILE_SIZE, snake.x + TILE_SIZE // 2, snake.y + TILE_SIZE + 5)
    else:  # Moving up
        eye1 = (snake.x + 5, snake.y + 5, snake.x + 10, snake.y + 10)
        eye2 = (snake.x + 15, snake.y + 5, snake.x + 20, snake.y + 10)
        tongue = (snake.x + TILE_SIZE // 2, snake.y - 5, snake.x + TILE_SIZE // 2, snake.y)

    # Draw snake
    canvas.create_rectangle(snake.x, snake.y, snake.x + TILE_SIZE, snake.y + TILE_SIZE, fill=SETTINGS["snake_color"])
    canvas.create_oval(*eye1, fill="white")  # Left eye
    canvas.create_oval(*eye2, fill="white")  # Right eye
    canvas.create_line(*tongue, fill="red")  # Tongue

    for tile in snake_body:
        canvas.create_rectangle(tile.x, tile.y, tile.x + TILE_SIZE, tile.y + TILE_SIZE, fill=SETTINGS["snake_color"])

    # Score and game-over text
    if game_over:
        canvas.create_text(canvas.winfo_width() / 2, canvas.winfo_height() / 2, font="Arial 20", text="Game Over", fill="red")
        canvas.create_text(canvas.winfo_width() / 2, canvas.winfo_height() / 2 + 30, font="Arial 12", text="Press 'R' to restart", fill="gray")
    else:
        canvas.create_text(canvas.winfo_width() - 120, 20, font="Arial 12", text=f"Score: {score}", fill="gray")
        canvas.create_text(canvas.winfo_width() - 120, 40, font="Arial 12", text=f"Highscore: {high_score}", fill="gray")

    # Schedule the next frame
    timer_id = window.after(game_speed, draw)

# Functions for settings
def open_settings():
    global SETTINGS
    def update_color():
        color = colorchooser.askcolor(title="Choose a color for the snake")[1]
        if color:
            SETTINGS["snake_color"] = color
            save_settings()

    def update_controls():
        new_up = simpledialog.askstring("Controls", f"Current up key: {SETTINGS['controls']['up']}")
        new_down = simpledialog.askstring("Controls", f"Current down key: {SETTINGS['controls']['down']}")
        new_left = simpledialog.askstring("Controls", f"Current left key: {SETTINGS['controls']['left']}")
        new_right = simpledialog.askstring("Controls", f"Current right key: {SETTINGS['controls']['right']}")
        if new_up and new_down and new_left and new_right:
            SETTINGS["controls"] = {
                "up": new_up,
                "down": new_down,
                "left": new_left,
                "right": new_right
            }
            save_settings()

    def toggle_theme():
        SETTINGS["theme"] = "light" if SETTINGS["theme"] == "dark" else "dark"
        save_settings()
        apply_theme()

    settings_window = tk.Toplevel(window)
    settings_window.title("Settings")
    settings_window.geometry("300x300")

    tk.Button(settings_window, text="Change Color", command=update_color).pack(pady=10)
    tk.Button(settings_window, text="Change Keys", command=update_controls).pack(pady=10)
    tk.Button(settings_window, text="Toggle Theme", command=toggle_theme).pack(pady=10)
    tk.Button(settings_window, text="Back", command=settings_window.destroy).pack(pady=10)

def open_support():
    messagebox.showinfo("Support", "We would greatly appreciate your support. If you'd like to make a contribution, please send Bitcoin to the following address: bc1qv7g893pqw327ahg53zfzzk9yfumdkxqt6y2n47. Thank you for your generosity!")

def open_discord():
    webbrowser.open("https://discord.gg/DVRSAm3hem")

# Load settings and start the game
load_settings()
reset_game()
apply_theme()

# Create Settings and Support buttons
settings_button = tk.Button(window, text="Settings", command=open_settings, bg="gray", fg="white")
settings_button.place(x=10, y=10)

support_button = tk.Button(window, text="Support Us", command=open_support, bg="gray", fg="white")
support_button.place(x=10, y=40)

discord_button = tk.Button(window, text="Discord", command=open_discord, bg="gray", fg="white")
discord_button.place(x=10, y=70)

# Bind events
window.bind("<Key>", change_direction)
window.bind("r", lambda _: reset_game())  # Restart game

window.mainloop()
