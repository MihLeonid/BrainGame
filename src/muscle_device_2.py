import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations
import time
import math
import threading

BOARD_ID = 10
CHANNEL = 1

params = BrainFlowInputParams()
params.timeout = 15

BoardShim.enable_dev_board_logger()

board = BoardShim(BOARD_ID, params)
board.prepare_session()
board.start_stream()


history_data = []


def get_data_raw():
    data = board.get_current_board_data(5)
    while len(data[CHANNEL]) == 0:
        time.sleep(0.1)
    return data[CHANNEL]


def get_data():
    ans = [max([abs(x) for x in get_data_raw()]) for i in range(5)]
    res = sum(ans) / 5
    if res < 200:
        return res / 1000
    return res / 100


def stop():
    board.stop_stream()
    board.release_session()

"""
def side_thread():
    FPS = 30
    while True:
        time.sleep(1 / FPS)
        for x in get_data_raw():
            history_data.append(x)


threading.Thread(target=side_thread, daemon=True).start()

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

N = 500
K1 = 5
K2 = 10

def animate(i):
    y_values = history_data[-N:]
    x_values = list(range(len(y_values)))
    plt.cla()
    plt.ylim(-1500, 1500)
    plt.plot(x_values, y_values, color="blue")
    if len(history_data) > N + K1:
        y_values_2 = [max([abs(history_data[i - N - j]) for j in range(K1)]) for i in range(N)]
        plt.plot(x_values, y_values_2, color="red")
    #if len(history_data) > N + K2:
    #    y_values_2 = [sum([history_data[i - N - j] for j in range(K2)]) / K2 for i in range(N)]
    #    plt.plot(x_values, y_values_2, color="green")
        

ani = FuncAnimation(plt.gcf(), animate, 1000)
plt.tight_layout()
plt.show()
"""