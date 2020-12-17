import argparse
import time
import math
import numpy as np
import device

running = True

out = open("stay.txt", "w")

while True:
    time.sleep(0.2)
    #out.write(str(device.get_data())+ '\n')
    print(device.get_data())

device.stop();