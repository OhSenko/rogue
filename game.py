import tkinter as tk
from PIL import Image, ImageTk
import random
import math

# Constants
TILE_SIZE = 20
PLAYER_START_X = 300
PLAYER_START_Y = 200
PLAYER_SPEED = 2
ENEMY_SPEED = 1.5
BULLET_SPEED = 5
BULLET_SIZE = 17
TRAIL_LENGTH = 5
ENEMY_SIZE = 20
ENEMY_SPAWN_INTERVAL = 2000
ENEMY_HEALTH = 5


root = tk.Tk()
root.title("Examen Applicatieontwikkeling Jesse")
root.state('zoomed')

# canvas setup
canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight(), bg="black")
canvas.pack()

# load and resize player image
original_image = Image.open("player.png")
player_image = ImageTk.PhotoImage(original_image.resize((50, 50), Image.LANCZOS))

# player character
player = canvas.create_image(PLAYER_START_X, PLAYER_START_Y, image=player_image, anchor=tk.NW)

# key binds
move_directions = {'w': (0, -1), 'a': (-1, 0), 's': (0, 1), 'd': (1, 0)}
shoot_directions = {'Up': (0, -1), 'Down': (0, 1), 'Left': (-1, 0), 'Right': (1, 0)}

# movement variables
dx = dy = 0
keys_pressed = set()

# bllet class
class Bullet:
    def __init__(self, x, y, dx, dy):
        self.shape = canvas.create_oval(x, y, x + BULLET_SIZE, y + BULLET_SIZE, fill="white")
        self.dx = dx
        self.dy = dy
        self.trail = []

    def update(self):
        x1, y1, x2, y2 = canvas.coords(self.shape)
        if not (0 <= x1 < root.winfo_screenwidth() and 0 <= y1 < root.winfo_screenheight()):
            canvas.delete(self.shape)
            for trail_item in self.trail:
                canvas.delete(trail_item)
            return False
        for obstacle in obstacles:
            if is_collision(x1, y1, x2, y2, *obstacle):
                canvas.delete(self.shape)
                for trail_item in self.trail:
                    canvas.delete(trail_item)
                return False
        for enemy in enemies:
            if is_collision(x1, y1, x2, y2, *canvas.bbox(enemy.shape)):
                enemy.hit()
                canvas.delete(self.shape)
                for trail_item in self.trail:
                    canvas.delete(trail_item)
                return False
        self.trail.append(canvas.create_oval(x1, y1, x2, y2, fill="white"))
        if len(self.trail) > TRAIL_LENGTH:
            canvas.delete(self.trail.pop(0))
        canvas.move(self.shape, self.dx, self.dy)
        return True

bullets = []

# enemy class
class Enemy:
    def __init__(self, x, y):
        self.shape = canvas.create_rectangle(x, y, x + ENEMY_SIZE, y + ENEMY_SIZE, fill="red")
        self.health = ENEMY_HEALTH

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            canvas.delete(self.shape)
            enemies.remove(self)

    def move_towards_player(self, player_coords):
        px, py = (player_coords[0] + player_coords[2]) / 2, (player_coords[1] + player_coords[3]) / 2
        ex, ey = (canvas.coords(self.shape)[0] + canvas.coords(self.shape)[2]) / 2, (canvas.coords(self.shape)[1] + canvas.coords(self.shape)[3]) / 2
        angle = math.atan2(py - ey, px - ex)
        dx, dy = ENEMY_SPEED * math.cos(angle), ENEMY_SPEED * math.sin(angle)
        canvas.move(self.shape, dx, dy)

enemies = []

# obstacles
obstacles = [
    (100, 100, 200, 200),
    (400, 150, 500, 250),
    (600, 300, 700, 400),
    (150, 300, 250, 400),
    (300, 400, 400, 500)
]

# reate obstacles
for obstacle in obstacles:
    canvas.create_rectangle(obstacle, fill="gray")

# collision detection
def is_collision(x1, y1, x2, y2, ox1, oy1, ox2, oy2):
    return not (x2 < ox1 or x1 > ox2 or y2 < oy1 or y1 > oy2)

# game loop
def update():
    global dx, dy
    new_dx = sum(move_directions.get(key, (0, 0))[0] for key in keys_pressed) * PLAYER_SPEED
    new_dy = sum(move_directions.get(key, (0, 0))[1] for key in keys_pressed) * PLAYER_SPEED
    player_coords = canvas.bbox(player)
    
    # check for player collisions with obstacles
    next_player_coords = (player_coords[0] + new_dx, player_coords[1] + new_dy,
                          player_coords[2] + new_dx, player_coords[3] + new_dy)
    if not any(is_collision(*next_player_coords, *obstacle) for obstacle in obstacles):
        dx, dy = new_dx, new_dy
    else:
        dx = dy = 0

    canvas.move(player, dx, dy)
    x1, y1, x2, y2 = canvas.bbox(player)
    
    # wrap around the screen
    if x1 < 0:
        canvas.move(player, root.winfo_screenwidth(), 0)
    elif x2 > root.winfo_screenwidth():
        canvas.move(player, -root.winfo_screenwidth(), 0)
    elif y1 < 0:
        canvas.move(player, 0, root.winfo_screenheight())
    elif y2 > root.winfo_screenheight():
        canvas.move(player, 0, -root.winfo_screenheight())
    
    for bullet in bullets:
        if not bullet.update():
            bullets.remove(bullet)
    
    for enemy in enemies:
        enemy.move_towards_player(player_coords)
        ex1, ey1, ex2, ey2 = canvas.bbox(enemy.shape)
        if is_collision(x1, y1, x2, y2, ex1, ey1, ex2, ey2):
            canvas.create_text(root.winfo_screenwidth() // 2, root.winfo_screenheight() // 2,
                               text="Game Over", fill="white", font=("Helvetica", 50))
            root.update()
            return
    
    root.after(10, update)  # update every 10 milliseconds

# event handlers
def key_press(event):
    key = event.keysym
    if key in move_directions:
        keys_pressed.add(key)

def key_release(event):
    key = event.keysym
    if key in move_directions:
        keys_pressed.discard(key)
    elif key in shoot_directions:
        shoot(*shoot_directions[key])

def shoot(dx, dy):
    x1, y1, x2, y2 = canvas.bbox(player)
    x = (x1 + x2) / 2
    y = (y1 + y2) / 2
    bullets.append(Bullet(x, y, dx * BULLET_SPEED, dy * BULLET_SPEED))

def spawn_enemy():
    x = random.randint(0, root.winfo_screenwidth() - ENEMY_SIZE)
    y = random.randint(0, root.winfo_screenheight() - ENEMY_SIZE)
    enemies.append(Enemy(x, y))
    root.after(ENEMY_SPAWN_INTERVAL, spawn_enemy)

# bind keys
root.bind("<KeyPress>", key_press)
root.bind("<KeyRelease>", key_release)

# start game loop
update()

# start enemy spawn loop
spawn_enemy()

# tart Tkinter event loop
root.mainloop()
