import pygame
import mne
import random
import threading
import numpy as np
import scipy
from scipy import fftpack
from scipy.signal import cheby1, freqz, sosfilt
import random
import time
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, WindowFunctions, DetrendOperations

OFFSET = 0.2

WAVES = {
    "gamma": ("γ", ("T3", "T4"), 500, (30 - OFFSET, 60 - OFFSET)),
    "theta": ("θ", ("T3", "T4", "O1", "O2"), 100, (4 - OFFSET, 8 - OFFSET)),
    "delta": ("δ", ("T3", "T4", "O1", "O2"), 100, (1 - OFFSET, 4 - OFFSET)),
    "delta_theta": ("δθ", ("T3", "T4", "O1", "O2"), 100, (3 - OFFSET, 5 - OFFSET)),
    "beta1": ("β1", ("T3", "T4", "O1", "O2"), 100, (14 - OFFSET, 25 - OFFSET)),
    "beta2": ("β2", ("T3", "T4"), 100, (25 - OFFSET, 40 - OFFSET)),
    "alpha": ("α", ("O1", "O2"), 100, (8 - OFFSET, 13 - OFFSET)),
    "kappa": ("κ", ("T3", "T4"), 100, (8 - OFFSET, 13 - OFFSET)),
    "lambda": ("λ", ("O1", "O2"), 100, (12 - OFFSET, 14 - OFFSET))
}

BOARD_ID = BoardIds.BRAINBIT_BOARD.value

SPHERE = 0.1

eeg_channels = BoardShim.get_eeg_channels(BOARD_ID)
sampling_rate = BoardShim.get_sampling_rate(BOARD_ID)
ZONE_ORDER = BoardShim.get_eeg_names(BOARD_ID)
# ZONE_ORDER[0] = "T3"
# ZONE_ORDER[1] = "T4"
# ZONE_ORDER[2] = "O1"
# ZONE_ORDER[3] = "O2"


history_data = None

def information_gathering():
    global history_data

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

threading.Thread(target=information_gathering, daemon=True).start()


"""
def ui():
    pygame.init()
    pygame.font.init()

    # screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen = pygame.display.set_mode((700, 700))

    STEP = 128
    FONT_SIZE = 96
    X_OFFSET = (pygame.display.Info().current_w - STEP * 4) // 2
    Y_OFFSET = (pygame.display.Info().current_h - STEP * 4) // 2

    font = pygame.font.SysFont("Arial", FONT_SIZE)

    keys = "ABCDEFGHIJKLMNOPQRSTUVWXY"

    def update_ui():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break

        screen.fill((0, 0, 0))

        for i in range(5):
            for j in range(5):
                text = font.render(keys[i * 5 + j], False, (0, 127, 255) if focus in (("row", i), ("col", j)) else (255, 255, 255))
                screen.blit(text, text.get_rect(center=(X_OFFSET + STEP * j, Y_OFFSET + STEP * i)))

        pygame.display.flip()


    while True:
        row_order = [0, 0, 0, 0, 0, 0, 4]
        random.shuffle(row_order)

        for i in row_order:
            focus = ("row", i)
            update_ui()
            time.sleep(0.03)
            focus = None
            update_ui()
            time.sleep(0.2)


    pygame.quit()

threading.Thread(target=ui, daemon=True).start()
"""


def animation():
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

    hist_band_power = {wave: [] for wave in WAVES.keys()}

    def animate(frame):
        if history_data is not None and len(history_data[0]) >= 513:
            for i, row in enumerate(inner_axs):
                for j, ax in enumerate(row):
                    ax.cla()
                    if i > 0 and j == 0:
                        ax.set_title(list(WAVES.values())[i - 1][0], fontsize=40)

            mne.viz.plot_topomap(np.array([history_data[i][-1] for i in range(len(ZONE_ORDER))]), pos=info, contours=0, axes=inner_axs[0][0], show=False, sphere=SPHERE)

            psds = []
            for row in history_data:
                row = row[-513:].copy()
                DataFilter.detrend(row, DetrendOperations.LINEAR.value)
                psds.append(DataFilter.get_psd_welch(row, 512, 256, sampling_rate, WindowFunctions.BLACKMAN_HARRIS.value))

            for i, (wave, (symbol, zones, limit, (l, r))) in enumerate(WAVES.items()):
                band_power = sum(DataFilter.get_band_power(psds[ZONE_ORDER.index(zone)], l, r) for zone in zones)
                hist_band_power[wave].append(band_power)
                hist_band_power[wave] = hist_band_power[wave][-10:]
                """
                mne.viz.plot_topomap(np.array([band_power if zone in zones else 0 for zone in ZONE_ORDER]), pos=info, vmin=0, vmax=limit, contours=0, axes=inner_axs[1 + i][0], show=False, sphere=SPHERE)
                inner_axs[1 + i][1].set_ylim(0, max(limit, max(hist_band_power[wave])))
                inner_axs[1 + i][1].plot(hist_band_power[wave])
                """
                print(wave, band_power)
            print()

            """
            sig_fft[np.abs(sample_freq) > sample_freq[10]] = 0
            sig_fft[0] = 0
            y_values = fftpack.ifft(sig_fft)[4:-4]
            x_values = list(range(len(y_values)))
            plt.ylim(..., ...)
            plt.plot(x_values, y_values)
            """

            plt.pause(0.01)


    ani = FuncAnimation(plt.gcf(), animate, 1000)
    plt.show()

animation()