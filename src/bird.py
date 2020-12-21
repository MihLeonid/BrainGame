import argparse
import time
import math
import numpy as np
import pygame
import random
from pygame.locals import *

import brain_device as device

SEED = 1337
random.seed(SEED)

# constants
FPS = 60
H = 720
W = 720

MIN_DIFFICULTY = 10;
DIFFICULTY = 54;
DIFFICULTY_STEPS = 100;
spawn_period = 3

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 70, 225)
RED = (157, 78, 0)

sc = pygame.display.set_mode((W, H))

hurt_cnt = 0
up_down_cnt = 0

r = 16
y_min = r
y_max = H - r

G = 800
max_speed = 1300

x_speed = 160
block_width = 64


pygame.font.init()
my_font = pygame.font.SysFont("Comic Sans MS", 50, italic=True)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("../assets/Sprites/Bird.png")
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
        new_y = self.y + delta_y
        if new_y <= y_min:
            new_y = y_min
            if self.speed < 0:
                self.speed = -self.speed / 2
        if new_y >= y_max:
            new_y = y_max
            if self.speed > 0:
                self.speed = -self.speed / 2
        self.y = new_y
        self.rect = self.surf.get_rect(center = (W // 2, int(H - self.y)))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Barrier(pygame.sprite.Sprite):
    def __init__(self):
        global up_down_cnt
        super().__init__()
        self.image = pygame.image.load("../assets/Sprites/Barrier.png")
        self.surf = pygame.Surface((block_width, H))
        self.x = 3 * W // 2
        self.y = int((-H/2+(H/DIFFICULTY_STEPS)*random.randint(MIN_DIFFICULTY, DIFFICULTY)))
        if (up_down_cnt==2)or(up_down_cnt==-2 and random.randint(0, 1) == 0):
            self.y=H-self.y;
            if(up_down_cnt>0):
                up_down_cnt=0;
            up_down_cnt-=1
        else:
            if(up_down_cnt<0):
                up_down_cnt=0;
            up_down_cnt+=1;
        self.rect = self.surf.get_rect(center = (self.x, self.y))

    def move(self, delta_x):
        self.x += delta_x
        self.rect = self.surf.get_rect(center = (int(self.x), int(self.y)))

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

    value = device.get_data()
    #player.add_speed(0.334 * value * G * delta_time)
    player.move(value*delta_time*G/3)
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            running = False
        #elif i.type == pygame.KEYDOWN:
        #    if i.key == pygame.K_UP:
        #        player.add_speed(17 * G * delta_time)
    #player.add_speed(-G * delta_time)
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
