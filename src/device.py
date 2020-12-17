import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations

BOARD_ID = 10 # BoardIds.SYNTHETIC_BOARD # BRAINBIT_BOARD
CHANNEL = 1

params = BrainFlowInputParams()
params.timeout = 15  # discovery timeout (seconds)

BoardShim.enable_dev_board_logger()

board = BoardShim(BOARD_ID, params)
board.prepare_session()
board.start_stream()

def get_data():
    data = board.get_current_board_data(50)
    while len(data[CHANNEL]) == 0:
        time.sleep(0.1)
    return 2 ** min(11, math.floor(math.log2(max(map(abs, data[CHANNEL])))));
