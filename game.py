import tkinter as tk  # Importeer de tkinter module als tk
from PIL import Image, ImageTk  # Importeer Image en ImageTk vanuit PIL
import random  # Importeer de random module
import math  # Importeer de math module
import platform  # Importeer de platform module voor platformafhankelijke operaties

# Constanten voor het spel
TILE_SIZE = 20  # Grootte van de tegels
PLAYER_START_X = 960  # Startpositie van de speler op de x-as
PLAYER_START_Y = 540  # Startpositie van de speler op de y-as
PLAYER_SPEED = 3  # Snelheid van de speler
ENEMY_SPEED = 1.5  # Snelheid van de vijand
BULLET_SPEED = 5  # Snelheid van de kogel
BULLET_SIZE = 17  # Grootte van de kogel
TRAIL_LENGTH = 3  # Lengte van het spoor van de kogel
ENEMY_SIZE = 40  # Grootte van de vijand
ENEMY_SPAWN_INTERVAL = 2000  # Interval voor het spawnen van vijanden in milliseconden
ENEMY_HEALTH = 3  # Gezondheid van de vijand

# Maak een tkinter root venster
root = tk.Tk()
root.title("Examen Applicatieontwikkeling Jesse")  # Titel van het venster instellen

# Maximale grootte van het venster afhankelijk van het besturingssysteem
if platform.system() == 'Windows':
    root.state('zoomed')  # Maximaliseer het venster op Windows
elif platform.system() == 'Darwin':
    root.attributes('-fullscreen', True)  # Maak het venster fullscreen op macOS
    root.attributes('-zoomed', True)  # Zoom het venster op macOS
elif platform.system() == 'Linux':
    root.attributes('-fullscreen', True)  # Maak het venster fullscreen op Linux (bijv. Ubuntu)

# Canvas instellen voor het spel
canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight(), bg="black")
canvas.pack()

# Afbeelding van de speler laden en schalen
original_player_image = Image.open("player.png")
player_image = ImageTk.PhotoImage(original_player_image.resize((50, 50), Image.LANCZOS))
player = canvas.create_image(PLAYER_START_X, PLAYER_START_Y, image=player_image, anchor=tk.CENTER)

# Afbeelding van de vijand laden en schalen
original_enemy_image = Image.open("enemy.png")
enemy_image = ImageTk.PhotoImage(original_enemy_image.resize((ENEMY_SIZE, ENEMY_SIZE), Image.LANCZOS))

# Variabelen voor beweging
dx = dy = 0  # Snelheid van de speler op x- en y-as
keys_pressed = set()  # Set om ingedrukte toetsen bij te houden

# Definieer bewegingsrichtingen voor de speler
move_directions = {'w': (0, -1), 'a': (-1, 0), 's': (0, 1), 'd': (1, 0)}

# Definieer schietrichtingen voor de speler
shoot_directions = {'Up': (0, -1), 'Down': (0, 1), 'Left': (-1, 0), 'Right': (1, 0)}

# Klasse voor kogels
class Bullet:
    def __init__(self, x, y, dx, dy):
        self.shape = canvas.create_oval(x, y, x + BULLET_SIZE, y + BULLET_SIZE, fill="white")  # Kogel vorm (ovaal)
        self.dx = dx  # Snelheid van de kogel op x-as
        self.dy = dy  # Snelheid van de kogel op y-as
        self.trail = []  # Lijst voor het spoor van de kogel

    def update(self):
        x1, y1, x2, y2 = canvas.coords(self.shape)  # Coördinaten van de kogel
        if not (0 <= x1 < root.winfo_screenwidth() and 0 <= y1 < root.winfo_screenheight()):
            canvas.delete(self.shape)  # Verwijder kogel als hij buiten het scherm is
            for trail_item in self.trail:
                canvas.delete(trail_item)  # Verwijder ook het spoor van de kogel
            return False
        for obstacle in obstacles:
            if is_collision(x1, y1, x2, y2, *obstacle):
                canvas.delete(self.shape)  # Verwijder kogel bij botsing met obstakel
                for trail_item in self.trail:
                    canvas.delete(trail_item)  # Verwijder ook het spoor van de kogel
                return False
        for enemy in enemies:
            if is_collision(x1, y1, x2, y2, *canvas.bbox(enemy.shape)):
                enemy.hit()  # Raak vijand als kogel hem raakt
                canvas.delete(self.shape)  # Verwijder kogel bij botsing met vijand
                for trail_item in self.trail:
                    canvas.delete(trail_item)  # Verwijder ook het spoor van de kogel
                return False
        self.trail.append(canvas.create_oval(x1, y1, x2, y2, fill="white"))  # Maak een nieuw spoor voor de kogel
        if len(self.trail) > TRAIL_LENGTH:
            canvas.delete(self.trail.pop(0))  # Verwijder oudste spoor als er te veel zijn
        canvas.move(self.shape, self.dx, self.dy)  # Beweeg de kogel volgens zijn snelheid
        return True

bullets = []  # Lijst om kogels bij te houden

# Klasse voor vijanden
class Enemy:
    def __init__(self, x, y):
        self.shape = canvas.create_image(x, y, image=enemy_image, anchor=tk.CENTER)  # Vijand vorm (afbeelding)
        self.health = ENEMY_HEALTH  # Gezondheid van de vijand

    def hit(self):
        self.health -= 1  # Verminder gezondheid van de vijand bij een hit
        if self.health <= 0:
            canvas.delete(self.shape)  # Verwijder vijand als gezondheid nul is
            enemies.remove(self)  # Verwijder vijand uit de lijst

    def move_towards_player(self, player_coords):
        px, py = (player_coords[0] + player_coords[2]) / 2, (player_coords[1] + player_coords[3]) / 2  # Midden van de speler
        ex, ey = canvas.coords(self.shape)  # Coördinaten van de vijand
        angle = math.atan2(py - ey, px - ex)  # Bereken hoek naar de speler
        dx, dy = ENEMY_SPEED * math.cos(angle), ENEMY_SPEED * math.sin(angle)  # Bereken nieuwe snelheid
        canvas.move(self.shape, dx, dy)  # Beweeg de vijand

enemies = []  # Lijst om vijanden bij te houden

# Functie om obstakels te genereren
def generate_obstacles(num_obstacles, width, height):
    obstacles = []
    for _ in range(num_obstacles):
        x1 = random.randint(0, width - 200)
        y1 = random.randint(0, height - 200)
        x2 = x1 + random.randint(100, 200)
        y2 = y1 + random.randint(100, 200)
        obstacles.append((x1, y1, x2, y2))
    return obstacles

num_obstacles = 20  # aantal obstakels
width = 1920  # breedte van het speelveld
height = 1080  # hoogte van het speelveld
obstacles = generate_obstacles(num_obstacles, width, height)  # genereer obstakels

# Maak obstakels op het canvas
for obstacle in obstacles:
    canvas.create_rectangle(obstacle, fill="gray")  # maak een rechthoekig obstakel

# botsing detectie (heeft mijn auto niet)
def is_collision(x1, y1, x2, y2, ox1, oy1, ox2, oy2):
    return not (x2 < ox1 or x1 > ox2 or y2 < oy1 or y1 > oy2)  # controleer of er een botsing is (boem is ho)

# game loop
def update():
    global dx, dy  # globale variabelen dx en dy
    new_dx = sum(move_directions.get(key, (0, 0))[0] for key in keys_pressed) * PLAYER_SPEED  # snelheid op x as
    new_dy = sum(move_directions.get(key, (0, 0))[1] for key in keys_pressed) * PLAYER_SPEED  # snelheid op y as
    player_coords = canvas.bbox(player)  # grenzen van de speler

    next_player_coords = (player_coords[0] + new_dx, player_coords[1] + new_dy,
                          player_coords[2] + new_dx, player_coords[3] + new_dy)
    if not any(is_collision(*next_player_coords, *obstacle) for obstacle in obstacles):
        dx, dy = new_dx, new_dy  # beweeg de speler als er geen obstakel in aanraking is met hem
    else:
        dx = dy = 0  # stop de speler alsie een obstakel aanraakt

    canvas.move(player, dx, dy)  # beweeg speler
    x1, y1, x2, y2 = canvas.bbox(player)  # grenzen speler

    # warp de speler als ie buiten beeld gaat.
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
            bullets.remove(bullet)  # als je iemand raakt dan verdwijnt de kogel

    for enemy in enemies:
        enemy.move_towards_player(player_coords)  # beweeg vijand naar de speler
        ex, ey = canvas.coords(enemy.shape)  # coords van de vijanden
        if is_collision(x1, y1, x2, y2, ex - ENEMY_SIZE / 2, ey - ENEMY_SIZE / 2, ex + ENEMY_SIZE / 2, ey + ENEMY_SIZE / 2):
            canvas.create_text(root.winfo_screenwidth() // 2, root.winfo_screenheight() // 2,
                               text="Game Over", fill="white", font=("Helvetica", 50))  # en toen was je dood
            root.update()  # update het venster
            return

    root.after(10, update)  # hij update elke 10ms

# event handlers voor je keybinds
def key_press(event):
    global keys_pressed
    key = event.keysym
    if key in move_directions:
        keys_pressed.add(key)  # voeg de ingedrukte toets toe aan de lijst anders werkt ie niet

def key_release(event):
    global keys_pressed
    key = event.keysym
    if key in move_directions:
        keys_pressed.discard(key)  # laat een toets los en dit programma laat het los net zoals rose jack losliet bij titanic
    elif key in shoot_directions:
        shoot(*shoot_directions[key])  # schiet in derichting van welke knop je drukt (kijk keybinds voor meer info)

def shoot(dx, dy):
    x1, y1, x2, y2 = canvas.bbox(player)  # dit leest de coordinaten van de speler
    x = (x1 + x2) / 2 # dit zorgt er voor dat de kogel uit het midden van je poppetje
    y = (y1 + y2) / 2  # 
    bullets.append(Bullet(x, y, dx * BULLET_SPEED, dy * BULLET_SPEED))  # nieuwe kogel aan de lijst toevoegen

# spawn vijanden op random locaties
def spawn_enemy():
    x = random.randint(0, root.winfo_screenwidth() - ENEMY_SIZE)
    y = random.randint(0, root.winfo_screenheight() - ENEMY_SIZE)
    enemies.append(Enemy(x, y))  # nog meer vijadnen
    root.after(ENEMY_SPAWN_INTERVAL, spawn_enemy)  # intervals om nog meer vijanden te spawnen want er waren neit al genoeg lol

# laat het toetsenbord werken
root.bind("<KeyPress>", key_press)
root.bind("<KeyRelease>", key_release)

# start de game loop
update()

# start het spawnen van vijanden
spawn_enemy()

# start het tkinter event loop
root.mainloop()
