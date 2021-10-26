"""
Installation:
py -m pip install pygame numpy

Start:
py SpaceBoholders.py

test

"""

import pygame
from pygame.locals import *
import random as rd
import math
import numpy as np
from os import path

# constants
WIDTH = 1024
HEIGHT = 768
FPS = 60
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
YELLOW = (255, 255, 0)

game_folder = path.dirname(__file__)
img_folder = path.join(game_folder, "img")

# initialize pygame and make a window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SPACE BEHOLDERS")
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

splash = 1
running = 0

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(img_folder, "ship.png")).convert()
        self.backup_image = self.image
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.radius = 44
        self.rect.center = (WIDTH - 1014, HEIGHT / 2)
        self.speedx = 0
        self.speedy = 0

    def update(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.rect.x, mouse_y - self.rect.y
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.image = pygame.transform.rotate(self.backup_image, int(angle))
        self.rect = self.image.get_rect(center=self.rect.center)
    
        if self.speedx > 0:
            self.speedx -= .08
        if self.speedx < 0:
            self.speedx += .08
        if self.speedy > 0:
            self.speedy -= .08
        if self.speedy < 0:
            self.speedy += .08
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a]:
            self.speedx = -5
        if keystate[pygame.K_d]:
            self.speedx = 5
        if keystate[pygame.K_w]:
            self.speedy = -5
        if keystate[pygame.K_s]:
            self.speedy = 5
            
        if self.rect.left <= 5:
            self.rect.left = 5
        if self.rect.right >= 1020:
            self.rect.right = 1020
        if self.rect.top <= 5:
            self.rect.top = 5
        if self.rect.bottom >= 762:
            self.rect.bottom = 762
        
        self.rect.x += self.speedx
        self.rect.y += self.speedy
    
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.centery)
        all_sprites.add(bullet)
        bullets.add(bullet)
    
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image1 = pygame.image.load(path.join(img_folder, "alien.png")).convert()
        self.image2 = pygame.image.load(path.join(img_folder, "alien2.png")).convert()
        self.image = self.image1
        self.image.set_colorkey(WHITE)
        self.image2.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.radius = 44
        self.rect.x = rd.randrange(0, WIDTH - self.rect.width)
        self.rect.y = rd.randrange(-100, -40)
        self.speedy = rd.randrange(1, 8)
        self.speedx = rd.randrange(-3, 3)
        self.last_update = pygame.time.get_ticks()
    
    def update_image(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 80:
            if self.image == self.image1:
                self.image = self.image2
            else:
                self.image = self.image1
            self.last_update = now
    
    def update(self):
        self.update_image()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT + 10 or self.rect.left < - 25 or self.rect.right > WIDTH + 20:
            self.rec = self.image.get_rect()
            self.rect.x = rd.randrange(0, WIDTH - self.rect.width)
            self.rect.y = rd.randrange(-100, -40)
            self.speedy = rd.randrange(1, 8)
            
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        #self.image = pygame.image.load(path.join(img_folder, "bullet.png")).convert()
        self.image = pygame.Surface((10,10))
        self.image.fill(GREEN)
        
        self.rect = self.image.get_rect()
        self.rect.centery = y
        self.rect.centerx = x
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.velx = mouse_x - self.rect.centerx
        self.vely = mouse_y - self.rect.centery
        self.velocity = np.array([self.velx, self.vely])
        self.velocity = 10 * self.velocity / np.linalg.norm(self.velocity)
        
    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        
        if self.rect.bottom < 0:
            self.kill()
        if self.rect.top > 768:
            self.kill()
        if self.rect.left < 0:
            self.kill()
        if self.rect.right > 1024:
            self.kill()

class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(img_folder, "cursor.png")).convert()
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
    
    def update(self):
        x, y = pygame.mouse.get_pos()
        self.rect.x = x - 23
        self.rect.y = y - 23
        
# other graphics
space = pygame.image.load(path.join(img_folder, "space.png")).convert()
  
# Sprites
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
cursor = Cursor()
player = Player()
all_sprites.add(player)
all_sprites.add(cursor)

for i in range(8):
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

while splash:
  screen.fill(0)
  # backdrop()
  
  font = pygame.font.Font(None, 54)
  splashtext = font.render("SPACE BEHOLDERS", True, (255,0,0))
  screen.blit(splashtext, (screen.get_rect().centerx-165,screen.get_rect().centery))
  font = pygame.font.Font(None, 32)
  splashtext = font.render("press any key to start", True, (255,255,255))
  screen.blit(splashtext, (screen.get_rect().centerx-75,screen.get_rect().centery+50))
  font = pygame.font.Font(None, 32)
  splashtext = font.render("Use Mouse to aim, Use keys A,S,D,W to fly", True, (255,255,255))
  screen.blit(splashtext, (screen.get_rect().centerx,screen.get_rect().centery+50))
  pygame.display.flip()
  
  for event in pygame.event.get():
    if event.type == pygame.KEYDOWN:
      splash = 0
      running = 1
      pygame.time.set_timer(pygame.KEYDOWN, 0)
  
# 4 game loop
exitcode = 0

#Game Loop
while running:
    clock.tick(FPS)
    
    # 1.0 Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            player.shoot()
            
    # 2.0 Update
    all_sprites.update()
    
    # 2.1 check for collisions
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        m = Mob()
        all_sprites.add(m)
        mobs.add(m)
        
    hits = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_circle)
    if hits:
        running = True #Change to False to test collisions
    
    # 3.0 Draw
    screen.fill(BLACK)
    screen.blit(space,(32,64))
    
    all_sprites.draw(screen)
    pygame.display.flip() # always do this last
    
pygame.quit()