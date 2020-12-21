import time
import numpy as np
import random
import brainflow
import sys
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, WindowFunctions, DetrendOperations

BOARD_ID=BoardIds.BRAINBIT_BOARD.value

interpolation=True
def no_interpolation():
    global interpolation
    interpolation=False

params = BrainFlowInputParams()
params.timeout = 15  # discovery timeout (seconds)

BoardShim.enable_dev_board_logger()

if len(sys.argv) == 1:
    session_id = "brain-" + "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(10))
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
    new_data=[]
    tsum=0
    tsub=0
    osum=0
    osub=0
    delta_theta=[]
    theta_alpha=[]
    lambda_sum=0
    for a in range(4):
        eeg_channel = eeg_channels[a]
        DataFilter.detrend (history_data[eeg_channel], DetrendOperations.LINEAR.value)
        psd = DataFilter.get_psd_welch (history_data[eeg_channel], nfft, nfft // 2, sampling_rate, WindowFunctions.BLACKMAN_HARRIS.value)
        band_power_alpha = DataFilter.get_band_power (psd, 7.0, 13.0)
        band_power_alpha_beta = DataFilter.get_band_power (psd, 12.5, 20.0)
        band_power_theta_alpha = DataFilter.get_band_power (psd, 5.0, 11.0)
        band_power_theta = DataFilter.get_band_power (psd, 3.0, 7.0)
        band_power_kapa = DataFilter.get_band_power (psd, 8.0, 13.0)
        band_power_delta_theta = DataFilter.get_band_power (psd, 2.2, 4.0)
        band_power_beta = DataFilter.get_band_power (psd, 14.0, 30.0)
        band_power_lambda = DataFilter.get_band_power (psd, 3.8, 4.8)
        #print(band_power_lambda, end=" ")
        power=band_power_delta_theta
        if(a==0):
            tsum+=power
            tsub+=power
        if a==1:
            tsum+=power
            tsub-=power
        if a==2:
            osum+=power
            osub+=power
            lambda_sum+=band_power_lambda
        if a==3:
            osum+=power
            osub-=power
            lambda_sum+=band_power_lambda
        #result.append([power, band_power_theta, band_power_theta_alpha])
        delta_theta.append(band_power_delta_theta)
        theta_alpha.append(band_power_theta_alpha)
    new_data=[tsum, osum]
    #print(new_data, end=" ")
    #result=new_data
    #print(new_data)
    history_data=None
    return new_data
data_history = []
def ready_to_get_data():
    global interpolation
    global last_data
    global prev_last_data
    global last_data_time
    global prev_last_data_time
    global data_history
    data=get_good_data()
    if(data is None):
        return False
    else:
        data=sum(data)/2000
        print(data, end=' ')
        result=0
        if data>0.7:
            result = 1
        #if data>0.9:
        #    result=-1
        #if data>2.5:
        #    result=1
        data=result
        print(result)
        prev_last_data=last_data
        prev_last_data_time=last_data_time
        last_data=data
        last_data_time=time.time()
        data_history.append(data)
        return True
def get_data():
    global interpolation
    global last_data
    global prev_last_data
    global last_data_time
    global prev_last_data_time
    global data_history
    data=get_good_data()
    if(data is None):
        if interpolation:
            if(last_data_time==prev_last_data_time):
                data_history.aooend(0)
                return 0
            value = last_data+((last_data-prev_last_data)/(last_data_time-prev_last_data_time))*(time.time()-last_data_time)
            data_history.append(value)
            return value
        return 0
    else:
        data=sum(data)/2000
        print(data, end=' ')
        result=0
        if data>0.7:
            result = 1
        #if data>0.9:
        #    result=-1
        #if data>2.5:
        #    result=1
        data=result
        print(result)
        prev_last_data=last_data
        prev_last_data_time=last_data_time
        last_data=data
        last_data_time=time.time()
        data_history.append(data)
        return data
def stop():
    board.stop_stream()
    board.release_session()
def get_window(cnt):
    global data_history
    return data_history[-cnt:]