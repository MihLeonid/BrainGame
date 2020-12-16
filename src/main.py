import argparse
import time
import math
import numpy as np
import matplotlib.pyplot as plt

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations


BOARD_ID = BoardIds.SYNTHETIC_BOARD # BRAINBIT_BOARD
EEG_CHANNELS = BoardShim.get_eeg_channels(BOARD_ID)


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

while True:
    time.sleep(0.05)

    ax.clear()
    ax.set_xlim(0, 50)

    data = board.get_current_board_data(50)

    limit = 0
    for chan in EEG_CHANNELS:
        limit = max(limit, 2 ** math.ceil(math.log2(max(map(abs, data[chan])))))

    ax.set_ylim(-limit, limit)
    for chan in EEG_CHANNELS:
        ax.plot(data[chan])
    plt.draw()
    plt.pause(0.01)

board.stop_stream()
board.release_session()
