import argparse
import time
import math
import numpy as np
import pygame


import device

# constants
FPS = 60
H = 720
W = 405
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 70, 225)

sc = pygame.display.set_mode((W, H))

speed = 0
x = W // 2
y = H // 2
r = 16
y_min = r
y_max = H - r

G = 800
x_speed = 160
max_speed = 1300
block_width = 64



class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("Sprites/Barrier.png")
        self.surf = pygame.Surface((2 * r, 2 * r))
        self.rect = self.surf.get_rect(center = (x, y))
        
    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0,5)
         
        if self.rect.left > 0:
              if pressed_keys[K_LEFT]:
                  self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH:        
              if pressed_keys[K_RIGHT]:
                  self.rect.move_ip(5, 0)


class Barrier(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Sprites/Barrier.png")
    

running = True

prevtime = time.time()
while running:
    time.sleep(1 / FPS)
    
    delta_time = time.time() - prevtime
    
    
    value = device.get_data()
    # print(value)
    speed += 0.334 * value * G * delta_time
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            running = False
        #elif i.type == pygame.KEYDOWN:
        #    if i.key == pygame.K_UP:
        #        speed = 0.3 * max_speed
    y = min(y_max, max(y_min, y + delta_time * speed))
    speed -= G * delta_time
    if speed < -max_speed:
        speed = -max_speed
    if speed > max_speed:
        speed = max_speed
    if y == y_min and speed < 0:
        if speed < -50:
            speed = -speed / 2
        else:
            speed = 0
    if y == y_max:
        speed = min(speed, 0)
    sc.fill(WHITE)
    pygame.draw.circle(sc, BLUE, (x, H - y), r)
    pygame.display.update()
    prevtime = time.time()

pygame.quit()
device.stop()
