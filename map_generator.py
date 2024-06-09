import random

def generate_obstacles():
    obstacles = []
    for _ in range(5):  # Adjust the number of obstacles as needed
        x1 = random.randint(0, 700)
        y1 = random.randint(0, 500)
        x2 = x1 + 100
        y2 = y1 + 100
        obstacles.append((x1, y1, x2, y2))
    return obstacles
