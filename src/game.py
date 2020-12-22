import time
import random
import threading
from pygame.locals import *

history_data = []


def side_thread():
    #for debugging False, for testing - True
    USE_DEVICE = True
    
    import pygame
    
    if USE_DEVICE:
        import muscle_device as device
    
    FPS = 40
    H = 720
    W = 1280
    
    SKY = (183, 236, 255)
    RED = (157, 0, 121)
    GOLD = (234, 206, 0)
    BLACK = (0, 0, 0)
    
    sc = pygame.display.set_mode((W, H))
    
    hurt_cnt = 0
    coin_cnt = 0
    
    r = 25
    y_min = r
    y_max = H - r
    
    G = 800
    max_speed = 1300
    
    x_speed = 200
    block_width = 128
    
    MUSCLE_COEFF = 0.334
    
    level_parts = [((192, 0), (192, 960), (448, -60), (448, 900), (704, -120), (704, 840), (960, -60), (960, 540)),
                   ((192, 60), (576, 660), (960, 60), (576, 180)),
                   ((192, 0), (448, 720), (832, 0), (960, 900), (704, 420)),
                   ((192, 720), (576, -120), (960, 0), (704, 300)),
                   ((192, 180), (448, 0), (960, 540), (960, 60)),
                   ((192, 0), (576, 0), (960, 120), (448, 360))]
    level_parts_cnt = 20
    
    pygame.font.init()
    my_font = pygame.font.SysFont("Comic Sans MS", 50, italic=True)
    
    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.images = [pygame.image.load("../assets/Sprites/Bird.png"), pygame.image.load("../assets/Sprites/Bird2.png")]
            self.image = self.images[0]
            self.image_id = 0
            self.surf = pygame.Surface((2 * r, 2 * r))
            self.rect = self.surf.get_rect(center = (W // 2, H // 2))
            self.speed = 0
            self.x = W // 2
            self.y = H // 2
            self.countdown = 5
        
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
        
        def switch(self):
            self.image_id = 1 - self.image_id
            self.image = self.images[self.image_id]
        
        def draw(self, surface):
            self.countdown -= 1
            if self.countdown == 0:
                self.switch()
                self.countdown = 5
            surface.blit(self.image, self.rect)    
    
    
    class Barrier(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = pygame.image.load("../assets/Sprites/Barrier.png")
            self.surf = pygame.Surface((block_width, H))
            
            self.x = x
            self.y = y
            
            self.rect = self.surf.get_rect(center = (self.x, H - self.y))
        
        def move(self, delta_x):
            self.x += delta_x
            self.rect = self.surf.get_rect(center = (int(self.x), int(H - self.y)))
        
        def draw(self, surface):
            surface.blit(self.image, self.rect)
    
    
    class Coin(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.images = [pygame.image.load("../assets/Sprites/Coin1.png"),
                           pygame.image.load("../assets/Sprites/Coin2.png"),
                           pygame.image.load("../assets/Sprites/Coin3.png"),
                           pygame.image.load("../assets/Sprites/Coin4.png"),
                           pygame.image.load("../assets/Sprites/Coin5.png"),
                           pygame.image.load("../assets/Sprites/Coin4.png"),
                           pygame.image.load("../assets/Sprites/Coin3.png"),
                           pygame.image.load("../assets/Sprites/Coin2.png")]
            self.image_id = 0
            self.image = self.images[0]
            self.countdown = 5
            self.surf = pygame.Surface((2 * r, 2 * r))
            
            self.x = x
            self.y = y
            
            self.rect = self.surf.get_rect(center = (self.x, H - self.y))
        
        def move(self, delta_x):
            self.x += delta_x
            self.rect = self.surf.get_rect(center = (int(self.x), int(H - self.y)))
        
        def switch(self):
            self.image_id += 1
            if self.image_id == len(self.images):
                self.image_id = 0
            self.image = self.images[self.image_id]
        
        def draw(self, surface):
            self.countdown -= 1
            if self.countdown == 0:
                self.switch()
                self.countdown = 5
            surface.blit(self.image, self.rect)
    
    
    class Cloud(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = pygame.image.load("../assets/Sprites/Cloud.png")
            self.x = x
            self.y = y
            self.surf = pygame.Surface((256, 128))
            self.rect = self.surf.get_rect(center = (int(self.x), int(H - self.y)))
        
        def move(self, delta_x):
            self.x += delta_x
            if self.x < -100:
                self.x += W + 200
            self.rect = self.surf.get_rect(center = (int(self.x), int(H - self.y)))
        
        def draw(self, surface):
            surface.blit(self.image, self.rect)
    
    
    class Ball(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.image = pygame.image.load("../assets/Sprites/Ball.png")
            self.x = W / 2
            self.y = H / 2
            self.surf = pygame.Surface((2 * r, 2 * r))
            self.rect = self.surf.get_rect(center = (int(self.x), int(H - self.y)))
        
        def set_y(self, new_y):
            self.y = new_y
            self.rect = self.surf.get_rect(center = (int(self.x), int(H - self.y)))
        
        def draw(self, surface):
            surface.blit(self.image, self.rect)
        
    ball = Ball()
    player = Player()
    barriers = []
    coins = []
    clouds = [Cloud(100, 270), Cloud(200, 550), Cloud(500, 140), Cloud(630, 620), Cloud(770, 300), Cloud(990, 550), Cloud(1150, 350)]
    
    """
    # loading barriers and coins from file ...
    load_file = open("../assets/Levels/Level0.txt", "r")
    load_lines = load_file.read().split('\n')
    load_barriers_cnt = int(load_lines[0])
    for i in range(load_barriers_cnt):
        barriers.append(Barrier(*list(map(int, load_lines[i + 1].split()))))
    load_coins_cnt = int(load_lines[load_barriers_cnt + 1])
    for i in range(load_coins_cnt):
        coins.append(Coin(*list(map(int, load_lines[load_barriers_cnt + i + 2].split()))))
    """
    # generating level parts
    for i in range(level_parts_cnt):
        j = random.randint(0, len(level_parts) - 1)
        for k in range(len(level_parts[j]) - 1):
            barriers.append(Barrier(level_parts[j][k][0] + i * 128 * 9 + W, level_parts[j][k][1]))
        coins.append(Coin(level_parts[j][-1][0] + i * 128 * 9 + W, level_parts[j][-1][1]))
    
    running = True
    prevtime = time.time()
    hurt_offset = 2
    last_hurt = prevtime - hurt_offset
    
    education_id = 0
    education_offset = 2.5
    education_time_stamp = prevtime
    education_data = []
    average_relax = 0
    # 0 - start_offset
    # 1 - text
    # 2 - receiving
    # 3 - text
    # 4 - receiving
    # 5 - game
    if not USE_DEVICE:
        education_id = 5
    
    while running:
        time.sleep(1 / FPS)
        cur_time = time.time()
        delta_time = cur_time - prevtime
        
        value = device.get_data()
        
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                running = False
            elif i.type == pygame.KEYDOWN:
                if i.key == pygame.K_UP:
                    player.add_speed(17 * G * delta_time)
        if education_id == 5:
            if USE_DEVICE:
                history_data.append(value)
                # print(value)
                value = max(0, value - average_relax) * MUSCLE_COEFF
                player.add_speed(value * G * delta_time)
        
            player.add_speed(-G * delta_time)
            player.move(player.speed * delta_time)
        
        sc.fill(SKY)
        
        for cloud in clouds:
            cloud.move(-3 * x_speed * delta_time / 2)
            cloud.draw(sc)
        
        
        if education_id != 5 and cur_time > education_time_stamp + education_offset:
            education_id += 1
            education_time_stamp = cur_time
            if education_id == 3:
                if len(education_data) != 0:
                    average_relax = min(education_data)
                    average_relax = max(average_relax, 0)
                    print(average_relax)
                    education_data = []
            if education_id == 5:
                if len(education_data) != 0:
                    average = sum(education_data) / len(education_data) * 0.5
                    average = max(average, 1 + average_relax)
                    MUSCLE_COEFF = 1 / (average - average_relax)
                    print(average)
        
        if education_id == 0:
            ball.set_y(H * value / 15)
            ball.draw(sc)
        elif education_id == 1:
            education_surface = my_font.render("Приготовьтесь расслабить мышцы", False, BLACK)
            sc.blit(education_surface, (100, H * 3 / 5))
            ball.set_y(H * value / 15)
            ball.draw(sc)
        elif education_id == 2:
            education_surface = my_font.render("Расслабьте мышцы", False, BLACK)
            sc.blit(education_surface, (100, H * 3 / 5))
            education_data.append(value)
            ball.set_y(H * value / 15)
            ball.draw(sc)
        elif education_id == 3:
            education_surface = my_font.render("Приготовьтесь напрягать мышцы", False, BLACK)
            sc.blit(education_surface, (100, H * 3 / 5))
            ball.set_y(H * value / 15)
            ball.draw(sc)
        elif education_id == 4:
            education_surface = my_font.render("Напрягайте мышцы", False, BLACK)
            sc.blit(education_surface, (100, H * 3 / 5))
            education_data.append(value)
            ball.set_y(H * value / 15)
            ball.draw(sc)
        else:
            player.draw(sc)
            for barrier in barriers:
                barrier.move(-x_speed * delta_time)
                barrier.draw(sc)
                if pygame.sprite.spritecollideany(player, barriers):
                    if cur_time > last_hurt + hurt_offset:
                        hurt_cnt += 1
                        last_hurt = cur_time
        
            for coin in coins:
                coin.move(-x_speed * delta_time)
                coin.draw(sc)
            for coin in pygame.sprite.spritecollide(player, coins, False):
                coin_cnt += 1
                coin.kill()
                coins.remove(coin)
        
            hurt_surface = my_font.render("Hits: " + str(hurt_cnt), False, RED)
            sc.blit(hurt_surface, (0, 0))
            coin_surface = my_font.render("Coins: " + str(coin_cnt), False, GOLD)
            sc.blit(coin_surface, (0, 90))
        
        pygame.display.update()
        prevtime = time.time()
    
    
    pygame.quit()
    device.stop()



#threading.Thread(target=side_thread, daemon=True).start()
side_thread()
"""
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def animate(i):
    y_values = history_data[-100:]
    x_values = list(range(len(y_values)))
    plt.cla()
    plt.ylim(0, 15)
    plt.plot(x_values, y_values)


ani = FuncAnimation(plt.gcf(), animate, 1000)    
plt.tight_layout()
plt.show()
"""