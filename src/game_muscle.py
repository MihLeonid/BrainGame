import argparse
import time
import math
import numpy as np
import pygame


import device

FPS = 60
H = 720  # высота экрана
W = 360  # ширина экрана
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 70, 225)


sc = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

x = W // 2
y_min = 30
y_max = H - 30
y = H // 2
r = 50
speed = 0
running = True


alpha = 2000
t = 0

prevtime = time.time()
goingup = False
while running:
    delta = time.time() - prevtime
    action = 0
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            running = False
        elif i.type == pygame.KEYDOWN:
            if i.key == pygame.K_UP:
                goingup = True
                action = 4000
        elif i.type == pygame.KEYUP:
            goingup = False
    speed = min(speed + action, 1000)
    y = min(y_max, max(y_min, y + delta * speed))
    speed -= alpha * delta
    if y == y_min and speed < 0:
        if speed < -50:
            speed = -speed / 2
        else:
            speed = 0
    if y == y_max:
        speed = min(speed, 0)
    sc.fill(WHITE)
    pygame.draw.circle(sc, BLUE, (x, H - y), r)
    pygame.draw.line(sc, BLACK, (0, H - 10), (W, H - 10), 10)
    pygame.display.update()
    prevtime = time.time()

pygame.quit()
