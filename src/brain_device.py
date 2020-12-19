import time
import numpy as np
import random
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, WindowFunctions, DetrendOperations

BOARD_ID=BoardIds.BRAINBIT_BOARD.value
#BOARD_ID=BoardIds.SYNTHETIC_BOARD.value

params = BrainFlowInputParams ()
params.timeout = 15
BoardShim.enable_dev_board_logger ()


session_id = "brain-" + "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(10))
print("Session ID:", session_id)
data_filename = "data/" + session_id + ".csv"

board = BoardShim (BOARD_ID, params)
board.prepare_session()
board.start_stream(streamer_params="file://" + data_filename + ":w")

last_data=0
prev_last_data=0
last_data_time=time.time()
prev_last_data_time=time.time()

def get_some_data():
    return board.get_board_data()

history_data=None

def get_good_data():
    global history_data
    sampling_rate = BoardShim.get_sampling_rate(BOARD_ID)
    nfft = DataFilter.get_nearest_power_of_two (sampling_rate)
    eeg_channels = BoardShim.get_eeg_channels (BOARD_ID)

    if history_data is None:
        history_data = get_some_data()

    history_data = np.hstack((history_data, get_some_data()))
    if len(history_data[0]) <= nfft:
        return None

    result=[]
    new_data[]
    for a in range(4):
        eeg_channel = eeg_channels[a]
        DataFilter.detrend (history_data[eeg_channel], DetrendOperations.LINEAR.value)
        psd = DataFilter.get_psd_welch (history_data[eeg_channel], nfft, nfft // 2, sampling_rate, WindowFunctions.BLACKMAN_HARRIS.value)
        band_power_alpha = DataFilter.get_band_power (psd, 7.0, 13.0)
        band_power_theta_alpha = DataFilter.get_band_power (psd, 5.0, 11.0)
        band_power_theta = DataFilter.get_band_power (psd, 3.0, 7.0)
        #band_power_beta = DataFilter.get_band_power (psd, 14.0, 30.0)
        result.append(band_power_theta)
        new_data.append([band_power_theta, band_power_theta_alpha, band_power_alpha]
    print(new_data)
    history_data=None
    return result
def get_data():
    global last_data
    global prev_last_data
    global last_data_time
    global prev_last_data_time
    data=get_good_data()
    if(data is None):
        if(last_data_time==prev_last_data_time):
            return 0
        return last_data+((last_data-prev_last_data)/(last_data_time-prev_last_data_time))*(time.time()-last_data_time)
    else:
        data=sum(data)/100
        print(data);
        prev_last_data=last_data
        prev_last_data_time=last_data_time
        last_data=data
        last_data_time=time.time()
        return data
def stop():
    board.stop_stream()
    board.release_session()
