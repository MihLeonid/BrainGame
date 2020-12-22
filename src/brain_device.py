import analysis.theta as analysis
#IMPORTING THIS FILE IMPORT RIGHT ANALYSIS as analysis !!!
import pygame
import mne
import random
import threading
import time
import numpy as np
import brainflow
import sys
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, WindowFunctions, DetrendOperations


# CONSTANTS
BOARD_ID=BoardIds.BRAINBIT_BOARD.value

#OFFSET = 0.2
OFFSET = 0

WAVES = {
    ##"gamma": ("γ", ("T3", "T4"), 500, (30 - OFFSET, 60 - OFFSET)),
    #"theta": ("θ", ("T3", "T4", "O1", "O2"), 100, (4 - OFFSET, 8 - OFFSET)),
    "theta_": ("θ_", ("T3", "T4", "O1", "O2"), 100, (3 - OFFSET, 7 - OFFSET)),
    #"delta": ("δ", ("T3", "T4", "O1", "O2"), 100, (1 - OFFSET, 2 - OFFSET)),
    #"delta_theta": ("δθ", ("T3", "T4", "O1", "O2"), 100, (3 - OFFSET, 5 - OFFSET)),
    "delta_theta_": ("δθ_", ("T3", "T4", "O1", "O2"), 100, (2.4 - OFFSET, 4.2 - OFFSET)),
    #"theta_alpha": ("θα", ("T3", "T4", "O1", "O2"), 100, (5.2 - OFFSET, 11.2 - OFFSET)),
    "beta1": ("β1", ("T3", "T4", "O1", "O2"), 100, (14 - OFFSET, 25 - OFFSET)),
    "beta2": ("β2", ("T3", "T4"), 100, (25 - OFFSET, 40 - OFFSET)),
    #"alpha": ("α", ("O1", "O2"), 100, (8 - OFFSET, 13 - OFFSET)),
    #"alpha_beta": ("αβ", ("T3", "T4", "O1", "O2"), 100, (12.5 - OFFSET, 20 - OFFSET)),
    "alpha": ("α", ("O1", "O2"), 100, (7 - OFFSET, 13 - OFFSET)),
    "kappa": ("κ", ("T3", "T4", "O1", "O2"), 100, (8 - OFFSET, 13 - OFFSET)),
    "lambda": ("λ", ("O1", "O2"), 100, (12 - OFFSET, 14 - OFFSET)),
    "lambda_": ("λ_", ("T3", "T4", "O1", "O2"), 100, (3.8 - OFFSET, 4.8 - OFFSET))
}
eeg_channels = BoardShim.get_eeg_channels(BOARD_ID)
sampling_rate = BoardShim.get_sampling_rate(BOARD_ID)
ZONE_ORDER = BoardShim.get_eeg_names(BOARD_ID)
BUGGY_BRAINFLOW = 1
NFFT = 256
RNFFT = NFFT + BUGGY_BRAINFLOW
MAX_DATA = RNFFT
MAX_POWER = 9

#INFORMATION GATHERING
board = None
history_data = None
hist_band_power = {wave: [] for wave in WAVES.keys()}
ready = False
def information_gathering():
    global history_data
    global hist_band_power
    global ready
    global board

    params = BrainFlowInputParams()
    params.timeout = 15
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

    while True:
        data = board.get_board_data()
        eeg_data = np.array([data[chan,:] for chan in eeg_channels])
        if len(eeg_data[0]):
            if history_data is None:
                history_data = eeg_data
            else:
                history_data = np.hstack((history_data, eeg_data))
            history_data_tmp = []
            for row in history_data:
                history_data_tmp.append(row[-MAX_DATA:])
            history_data = np.array(history_data_tmp)
            if history_data is not None and len(history_data[0]) >= RNFFT:
                psds = []
                for row in history_data:
                    row = row[-RNFFT:].copy()
                    DataFilter.detrend(row, DetrendOperations.LINEAR.value)
                    psds.append(DataFilter.get_psd_welch(row, NFFT, NFFT // 2, sampling_rate, WindowFunctions.BLACKMAN_HARRIS.value))
                for i, (wave, (symbol, zones, limit, (l, r))) in enumerate(WAVES.items()):
                    band_power = dict()
                    for zone in zones:
                        if zone in ZONE_ORDER:
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
    global board
    board.stop_stream()
    board.release_session()

SPHERE = 0.1
def log():
    global ready
    global hist_band_power
    if ready:
        for i, (wave, (symbol, zones, limit, (l, r))) in enumerate(WAVES.items()):
            band_power = hist_band_power[wave][-1]
            print(wave, band_power)
        print()
def animation():
    global hist_band_power
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    import matplotlib.gridspec as gridspec

    info = mne.create_info(ch_names=ZONE_ORDER, sfreq=sampling_rate, ch_types=["eeg"] * len(ZONE_ORDER))
    info.set_montage(mne.channels.make_standard_montage("standard_1020"))

    fig = plt.figure()
    outer = gridspec.GridSpec(nrows=1, ncols=1 + len(WAVES), wspace=0.2, hspace=0.2)

    inner_axs = []
    for i in range(1 + len(WAVES)):
        inner_axs.append([])
        cnt = 2 if i > 0 else 1
        inner = gridspec.GridSpecFromSubplotSpec(cnt, 1, subplot_spec=outer[i], wspace=0.1, hspace=0.1)
        for j in range(cnt):
            ax = plt.Subplot(fig, inner[j])
            fig.add_subplot(ax)
            if i > 0 and j == 0:
                ax.set_title(list(WAVES.values())[i - 1][0], fontsize=40)
            inner_axs[i].append(ax)
            ax.plot()

    def animate(frame):
        global ready
        if ready:
            for i, row in enumerate(inner_axs):
                for j, ax in enumerate(row):
                    ax.cla()
                    if i > 0 and j == 0:
                        ax.set_title(list(WAVES.values())[i - 1][0], fontsize=40)
            mne.viz.plot_topomap(np.array([sum([hist_band_power[i][-1][zone] if zone in hist_band_power[i][-1] else 0 for i in WAVES.keys()]) for zone in ZONE_ORDER]), pos=info, contours=0, axes=inner_axs[0][0], show=False, sphere=SPHERE)
            for i, (wave, (symbol, zones, limit, (l, r))) in enumerate(WAVES.items()):
                band_power = hist_band_power[wave][-1]
                mne.viz.plot_topomap(np.array([band_power[zone] if zone in zones else 0 for zone in ZONE_ORDER]), pos=info, vmin=0, vmax=limit, contours=0, axes=inner_axs[1 + i][0], show=False, sphere=SPHERE)
                inner_axs[1 + i][1].set_ylim(0, max(limit, max([max(elem.values()) if len(elem) else 0 for elem in hist_band_power[wave]])))
                inner_axs[1 + i][1].plot([sum(elem.values())/len(elem.values()) if len(elem.values()) else 0 for elem in hist_band_power[wave]])
            log()

            """
            sig_fft[np.abs(sample_freq) > sample_freq[10]] = 0
            sig_fft[0] = 0
            y_values = fftpack.ifft(sig_fft)[4:-4]
            x_values = list(range(len(y_values)))
            plt.ylim(..., ...)
            plt.plot(x_values, y_values)
            """

            plt.pause(0.01)


    ani = FuncAnimation(plt.gcf(), animate, 100)
    plt.show()
def prepare():
    while get_data() is None:
        time.sleep(0.1)
if __name__ == "__main__":
    start()
    animation()
    stop()
