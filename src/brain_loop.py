import argparse
import time
import math
import numpy as np

import analysis.three_state_eyes as analysis
import brain_device as device

running = True

while True:
    time.sleep(0.2)
    device.get_data()

device.stop();
