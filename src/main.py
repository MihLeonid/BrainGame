import argparse
import time
import math
import numpy as np
import pygame

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations


BOARD_ID = 10 # BoardIds.SYNTHETIC_BOARD # BRAINBIT_BOARD
CHANNEL = 1
FPS = 60
W = 1024  # ширина экрана
H = 768  # высота экрана
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 70, 225)


sc = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

x = W // 2
y_min = 65.0
y_max = H - 50
y = y_min
r = 50
speed = 0
running = True


alpha = 2000
t = 0


params = BrainFlowInputParams()
params.timeout = 15  # discovery timeout (seconds)

BoardShim.enable_dev_board_logger()

board = BoardShim(BOARD_ID, params)
board.prepare_session()
board.start_stream()



prevtime = time.time()
goingup = False
points = []
action = 0
while running:
    time.sleep(0.05)

    data = board.get_current_board_data(50)
    if len(data[CHANNEL]) == 0:
        time.sleep(0.1)
        continue

    points.append(2 ** min(11, math.floor(math.log2(max(map(abs, data[CHANNEL]))))))
    if len(points) > 50:
        points.pop(0)

    if len(points) > 5:
        i = 2
        while i < 4 and i < math.log2(max(points[-i:])) ** 2 / 15:
            i += 1
        action = max(points[-i:])
    if action < 256:
        action = 0
    action *= 0.4

    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            running = False
        elif i.type == pygame.KEYDOWN:
            if i.key == pygame.K_LEFT:
                x -= 3
            elif i.key == pygame.K_RIGHT:
                x += 3
            elif i.key == pygame.K_UP:
                goingup = True
        elif i.type == pygame.KEYUP:
            goingup = False
    speed = min(speed + action, 1000)
    y = min(y_max, max(y_min, y + (time.time() - prevtime) * speed))
    speed -= alpha * (time.time() - prevtime)
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
board.stop_stream()
board.release_session()
