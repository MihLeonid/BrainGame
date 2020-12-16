import argparse
import time
import numpy as np
import matplotlib.pyplot as plt

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations


BOARD_ID = BoardIds.BRAINBIT_BOARD
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

    data = board.get_current_board_data(50)
    ax.clear()
    ax.set_xlim(0, 50)
    ax.set_ylim(-512, 512)
    for chan in EEG_CHANNELS:
        ax.plot(data[chan])
    plt.draw()
    plt.pause(0.01)

board.stop_stream()
board.release_session()
