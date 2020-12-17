import argparse
import time
import math
import numpy as np
import pygame
import device

running = True

while running:
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            running = False
    print(get_data());

pygame.quit()
