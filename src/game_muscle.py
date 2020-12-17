import argparse
import time
import math
import numpy as np
import pygame
import random
from pygame.locals import *

#import device

# constants
FPS = 60
H = 720
W = 405
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 70, 225)
RED = (157, 78, 0)

sc = pygame.display.set_mode((W, H))

hurt_cnt = 0

r = 16
y_min = r
y_max = H - r

G = 800
max_speed = 1300

x_speed = 160
block_width = 64
spawn_period = 2.5


pygame.font.init()
my_font = pygame.font.SysFont("Comic Sans MS", 50, italic=True)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("Sprites/Bird.png")
        self.surf = pygame.Surface((2 * r, 2 * r))
        self.rect = self.surf.get_rect(center = (W // 2, H // 2))
        self.speed = 0
        self.x = W // 2
        self.y = H // 2
    
    def add_speed(self, addition):
        self.speed += addition
        if self.speed < -max_speed:
            self.speed = -max_speed
        if self.speed > max_speed:
            self.speed = max_speed
    
    def move(self, delta_y):
        delta_y = max(y_min - self.y, min(y_max - self.y, delta_y))
        self.rect.move_ip(0, -delta_y)
        self.y += delta_y
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Barrier(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Sprites/Barrier.png")
        self.surf = pygame.Surface((block_width, H))
        if random.randint(0, 1) == 0:
            self.rect = self.surf.get_rect(center = (3 * W // 2, H + random.randint(-H // 4, H // 4)))
        else:
            self.rect = self.surf.get_rect(center = (3 * W // 2, random.randint(-H // 4, H // 4)))
        self.x = 3 * W // 2
        self.y = H // 2
    
    def move(self, delta_x):
        self.rect.move_ip(delta_x, 0)
        self.x += delta_x
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)


player = Player()
barriers = []
running = True

prevtime = time.time()
start_time = prevtime
last_spawn = start_time
hurt_offset = 2
last_hurt = start_time - hurt_offset

while running:
    time.sleep(1 / FPS)
    
    cur_time = time.time()
    delta_time = cur_time - prevtime
    if cur_time >= last_spawn + spawn_period:
        last_spawn = cur_time
        barriers.append(Barrier())
    
    #value = device.get_data()
    #player.add_speed(0.334 * value * G * delta_time)
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            running = False
        elif i.type == pygame.KEYDOWN:
            if i.key == pygame.K_UP:
                player.add_speed(17 * G * delta_time)
    player.add_speed(-G * delta_time)
    player.move(player.speed * delta_time)
    sc.fill(WHITE)
    player.draw(sc)
    while len(barriers) > 0 and barriers[0].x <= -W:
        barriers.pop(0)
    for barrier in barriers:
        barrier.move(-x_speed * delta_time)
        barrier.draw(sc)
    if pygame.sprite.spritecollideany(player, barriers):
        if cur_time > last_hurt + hurt_offset:
            hurt_cnt += 1
            last_hurt = cur_time
            #if lives == 0:
            #    sc.fill(RED)
            #    running = False
    text_surface = my_font.render(str(hurt_cnt), False, RED)
    sc.blit(text_surface, (0, 0))
    pygame.display.update()
    prevtime = time.time()
    

pygame.quit()
device.stop()
