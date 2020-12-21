#BEFORE IMPORTING THIS FILE IMPORT SOME ANALYSIS as analysis !!!
import time
import numpy as np
import random
import brainflow
import sys
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, WindowFunctions, DetrendOperations


# CONSTANTS
BOARD_ID=BoardIds.SYNTETIC_BOARD.value

#OFFSET = 0.2
OFFSET = 0

WAVES = {
    #"gamma": ("γ", ("T3", "T4"), 500, (30 - OFFSET, 60 - OFFSET)),
    "theta": ("θ", ("T3", "T4", "O1", "O2"), 100, (4 - OFFSET, 8 - OFFSET)),
    "theta_": ("θ_", ("T3", "T4", "O1", "O2"), 100, (3 - OFFSET, 7 - OFFSET)),
    "delta": ("δ", ("T3", "T4", "O1", "O2"), 100, (1 - OFFSET, 4 - OFFSET)),
    "delta_theta": ("δθ", ("T3", "T4", "O1", "O2"), 100, (3 - OFFSET, 5 - OFFSET)),
    "delta_theta_": ("δθ_", ("T3", "T4", "O1", "O2"), 100, (2.4 - OFFSET, 4.2 - OFFSET)),
    "theta_alpha": ("θα", ("T3", "T4", "O1", "O2"), 100, (5 - OFFSET, 11 - OFFSET)),
    "beta1": ("β1", ("T3", "T4", "O1", "O2"), 100, (14 - OFFSET, 25 - OFFSET)),
    "beta2": ("β2", ("T3", "T4"), 100, (25 - OFFSET, 40 - OFFSET)),
    "alpha": ("α", ("O1", "O2"), 100, (8 - OFFSET, 13 - OFFSET)),
    "alpha_beta": ("αβ", ("T3", "T4", "O1", "O2"), 100, (12.5 - OFFSET, 20 - OFFSET)),
    #"alpha": ("α", ("O1", "O2"), 100, (7 - OFFSET, 13 - OFFSET)),
    "kappa": ("κ", ("T3", "T4", "O1", "O2"), 100, (8 - OFFSET, 13 - OFFSET)),
    "lambda": ("λ", ("O1", "O2"), 100, (12 - OFFSET, 14 - OFFSET))
    "lambda*": ("λ*", ("T3", "T4", "O1", "O2"), 100, (3.8 - OFFSET, 4.8 - OFFSET))
}
eeg_channels = BoardShim.get_eeg_channels(BOARD_ID)
sampling_rate = BoardShim.get_sampling_rate(BOARD_ID)
ZONE_ORDER = BoardShim.get_eeg_names(BOARD_ID)
BUGGY_BRAINFLOW = 1
NFFT = 512
RNFFT = NFFT + BUGGY_BRAINFLOW
MAX_DATA = RNFFT
MAX_POWER = 5

#PLAYBACK
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


#INFORMATION GATHERING
history_data=None
hist_band_power = {wave: [] for wave in WAVES.keys()}
ready = False
def information_gathering():
    global history_data
    global hist_band_power
    global ready

    params = BrainFlowInputParams()
    params.timeout = 15
    BoardShim.enable_dev_board_logger()

    board = BoardShim(BOARD_ID, params)
    board.prepare_session()
    board.start_stream()

    while True:
        data = board.get_board_data()
        eeg_data = np.array([data[chan,:] for chan in eeg_channels])
        if len(eeg_data[0]):
            if history_data is None:
                history_data = eeg_data
            else:
                history_data = np.hstack((history_data, eeg_data))
                history_data = np.array([history_data[chan, -MAX_DATA:] for chan in eeg_channels])
            if history_data is not None and len(history_data[0]) >= RNFFT:
                psds = []
                for row in history_data:
                    row = row[-RNFFT:].copy()
                    DataFilter.detrend(row, DetrendOperations.LINEAR.value)
                    psds.append(DataFilter.get_psd_welch(row, NFFT, NFFT // 2, sampling_rate, WindowFunctions.BLACKMAN_HARRIS.value))
                for i, (wave, (symbol, zones, limit, (l, r))) in enumerate(WAVES.items()):
                    band_power = dict()
                    for zone in zones:
                        band_power[zone] = DataFilter.get_band_power(psds[ZONE_ORDER.index(zone)], l, r)
                    hist_band_power[wave].append(band_power)
                    hist_band_power[wave] = hist_band_power[wave][-MAX_POWER:]
                    if len(hist_band_power[wave]) == MAX_POWER:
                        ready = True
        else:
            #TODO TRY
            time.sleep(0.1)

#ANALYSIS
result_history = []
def get_data():
    global result_history
    global hist_band_power
    global ready
    if ready:
        result = analysis.proccess(hist_band_power)
        result_history.append(result)
        return result
    return None
def get_window(cnt):
    global result_history
    return result_history[-cnt:]

#MANUPULATION
def start():
    threading.Thread(target=information_gathering, daemon=True).start()

def stop():
    board.stop_stream()
    board.release_session()

def graph():
    pass
if __name__ == "__main__":
    SPHERE = 0.1
