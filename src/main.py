import argparse
import time
import math
import numpy as np
import matplotlib.pyplot as plt

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations


BOARD_ID = 10 # BoardIds.SYNTHETIC_BOARD # BRAINBIT_BOARD
CHANNEL = 1


fig, ax = plt.subplots(1, 1)
plt.ion()
plt.show()

background = fig.canvas.copy_from_bbox(ax.bbox)


params = BrainFlowInputParams()
params.timeout = 15  # discovery timeout (seconds)

BoardShim.enable_dev_board_logger()

board = BoardShim(BOARD_ID, params)
board.prepare_session()
board.start_stream()

points = []
act_points = []

action = 0

while True:
    time.sleep(0.05)

    ax.clear()
    ax.set_xlim(0, 50)

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
        action = max(points[-i:]) / 1024
    if action < 256:
        action = 0
    act_points.append(action * 1500)
    if len(act_points) > 50:
        act_points.pop(0)

    ax.set_ylim(0, 2000)
    ax.plot(points)
    ax.plot(act_points)
    plt.draw()
    plt.pause(0.01)

board.stop_stream()
board.release_session()
