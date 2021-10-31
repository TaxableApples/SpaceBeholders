import pygame
from pygame.locals import *
import random as rd
import math
import numpy as np
from os import path

WIDTH = 1024
HEIGHT = 768
FPS = 60
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
YELLOW = (255, 255, 0)

game_folder = path.dirname(__file__)
resources_folder = path.join(game_folder, "resources")
img_folder = path.join(resources_folder, "images")

# initialize pygame and make a window
pygame.init()
pygame.mixer.init()
pygame.freetype.init();
pygame.display.set_caption("SPACE BEHOLDERS")
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
gameover = pygame.image.load(path.join(img_folder, "gameover.png"))
youwin = pygame.image.load(path.join(img_folder, "youwin.png"))

score = 0
splash = 1
running = 0
exitcode = 0

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()

class Player(pygame.sprite.Sprite):
    def __init__(self, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(img_folder, img)).convert()
        self.backup_image = self.image
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.radius = 44
        self.rect.center = (WIDTH / 2, HEIGHT - 20)
        self.speedx = 0
        self.speedy = 0
        self.health = 196

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
        bullet = Bullet(self.rect.centerx, self.rect.centery, GREEN)
        all_sprites.add(bullet)
        bullets.add(bullet)
    
class Mob(pygame.sprite.Sprite):
    def __init__(self, img1, img2):
        pygame.sprite.Sprite.__init__(self)
        self.image1 = pygame.image.load(path.join(img_folder, img1)).convert()
        self.image2 = pygame.image.load(path.join(img_folder, img2)).convert()
        self.image = self.image1
        self.image.set_colorkey(WHITE)
        self.image2.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.radius = 44
        self.rect.x = rd.randrange(0, WIDTH - self.rect.width)
        self.rect.y = rd.randrange(-100, -40)
        self.speedy = rd.randrange(1, 8)
        self.speedx = rd.randrange(-3, 3)
        self.penalty = 0
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
        if self.rect.top > HEIGHT + 10:
            self.penalty = rd.randint(5,20)
            self.rec = self.image.get_rect()
            self.rect.x = rd.randrange(0, WIDTH - self.rect.width)
            self.rect.y = rd.randrange(-100, -40)
            self.speedy = rd.randrange(1, 8)
            penalties.append(self.penalty)
            #self.kill()
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speedx = -self.speedx
            
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10,10))
        self.image.fill(color)       
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
    def __init__(self, file):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(img_folder, file)).convert()
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
    
    def update(self):
        x, y = pygame.mouse.get_pos()
        self.rect.x = x - 23
        self.rect.y = y - 23
        
class Healthbar(pygame.sprite.Sprite):
    def __init__(self, img, img2, loc):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(img_folder, img)).convert()
        self.health = pygame.image.load(path.join(img_folder, img2)).convert()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = loc

class Background(pygame.sprite.Sprite):
    def __init__(self, img, loc):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(img_folder, img)).convert()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = loc

# Splash Screen 
while splash:
  screen.fill(0)
  font = pygame.font.Font(None, 54)
  splashtext = font.render("SPACE BEHOLDERS", True, (255,0,0))
  screen.blit(splashtext, (screen.get_rect().centerx-165,screen.get_rect().centery))
  font = pygame.font.Font(None, 32)
  splashtext = font.render("press any key to start", True, (255,255,255))
  screen.blit(splashtext, (screen.get_rect().centerx-75,screen.get_rect().centery+50))
  font = pygame.font.Font(None, 32)
  splashtext = font.render("Use Mouse to aim, Use keys A,S,D,W to fly", True, (255,255,255))
  screen.blit(splashtext, (screen.get_rect().centerx-150,screen.get_rect().centery+150))
  pygame.display.flip()
  
  for event in pygame.event.get():
    if event.type == pygame.KEYDOWN:
      splash = 0
      running = 1
      pygame.time.set_timer(pygame.KEYDOWN, 0)

space = Background("space.png", [0,0])
cursor = Cursor("cursor.png")
healthbar = Healthbar("healthbar.png", "health.png", [5,5])
player = Player("ship.png")
penalties = [0]
all_sprites.add(player)
all_sprites.add(cursor)

for i in range(5):
    m = Mob("alien.png", "alien2.png")
    all_sprites.add(m)
    mobs.add(m)


# Game Loop******************************************
while running:
    clock.tick(FPS)
    
    # Events
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
                exitcode = 0
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            player.shoot()
            
    # Update
    all_sprites.update()
    
    # Check for Collisions
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        m = Mob("alien.png", "alien2.png")
        all_sprites.add(m)
        mobs.add(m)
        score += rd.randint(5,20)

    collide = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_circle)
    if collide:
        player.health -= rd.randint(5,20)

    # Win / Lose
    if player.health <= 0:
        exitcode=1
        running=0

    if len(penalties) > 1:
        score -= penalties[1]
        penalties.pop()

    # Draw
    screen.fill(BLACK)
    screen.blit(space.image,space.rect)
    screen.blit(healthbar.image,(5,5))

    font = pygame.font.Font(None, 32)
    scoretext = font.render("score: " + str(score), True, (255,0,0))
    screen.blit(scoretext, (500,700))
    
    for health1 in range(player.health):
        screen.blit(healthbar.health, (health1+8,8))
    
    all_sprites.draw(screen)
    pygame.display.flip()

# game over *****************************************
while exitcode:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                exitcode = 0

    screen.fill(0)
    if player.health<=0: 
        screen.blit(gameover, (0,0))
    else: 
        screen.blit(youwin, (0,0))

    pygame.display.flip()

pygame.quit()
