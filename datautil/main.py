import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations

import json
import asyncio
import random
import struct
import time
import threading
import websockets


BOARD_ID = BoardIds.BRAINBIT_BOARD.value
EEG_CHANNELS = BoardShim.get_eeg_channels(BOARD_ID)


session_id = "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(10))
print("Session ID:", session_id)

markers = []
markers_filename = "data/" + session_id + ".json"
data_filename = "data/" + session_id + ".raw"

data_f = open(data_filename, "wb")

alive_sockets = []

all_data = []

loop = None
def ws_server():
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    async def handler(websocket, path):
        alive_sockets.append(websocket)
        while True:
            data = json.loads(await websocket.recv())
            if data["action"] == "addMarker":
                markers.append({"start": data["start"], "end": data["end"], "key": data["key"]})
                with open(markers_filename, "w") as f:
                    f.write(json.dumps(markers))


    start_server = websockets.serve(handler, "localhost", 8765)
    loop.run_until_complete(start_server)
    loop.run_forever()

threading.Thread(target=ws_server, daemon=True).start()

params = BrainFlowInputParams()
params.timeout = 15  # discovery timeout (seconds)

BoardShim.enable_dev_board_logger()

board = BoardShim(BOARD_ID, params)
board.prepare_session()
board.start_stream()

data_index = 0
while True:
    data = board.get_board_data()
    if any(len(data[chan]) == 0 for chan in EEG_CHANNELS):
        time.sleep(0.1)
        continue

    to_send = []
    for item in zip(*[data[chan] for chan in EEG_CHANNELS]):
        cur_data = item[:4]
        data_f.write(struct.pack("<dddd", *cur_data))
        to_send.append({"action": "push", "idx": data_index, "data": cur_data})
        data_index += 1

    for websocket in alive_sockets:
        asyncio.run_coroutine_threadsafe(websocket.send(json.dumps(to_send)), loop)

board.stop_stream()
board.release_session()
