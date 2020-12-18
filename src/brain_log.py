import argparse
import time
import math
import numpy as np
import brain_device as device

running = True

#out = open("stay.txt", "w")

while True:
    time.sleep(0.2)
    #out.write(str(device.get_data())+ '\n')
    data=device.get_data()
    if(len(data)>0):
        print(data)

device.stop();
