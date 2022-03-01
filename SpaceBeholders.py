from operator import xor
import pygame
import pygame.freetype
from pygame.locals import *
import random as rd
import math
import numpy as np
from os import path

pygame.freetype.init()

WIDTH, HEIGHT = 1024, 768
FPS = 60
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

BEHOLDER_IMG = "beholder_pixel.png"
ASTEROID_LGA = "asteroid_lg.png"
ASTEROID_LGB = "asteroid_lg2.png"
ASTEROID_MED = "asteroid_md.png"
ASTEROID_SM = "asteroid_sm.png"
EXPLOSION_A = "explosion_01.png"
SHIP_IMG = "ship_pixel.png"
CURSOR_IMG = "cursor.png"
HEALTHBAR_IMG = "healthbar.png"
HEALTH_IMG = "health.png"
BULLET_IMG = "bullet.png"

DEBUG = True
PENALTY = [0]
ACCBONUS = 0
SCORE = 0
SOUND = 1

GAME_FOLDER = path.dirname(__file__)
RESOURCES_FOLDER = path.join(GAME_FOLDER, "resources")
IMG_FOLDER = path.join(RESOURCES_FOLDER, "images")
SOUND_FOLDER = path.join(RESOURCES_FOLDER, "audio")

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
GAMEFONT = pygame.freetype.Font(path.join(RESOURCES_FOLDER, "Retro Gaming.ttf"), 22)

pygame.init()
pygame.event.set_grab(True)

try:
    pygame.mixer.init()
except:
    SOUND = 0
    print("no sound card installed!")

# sounds
if SOUND > 0: 
    enemy_explosion = pygame.mixer.Sound(path.join(SOUND_FOLDER, "explosion.ogg"))
    laser_shoot = pygame.mixer.Sound(path.join(SOUND_FOLDER, "shoot.ogg"))
    pygame.mixer.music.load(path.join(SOUND_FOLDER,"space track.ogg"))
    pygame.mixer.music.play(loops = -1)

class Playersheet():
    def __init__(self):        
        self.image = pygame.image.load(path.join(IMG_FOLDER,SHIP_IMG)).convert()
        self.size = self.image.get_size()
        self.sheet = pygame.transform.scale(self.image, (int(self.size[0]*4), int(self.size[1]*4)))

    def get_image(self, row, frame):
        image = pygame.Surface((96, 96))
        image.blit(self.sheet, (0,0), ((frame * 96), (row * 96), 96, 96))
        image.set_colorkey(WHITE)

        return image

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image0 = Playersheet().get_image(0,0)
        self.image1 = Playersheet().get_image(0,1)
        self.image2 = Playersheet().get_image(0,2)
        self.image3 = Playersheet().get_image(1,0)
        self.image4 = Playersheet().get_image(1,1)
        self.image = self.image0
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.radius = 44
        self.rect.center = (WIDTH / 2, HEIGHT - 20)
        self.speedx = 0
        self.speedy = 0
        self.health = 196
        self.last_update = pygame.time.get_ticks()

    def update_image(self):
        now = pygame.time.get_ticks()

        if now - self.last_update > 80:
            if self.image == self.image0:
                self.image = self.image1
            elif self.image == self.image1:
                self.image = self.image2
            elif self.image == self.image2:
                self.image = self.image3
            elif self.image == self.image3:
                self.image = self.image4
            elif self.image == self.image4:
                self.image = self.image0
            self.last_update = now

    def update(self):
        self.update_image()
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

class Playerdamage(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image1 = Playersheet().get_image(1,2)
        self.image2 = Playersheet().get_image(2,0)
        self.image = self.image1
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.timer = 60
    
    def update(self):
        self.timer -= 1

        if self.timer > 0:
            if self.image == self.image1:
                self.image = self.image2
            elif self.image == self.image2:
                self.image = self.image1
        else:
            self.kill()

class Playerexhaust(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((rd.randint(1,4),(rd.randint(1,4))))
        self.random = rd.randint(0,1)
        if self.random == 1:
            self.image.fill(RED)
        else:
            self.image.fill(ORANGE)
        self.image.set_colorkey(BLACK) 
        self.rect = self.image.get_rect()
        self.rect.centery = y 
        self.rect.centerx = x + rd.randint(-25,25)

    def update(self):
        self.rect.y += 10
        if self.rect.y > HEIGHT:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((4,4))
        self.image.fill(GREEN)
        self.image.set_colorkey(BLACK)     
        self.radius = 4.5
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

class Aliensheet():
    def __init__(self):
        self.image = pygame.image.load(path.join(IMG_FOLDER,BEHOLDER_IMG)).convert()
        self.size = self.image.get_size()
        self.sheet = pygame.transform.scale(self.image, (int(self.size[0]*4), int(self.size[1]*4)))

    def get_image(self, row, frame):
        image = pygame.Surface((96, 96))
        image.blit(self.sheet, (0,0), ((frame * 96), (row * 96), 96, 96))
        image.set_colorkey(WHITE)

        return image

class Alien(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image1 = Aliensheet().get_image(0,0)
        self.image2 = Aliensheet().get_image(0,1)
        self.image3 = Aliensheet().get_image(0,2)
        self.image4 = Aliensheet().get_image(0,3)
        self.image5 = Aliensheet().get_image(0,4)
        self.image6 = Aliensheet().get_image(0,5)
        self.image7 = Aliensheet().get_image(0,6)
        self.image8 = Aliensheet().get_image(0,7)
        self.image9 = Aliensheet().get_image(0,8)
        self.image10 = Aliensheet().get_image(0,9)
        self.image = self.image1
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
            elif self.image == self.image2:
                self.image = self.image3
            elif self.image == self.image3:
                self.image = self.image4
            elif self.image == self.image4:
                self.image = self.image5
            elif self.image == self.image5:
                self.image = self.image6
            elif self.image == self.image6:
                self.image = self.image7
            elif self.image == self.image7:
                self.image = self.image8
            elif self.image == self.image8:
                self.image = self.image9
            elif self.image == self.image9:
                self.image = self.image10
            elif self.image == self.image10:
                self.image = self.image1

            self.last_update = now
    
    def update(self):
        self.update_image()
        self.rect.y += self.speedy
        self.rect.x += self.speedx

        if self.rect.top > HEIGHT + 10:
            self.penalty = rd.randint(5,20)
            self.rect.x = rd.randrange(0, WIDTH - self.rect.width)
            self.rect.y = rd.randrange(-600, -300)
            self.speedy = rd.randrange(1, 8)
            PENALTY.append(self.penalty)

        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speedx = -self.speedx

class AlienDeath(pygame.sprite.Sprite):
    def __init__(self, x, y, velx, vely):
        pygame.sprite.Sprite.__init__(self)
        
        self.image1 = Aliensheet().get_image(1,0)
        self.image2 = Aliensheet().get_image(1,1)
        self.image3 = Aliensheet().get_image(1,2)
        self.image4 = Aliensheet().get_image(1,3)
        self.image5 = Aliensheet().get_image(1,4)
        self.image6 = Aliensheet().get_image(1,5)
        self.image7 = Aliensheet().get_image(1,6)
        self.image8 = Aliensheet().get_image(1,7)
        self.image9 = Aliensheet().get_image(1,8)
        self.image10 = Aliensheet().get_image(1,9)

        self.image = self.image1
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.timer = 30
        self.speedx = velx
        self.speedy = vely

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        self.timer -= 1.5
        if self.timer <= 29:
            self.image = self.image1
        if self.timer <= 25:
            self.image = self.image2
        if self.timer <= 20:
            self.image = self.image3
        if self.timer <= 15:
            self.image = self.image4
        if self.timer <= 10:
            self.image = self.image5
        if self.timer <= 5:
            self.image = self.image6
        if self.timer <= 0:
            self.image = self.image7
        if self.timer <= -5:
            self.image = self.image8
        if self.timer <= -10:
            self.image = self.image9
        if self.timer <= -15:
            self.kill()
            
class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x):
        pygame.sprite.Sprite.__init__(self)  

        self.randomize = rd.randint(1,4)
        if self.randomize == 1:
            self.image = pygame.image.load(path.join(IMG_FOLDER, ASTEROID_LGA)).convert()
        elif self.randomize == 2:
            self.image = pygame.image.load(path.join(IMG_FOLDER, ASTEROID_LGB)).convert()
        elif self.randomize == 3:
            self.image = pygame.image.load(path.join(IMG_FOLDER, ASTEROID_MED)).convert()
        else:
            self.image = pygame.image.load(path.join(IMG_FOLDER, ASTEROID_SM)).convert()
        self.size = self.image.get_size()
        self.upsize = pygame.transform.scale(self.image, (int(self.size[0]*4), int(self.size[1]*4)))
        self.image = self.upsize
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.radius = 44
        self.rect.y = -100
        self.rect.x = x
        self.speedy = rd.randrange(1, 8)
        self.last_update = pygame.time.get_ticks()
        self.random = rd.randint(1, 20)
        if self.random > 18:
            self.rect.x = x
        else:
            self.rect.x = rd.randint(0, WIDTH)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10:
            self.kill()

class SpaceDebris(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.pseed = rd.randint(1, 4)
        self.cseed = rd.randint(2, 255)
        self.x = self.pseed
        self.y = self.pseed
        self.speed = rd.randrange(8, 12)
        self.image = pygame.Surface((self.x, self.y))
        self.image.fill((self.cseed, self.cseed, self.cseed))
        self.rect = self.image.get_rect()
        self.rect.y = -100
        self.rect.x = rd.randint(0, WIDTH)
        self._layer = -1

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT + 10:
            self.kill()

class Explosionsheet():
    def __init__(self):
        self.sheet = pygame.image.load(path.join(IMG_FOLDER, EXPLOSION_A)).convert()

    def get_image(self, frame):
        image = pygame.Surface((100, 100))
        image.blit(self.sheet, (0,0), ((frame * 100), 0, 100, 100))
        image.set_colorkey(BLACK)

        return image

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        self.image1 = Explosionsheet().get_image(0)
        self.image2 = Explosionsheet().get_image(1)
        self.image3 = Explosionsheet().get_image(2)
        self.image4 = Explosionsheet().get_image(3)
        self.image5 = Explosionsheet().get_image(4)
        self.image6 = Explosionsheet().get_image(5)
        self.image7 = Explosionsheet().get_image(7)
        self.image8 = Explosionsheet().get_image(8)
        self.image9 = Explosionsheet().get_image(9)
        self.image10 = Explosionsheet().get_image(10)
        self.image = self.image1
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.timer = 30

    def update(self):
        self.timer -= 1.5
        if self.timer <= 25:
            self.image = self.image1
        if self.timer <= 20:
            self.image = self.image2
        if self.timer <= 40:
            self.image = self.image3
        if self.timer <= 15:
            self.image = self.image4
        if self.timer <= 10:
            self.image = self.image5
        if self.timer <= 5:
            self.image = self.image6
        if self.timer <= 0:
            self.kill()

class Cursor(pygame.sprite.Sprite):
    def __init__(self, file):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(IMG_FOLDER, file)).convert()
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
    
    def update(self):
        x, y = pygame.mouse.get_pos()
        self.rect.x = x - 23
        self.rect.y = y - 23
        
class Healthbar(pygame.sprite.Sprite):
    def __init__(self, img, img2, loc):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(IMG_FOLDER, img)).convert()
        self.health = pygame.image.load(path.join(IMG_FOLDER, img2)).convert()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = loc

class Splashscreen(object):
    def __init__(self):
        self.running = True
        self.logo = Aliensheet().get_image(0,0)
        self.logo.set_colorkey(WHITE)

    def run(self):
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    self.running = False
                    pygame.time.set_timer(pygame.KEYDOWN, 0)

            SCREEN.fill(BLACK)
            SCREEN.blit(self.logo, (440, 200))
            GAMEFONT.render_to(SCREEN, (210 ,HEIGHT / 2), "SPACE BEHOLDERS", RED, None, size=64)
            GAMEFONT.render_to(SCREEN, (370 , 500), "Press Any Key to Play", RED, None, size=22)
            GAMEFONT.render_to(SCREEN, (190 , 600), "Use Mouse to aim and shoot, Use keys A,S,D,W to fly", RED, None, size=22)
            GAMEFONT.render_to(SCREEN, (330, 650), "Press the Spacebar to pause", RED, None, size=22)
            pygame.display.flip()

class Game(object):
    def __init__(self):
        self.running = True
        self.score = 0
        self.deaths = -1
        self.level = 4
        self.timer = 00
        self.accuracy = [0,0]
        self.acccalc = 0
        self.pause = False
        self.start_timer = 5.0
        self.start = True

        self.spawn = pygame.USEREVENT + 1
        self.clock = pygame.time.Clock()
        self.all = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.fx = pygame.sprite.Group()
        self.debris = pygame.sprite.Group()
        self.ship = pygame.sprite.Group()

        #self.space = Background(BACKGROUND_IMG, [0,0])
        self.player = Player()
        self.cursor = Cursor(CURSOR_IMG)
        self.healthbar = Healthbar(HEALTHBAR_IMG, HEALTH_IMG, [5,5])
        self.shooting = False
        self.bullet_timer = 0.5
        self.shoot_if = 0
        
        self.all.add(self.player)
        self.all.add(self.cursor)

    def restart(self):
        pygame.time.set_timer(self.spawn, 1000 - self.score * 2)

    def run(self):
        while self.running:
            
            if self.start:
                self.start = False

                for _ in range(self.level):
                    self.m = Alien()
                    self.all.add(self.m)
                    self.enemies.add(self.m)

            self.clock.tick(FPS)

            if self.timer < 0.0:
                self.timer = 20.00

            self.bullet_timer -= 0.025

            self.timer = round(self.timer - .01, 2)

            self.random = rd.randint(1,10000)

            if self.timer > 5.0 and self.random > 9950:
                self.asteroid = Asteroid(self.player.rect.centerx)
                self.asteroids.add(self.asteroid)
                self.all.add(self.asteroid)

            if self.random > 8000:
                self.exhaust = Playerexhaust(self.player.rect.centerx, (self.player.rect.centery+25))
                self.all.add(self.exhaust)

            # Control
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == K_ESCAPE:
                        self.running = False
                        global QUIT
                        QUIT = True
                    else:
                        QUIT = False
                    if e.key == K_SPACE:
                        self.pause = True

                if e.type == pygame.MOUSEBUTTONDOWN:
                    self.bullet_timer = 0
                    self.shooting = True
                
                if e.type == pygame.MOUSEBUTTONUP:
                    self.shooting = False

                if self.shooting:
                    self.bullet_timer -= self.shoot_if
                    if self.bullet_timer <= 0:
                        self.bullet_timer = 0.5
                        self.bullet = Bullet(self.player.rect.centerx, self.player.rect.centery, BULLET_IMG)
                        self.all.add(self.bullet)
                        self.bullets.add(self.bullet)
                        if SOUND > 0: 
                            pygame.mixer.Channel(0).play(laser_shoot)
                        self.accuracy[1] += 1

            self.all.update()

            while self.pause:
                for e in pygame.event.get():
                    if e.type == pygame.KEYDOWN:
                        self.pause = False


            # Collisions
            hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
            for sprite in hits:
                if dict[sprite]:
                    d = AlienDeath(sprite.rect.x, sprite.rect.y, sprite.speedx, sprite.speedy)
                    if SOUND > 0: 
                        pygame.mixer.Channel(1).play(enemy_explosion)
                    self.all.add(d)
                    self.score += rd.randint(5,20)
                    self.accuracy[0] += 1
                    
                if self.timer > 5.0 and len(self.enemies) <= self.level:
                    m = Alien()
                    self.all.add(m)
                    self.enemies.add(m)
      
            asteroid_hit = pygame.sprite.groupcollide(self.asteroids, self.bullets, False, True)

            collide = pygame.sprite.spritecollide(self.player, self.asteroids, False, pygame.sprite.collide_circle)
            if collide:
                self.player.health -= rd.randint(5,10)
            
            for sprite in collide:
                if dict[sprite]:
                    ex = (sprite.rect.x + self.player.rect.x) / 2    
                    ey = (sprite.rect.y + self.player.rect.y) / 2
                    e = Explosion(ex, ey)
                    d = Playerdamage(self.player.rect.x, self.player.rect.y)

                    self.all.add(d)
                    self.fx.add(d)
                    self.all.add(e)
                    self.fx.add(e)

            collide = pygame.sprite.spritecollide(self.player, self.enemies, False, pygame.sprite.collide_circle)
            if collide:
                self.player.health -= rd.randint(1,5)
            
            for sprite in collide:
                if dict[sprite]:
                    d = Playerdamage(self.player.rect.x, self.player.rect.y)

                    self.all.add(d)
                    self.fx.add(d)

            # Win / Lose
            if self.player.health <= 0:
                self.running = 0

            if len(PENALTY) > 1:
                self.score -= PENALTY[1]
                PENALTY.pop()

            if self.timer == 0:
                levelup = True
                newlevel = self.level + 1
                while levelup:
                    SCREEN.fill(BLACK)
                    GAMEFONT.render_to(SCREEN, (100,470), "Press Any Key to Continue to Level: " + str(self.level - 3), RED, None, size=40)
                    GAMEFONT.render_to(SCREEN, (400,550), "SCORE: " + str(self.score), RED, None, size=40)
                    
                    if self.level != newlevel:
                        self.level += 1
                        for _ in range(self.level):
                            m = Alien()
                            self.all.add(m)
                            self.enemies.add(m)
                    
                    for e in pygame.event.get():
                        if e.type == pygame.KEYDOWN:
                            levelup = False
                    pygame.display.flip()
            
            if self.accuracy[1] != 0:
                self.acccalc = self.accuracy[0] * 1.0 / self.accuracy[1]*100

            # Draw
            SCREEN.fill(BLACK)
            SCREEN.blit(self.healthbar.image,(5,5))
            for i in range(self.player.health):
                SCREEN.blit(self.healthbar.health, (i+8,8))

            GAMEFONT.render_to(SCREEN, (875,15), "'Esc' to Quit", RED, None, size=18)
            GAMEFONT.render_to(SCREEN, (200,700), "Score: " + str(self.score), RED, None, size=18)            
            GAMEFONT.render_to(SCREEN, (10,700), "Level: " + str(self.level - 3), RED, None, size=18)
            GAMEFONT.render_to(SCREEN, (400,700), "Round: " + str(self.timer), RED, None, size=18) 
            GAMEFONT.render_to(SCREEN, (700,700), "Accuracy: " + str(round(self.acccalc, 2)) + "%", RED, None, size=18)          
            if self.timer < 3.0:
                GAMEFONT.render_to(SCREEN, (500,300), str(int(self.timer)), RED, None, size=40)

            if int(self.clock.get_fps()) > 58:
                self.newdebris = SpaceDebris()
                self.debris.add(self.newdebris)
                self.all.add(self.newdebris)

            self.all.draw(SCREEN)

            if DEBUG:
                #pygame.draw.circle(SCREEN, GREEN, (self.player.rect.centerx, self.player.rect.centery), 42, 1)
                #for sprite in self.asteroids:
                #    pygame.draw.circle(SCREEN, RED, (sprite.rect.centerx, sprite.rect.centery), 44, 1)
                #for sprite in self.enemies:
                #    pygame.draw.circle(SCREEN, RED, (sprite.rect.centerx, sprite.rect.centery), 44, 1)
                GAMEFONT.render_to(SCREEN, (250,10), "DEBUG MODE ON", RED, None, size=18)
                GAMEFONT.render_to(SCREEN, (10,650), "Enemies: " + str(len(self.enemies)), RED, None, size=18)   
                GAMEFONT.render_to(SCREEN, (700,650), str(self.clock), RED, None, size=18)

            pygame.display.flip()
        
        #These must be defined at the bottom
        global SCORE 
        SCORE = self.score  

        global ACCBONUS
        ACCBONUS = self.acccalc * 10 * (self.level - 3)

def main():
    splash = True
    game = True 
    running = True
    timer = 2000
    firstrun = True

    pygame.display.set_caption("SPACE BEHOLDERS")
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    while running:
        if splash: 
            Splashscreen().run()      
        splash = False

        if game: 
            Game().run()     
        game = False

        if firstrun:
            score = SCORE
            accbonus = ACCBONUS
            firstrun = False

        SCREEN.fill(BLACK)
        
        if timer <=0:
            GAMEFONT.render_to(SCREEN, (390,410), "Press 'esc' to quit", RED, None, size=20)
            GAMEFONT.render_to(SCREEN, (340,450), "Press 'any key' to continue", RED, None, size=20)
        else:
            timer -= 1

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                if timer <=0:
                    running = False

            if e.type == pygame.KEYDOWN:
                if e.key == K_ESCAPE:
                        running = False
                else:
                    if timer <=0:
                        firstrun = True
                        timer = 2000
                        splash = True
                        game = True           

        if QUIT:
            final_message = "You Quit!"
        else:
            final_message = "You Died!"
        
        if timer < 1500 and accbonus >= 0:
            accbonus -= 1
            if score > 0:
                score += 1
            else:
                score -=1
        
        GAMEFONT.render_to(SCREEN, (400,300), final_message, RED, None, size=40)
        GAMEFONT.render_to(SCREEN, (350,350), "Final Score: " + str(score), RED, None, size=40)

        pygame.display.flip()

    pygame.quit()

main()