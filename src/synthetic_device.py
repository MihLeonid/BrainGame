import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations
import random
import time
import sys
import math

BOARD_ID=BoardIds.SYNTHETIC_BOARD.value
CHANNEL = 1

params = BrainFlowInputParams()
params.timeout = 15  # discovery timeout (seconds)

BoardShim.enable_dev_board_logger()

if len(sys.argv) == 1:
    session_id = "synthetic-" + "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(10))
    print("Session ID:", session_id)
    data_filename = "data/" + session_id + ".csv"
    board = BoardShim(BOARD_ID, params)
    board.prepare_session()
    board.start_stream(streamer_params="file://" + data_filename + ":w")
else:
    params.other_info = str(BOARD_ID)
    session_id = sys.argv[1].replace(".csv", "").replace(".json", "").replace("data/", "")
    params.file = "data/" + session_id + ".csv"
    board = BoardShim(BoardIds.PLAYBACK_FILE_BOARD.value, params)
    board.prepare_session()
    board.start_stream()

def get_some_data():
    return board.get_current_board_data(15)
def get_data_row():
    data = get_some_data()
    while len(data[CHANNEL]) == 0:
        time.sleep(0.1)
        data = get_some_data()
    # return 2 ** max(min(11, math.floor(math.log2(max(map(abs, data[CHANNEL]))))), 40);
    mi=min(data[CHANNEL])
    ma=max(data[CHANNEL])
    res=ma
    if(abs(mi)>abs(ma)):
        res=mi
    return res**7/7.5**7
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
    return (res[1]+res[3]+2*res[2])/100
def get_data():
    dt=abs(get_data_good());
    if(dt<2):
        dt/=10;
    if(dt>10):
        dt=(dt-10)/4+10;
    elif(dt>7):
        dt=(dt-7)/2+7;
    dt=(dt-3)/2+3
    return dt;
def stop():
    board.stop_stream()
    board.release_session()
