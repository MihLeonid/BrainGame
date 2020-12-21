import argparse
import time
import math
import numpy as np

import analysis.three_state_eyes as analysis
import brain_device as device

running = True

out = open("log.txt", "w")

while True:
    time.sleep(0.2)
    data=device.get_data()
    out.write(str(data)+ '\n')
    print(data)

device.stop();
