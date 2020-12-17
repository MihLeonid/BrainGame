import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations
import time
import math

BOARD_ID = 10 # BoardIds.SYNTHETIC_BOARD # BRAINBIT_BOARD
CHANNEL = 1

params = BrainFlowInputParams()
params.timeout = 15  # discovery timeout (seconds)

BoardShim.enable_dev_board_logger()

board = BoardShim(BOARD_ID, params)
board.prepare_session()
board.start_stream()

def get_data_row():
    data = board.get_current_board_data(50)
    while len(data[CHANNEL]) == 0:
        time.sleep(0.1)
    # return 2 ** max(min(11, math.floor(math.log2(max(map(abs, data[CHANNEL]))))), 40);
    mi=min(data[CHANNEL])
    ma=max(data[CHANNEL])
    res=ma
    if(abs(mi)>abs(ma)):
        res=mi
    return res
def get_data_3():
    return (get_data_row()+get_data_row()+get_data_row())/3
def get_data_good():
    res=[]
    res.append(get_data_3())
    res.append(get_data_3())
    res.append(get_data_3())
    res.append(get_data_3())
    res.append(get_data_3())
    res.sort()
    return res[1]+res[3]+2*res[2]
def get_data():
    return get_data_good()
def stop():
    board.stop_stream()
    board.release_session()
