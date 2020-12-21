import argparse
import time
import math
import numpy as np

import brain_device as device

device.start()

while True:
    time.sleep(0.2)
    device.get_data()

device.stop();
