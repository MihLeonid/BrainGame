import time
import numpy as np
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, WindowFunctions, DetrendOperations

BOARD_ID=BoardIds.BRAINBIT_BOARD.value
#BOARD_ID=BoardIds.SYNTHETIC_BOARD.value

params = BrainFlowInputParams ()
params.timeout = 15
BoardShim.enable_dev_board_logger ()

brain_time=time.time()

board = BoardShim (BOARD_ID, params)
board.prepare_session()
board.start_stream()

last_data=0
prev_last_data=0
last_data_time=time.time()
prev_last_data_time=time.time()
def get_some_data():
    return board.get_board_data()
def get_data_raw():
    data=get_some_data()
    if(len(data)==0):
        return "none"
    return data

def get_good_data():
    global brain_time
    if(time.time()-brain_time<1):
        return "none"
    else:
        brain_time=time.time()
    data=get_data_raw()
    if(data=="none"):
        return "none"
    sampling_rate = BoardShim.get_sampling_rate(BOARD_ID)
    nfft = DataFilter.get_nearest_power_of_two (sampling_rate)
    eeg_channels = BoardShim.get_eeg_channels (BOARD_ID)
    result=[];
    for a in range(4):
        eeg_channel = eeg_channels[a]
        DataFilter.detrend (data[eeg_channel], DetrendOperations.LINEAR.value)
        psd = DataFilter.get_psd_welch (data[eeg_channel], nfft, nfft // 2, sampling_rate, WindowFunctions.BLACKMAN_HARRIS.value)
        band_power_alpha = DataFilter.get_band_power (psd, 7.0, 13.0)
        band_power_beta = DataFilter.get_band_power (psd, 14.0, 30.0)
        result.append([band_power_alpha, band_power_beta])
    return result
def get_data():
    #global last_data
    #global prev_last_data
    #global last_data_time
    #global prev_last_data_time
    #data=get_good_data()
    #if(data=="none"):
        #return last_data+((last_data-prev_last_data)/(last_data_time-prev_last_data_time))*(time.time()-last_data_time)
    #else:
        #data=data[1][0]/50
        #prev_last_data=last_data
        #prev_last_data_time=last_data_time
        #last_data=data
        #last_data_time=time.time()
        #return data
    if(data=="none"):
        return [];
    else:
        return data;
def stop():
    board.stop_stream()
    board.release_session()
