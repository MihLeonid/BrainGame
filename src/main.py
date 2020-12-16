import argparse
import time
import numpy as np
import matplotlib.pyplot as plt

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations


BOARD_ID = BoardIds.BRAINBIT_BOARD
EEG_CHANNELS = BoardShim.get_eeg_channels(BOARD_ID)


params = BrainFlowInputParams()
# params.serial_number = args.serial_number
params.timeout = 15  # discovery timeout (seconds)
# params.file = args.file

BoardShim.enable_dev_board_logger()
# BoardShim.disable_board_logger()

board = BoardShim(BOARD_ID, params)
board.prepare_session()



board.start_stream()
time.sleep(0.05)
data = board.get_board_data()

board.stop_stream()
board.release_session()


for chan in EEG_CHANNELS:
    plt.plot(data[chan])
plt.show()
