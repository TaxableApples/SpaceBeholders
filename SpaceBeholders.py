from operator import xor
from pyexpat.errors import XML_ERROR_SUSPENDED
import pygame
import pygame.freetype
from pygame.locals import *
import random as rd
import numpy as np
from os import path

pygame.freetype.init()
pygame.init()
pygame.event.set_grab(True)

WIDTH, HEIGHT = 1024, 768
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

try:
    pygame.mixer.init()
except:
    SOUND = 0
    print("Error: Failed to load sound device!")

class Player_sheet():
    def __init__(self):        
        self.image = pygame.image.load(path.join(IMG_FOLDER,"ship_pixel.png")).convert()
        self.size = self.image.get_size()
        self.sheet = pygame.transform.scale(self.image, (int(self.size[0]*4), int(self.size[1]*4)))

    def get_image(self, row, frame):
        image = pygame.Surface((96, 96))
        image.blit(self.sheet, (0,0), ((frame * 96), (row * 96), 96, 96))
        image.set_colorkey((255,255,255))

        return image

class Alien_sheet():
    def __init__(self):
        self.image = pygame.image.load(path.join(IMG_FOLDER, "beholder_pixel.png")).convert()
        self.size = self.image.get_size()
        self.sheet = pygame.transform.scale(self.image, (int(self.size[0]*4), int(self.size[1]*4)))

    def get_image(self, row, frame):
        image = pygame.Surface((96, 96))
        image.blit(self.sheet, (0,0), ((frame * 96), (row * 96), 96, 96))
        image.set_colorkey((255,255,255))

        return image

class Explosion_sheet():
    def __init__(self):
        self.sheet = pygame.image.load(path.join(IMG_FOLDER, "explosion_01.png")).convert()

    def get_image(self, frame):
        image = pygame.Surface((100, 100))
        image.blit(self.sheet, (0,0), ((frame * 100), 0, 100, 100))
        image.set_colorkey((0,0,0))

        return image

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image0 = Player_sheet().get_image(0,0)
        self.image1 = Player_sheet().get_image(0,1)
        self.image2 = Player_sheet().get_image(0,2)
        self.image3 = Player_sheet().get_image(1,0)
        self.image4 = Player_sheet().get_image(1,1)
        self.image = self.image0
        self.image.set_colorkey((255,255,255))
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
        self.image1 = Player_sheet().get_image(1,2)
        self.image2 = Player_sheet().get_image(2,0)
        self.image = self.image1
        self.image.set_colorkey((255,255,255))
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

class Particles(pygame.sprite.Sprite):
    def __init__(self, x, y, xspeed, yspeed, color, lifespan):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((rd.randint(1,4),(rd.randint(1,4))))
        self.random = rd.randint(0,1)
        self.image.fill(color)
        self.image.set_colorkey((0,0,0)) 
        self.rect = self.image.get_rect()
        self.rect.centery = y 
        self.rect.centerx = x
        self.xspeed = xspeed
        self.yspeed = yspeed
        self.lifespan = lifespan
        self.timer = 0

    def update(self):
        self.timer += 1

        self.rect.y += self.yspeed
        self.rect.x += self.xspeed
        if self.rect.y > HEIGHT or self.timer > self.lifespan:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((4,4))
        self.image.fill((0,255,0))
        self.image.set_colorkey((0,0,0))     
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

class Healthpack(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(IMG_FOLDER, "healthpack.png")).convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.speedy = rd.randint(4,10)
        self.rect.y = -100
        self.rect.x = rd.randint(0,WIDTH)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10:
            self.kill()

class Healthbar(pygame.sprite.Sprite):
    def __init__(self, loc):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(IMG_FOLDER, "healthbar.png")).convert()
        self.health = pygame.image.load(path.join(IMG_FOLDER, "health.png")).convert()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = loc

class Alien(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image1 = Alien_sheet().get_image(0,0)
        self.image2 = Alien_sheet().get_image(0,1)
        self.image3 = Alien_sheet().get_image(0,2)
        self.image4 = Alien_sheet().get_image(0,3)
        self.image5 = Alien_sheet().get_image(0,4)
        self.image6 = Alien_sheet().get_image(0,5)
        self.image7 = Alien_sheet().get_image(0,6)
        self.image8 = Alien_sheet().get_image(0,7)
        self.image9 = Alien_sheet().get_image(0,8)
        self.image10 = Alien_sheet().get_image(0,9)
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
        
        self.image1 = Alien_sheet().get_image(1,0)
        self.image2 = Alien_sheet().get_image(1,1)
        self.image3 = Alien_sheet().get_image(1,2)
        self.image4 = Alien_sheet().get_image(1,3)
        self.image5 = Alien_sheet().get_image(1,4)
        self.image6 = Alien_sheet().get_image(1,5)
        self.image7 = Alien_sheet().get_image(1,6)
        self.image8 = Alien_sheet().get_image(1,7)
        self.image9 = Alien_sheet().get_image(1,8)
        self.image10 = Alien_sheet().get_image(1,9)

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
            self.image = pygame.image.load(path.join(IMG_FOLDER, "asteroid_lg.png")).convert()
        elif self.randomize == 2:
            self.image = pygame.image.load(path.join(IMG_FOLDER, "asteroid_lg2.png")).convert()
        elif self.randomize == 3:
            self.image = pygame.image.load(path.join(IMG_FOLDER, "asteroid_md.png")).convert()
        else:
            self.image = pygame.image.load(path.join(IMG_FOLDER, "asteroid_sm.png")).convert()
        self.size = self.image.get_size()
        self.upsize = pygame.transform.scale(self.image, (int(self.size[0]*4), int(self.size[1]*4)))
        self.image = self.upsize
        self.image.set_colorkey((255,255,255))
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

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        
        self.image1 = Explosion_sheet().get_image(0)
        self.image2 = Explosion_sheet().get_image(1)
        self.image3 = Explosion_sheet().get_image(2)
        self.image4 = Explosion_sheet().get_image(3)
        self.image5 = Explosion_sheet().get_image(4)
        self.image6 = Explosion_sheet().get_image(5)
        self.image7 = Explosion_sheet().get_image(7)
        self.image8 = Explosion_sheet().get_image(8)
        self.image9 = Explosion_sheet().get_image(9)
        self.image10 = Explosion_sheet().get_image(10)
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
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(IMG_FOLDER, "cursor.png")).convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
    
    def update(self):
        x, y = pygame.mouse.get_pos()
        self.rect.x = x - 23
        self.rect.y = y - 23

class Splashscreen(object):
    def __init__(self):
        self.running = True
        self.logo = Alien_sheet().get_image(0,0)
        self.logo.set_colorkey((255,255,255))

    def run(self):
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    self.running = False
                    pygame.time.set_timer(pygame.KEYDOWN, 0)
                if e.type == pygame.KEYDOWN:
                        if e.key == K_ESCAPE:
                            main_game_loop(False)

            SCREEN.fill((0,0,0))
            SCREEN.blit(self.logo, (440, 200))
            GAMEFONT.render_to(SCREEN, (210 ,HEIGHT / 2), "SPACE BEHOLDERS", (255,0,0), None, size=64)
            GAMEFONT.render_to(SCREEN, (370 , 500), "Press Any Key to Play", (255,0,0), None, size=22)
            GAMEFONT.render_to(SCREEN, (190 , 600), "Use Mouse to aim and shoot, Use keys A,S,D,W to fly", (255,0,0), None, size=22)
            GAMEFONT.render_to(SCREEN, (330, 650), "Press the Spacebar to pause", (255,0,0), None, size=22)
            pygame.display.flip()

class PlayGame(object):
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
        self.fps = 60
        self.spawn = pygame.USEREVENT + 1
        self.clock = pygame.time.Clock()
        self.all = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.fx = pygame.sprite.Group()
        self.debris = pygame.sprite.Group()
        self.ship = pygame.sprite.Group()
        self.powerup = pygame.sprite.Group()
        self.player = Player()
        self.cursor = Cursor()
        self.healthbar = Healthbar([5,5])
        self.shooting = False
        self.bullet_timer = 0.5
        self.shoot_if = 0       
        self.all.add(self.player)
        self.all.add(self.cursor)

    def run(self):
        def timed_and_random_events():
            self.clock.tick(self.fps)

            if self.start:
                self.start = False

                for _ in range(self.level):
                    self.m = Alien()
                    self.all.add(self.m)
                    self.enemies.add(self.m)

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
                self.exhaust = Particles((self.player.rect.centerx+rd.randint(-25,+25)), (self.player.rect.centery+25), 0, rd.randint(5,10), (255, 165, 0), rd.randint(25,100)) #Orange
                self.all.add(self.exhaust)

            if self.random > (10000 - self.level):
                self.healthpack = Healthpack()
                self.powerup.add(self.healthpack)
                self.all.add(self.healthpack)

        def player_controls():
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == K_ESCAPE:
                        self.running = False
                        global QUIT
                        QUIT = True
                    else:
                        QUIT = False

                if e.type == pygame.MOUSEBUTTONDOWN:
                    self.bullet_timer = 0
                    self.shooting = True
                
                if e.type == pygame.MOUSEBUTTONUP:
                    self.shooting = False

                if self.shooting:
                    self.bullet_timer -= self.shoot_if
                    if self.bullet_timer <= 0:
                        self.bullet_timer = 0.5
                        self.bullet = Bullet(self.player.rect.centerx, self.player.rect.centery)
                        self.all.add(self.bullet)
                        self.bullets.add(self.bullet)
                        if SOUND > 0: 
                            pygame.mixer.Channel(0).play(pygame.mixer.Sound(path.join(SOUND_FOLDER, "shoot.ogg")))
                        self.accuracy[1] += 1

        def pause_game():
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == K_SPACE:
                        self.pause = True

                while self.pause:
                        for e in pygame.event.get():
                            if e.type == pygame.KEYDOWN:
                                self.pause = False

        def enemy_hit_by_bullet():
                enemy_hit_by_bullet = pygame.sprite.groupcollide(self.bullets, self.enemies, False, False)
                for sprite in enemy_hit_by_bullet:
                    ex = sprite.rect.x
                    ey = sprite.rect.y
                    r = rd.randint(3,6)
                    for _ in range(r):
                        laser = Particles(ex, ey, rd.randint(-5,5), rd.randint(-5,5), (0,(rd.randint(100,255)),0), rd.randint(25,100))
                        blood = Particles(ex, ey, rd.randint(-5,5), rd.randint(-5,5), ((rd.randint(100,255)),0,0), rd.randint(25,100))
                        purplegoo = Particles(ex, ey, rd.randint(-5,5), rd.randint(-5,5), (147,112,219), rd.randint(25,100))
                        self.all.add(laser, blood, purplegoo)
        
        def player_shoot_enemy():
            player_shoot_enemy = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
            for sprite in player_shoot_enemy:
                if dict[sprite]:
                    d = AlienDeath(sprite.rect.x, sprite.rect.y, sprite.speedx, sprite.speedy)
                    if SOUND > 0: 
                        pygame.mixer.Channel(1).play(pygame.mixer.Sound(path.join(SOUND_FOLDER, "explosion.ogg")))
                    self.all.add(d)
                    self.score += rd.randint(5,20)
                    self.accuracy[0] += 1
                    
                if self.timer > 5.0 and len(self.enemies) <= self.level:
                    m = Alien()
                    self.all.add(m)
                    self.enemies.add(m)
        
        def player_shoot_asteroid():
            player_shoot_asteroid = pygame.sprite.groupcollide(self.bullets, self.asteroids, True, False)
            for sprite in player_shoot_asteroid:
                ex = sprite.rect.x  
                ey = sprite.rect.y
                r = rd.randint(3,6)
                for i in range(r):
                    pA = Particles(ex, ey, rd.randint(-5,5), rd.randint(-5,5), (0,(rd.randint(100,255)),0), rd.randint(25,100))

                    self.all.add(pA)
        
        def player_health_pickup():
            player_health_pickup = pygame.sprite.spritecollide(self.player, self.powerup, True, pygame.sprite.collide_circle)
            if player_health_pickup:
                self.player.health = 196
        
        def player_asteroid_collide():
            player_asteroid_collide = pygame.sprite.spritecollide(self.player, self.asteroids, False, pygame.sprite.collide_circle)
            if player_asteroid_collide:
                self.player.health -= rd.randint(5,12)
            
            for sprite in player_asteroid_collide:
                if dict[sprite]:
                    ex = (sprite.rect.x + self.player.rect.x) / 2    
                    ey = (sprite.rect.y + self.player.rect.y) / 2
                    e = Explosion(ex, ey)
                    d = Playerdamage(self.player.rect.x, self.player.rect.y)

                    self.all.add(d, e)
                    self.fx.add(d, e)
        
        def player_enemy_collide():
            player_enemy_collide = pygame.sprite.spritecollide(self.player, self.enemies, False, pygame.sprite.collide_circle)
            if player_enemy_collide:
                self.player.health -= rd.randint(5,10)
            
            for sprite in player_enemy_collide:
                if dict[sprite]:
                    d = Playerdamage(self.player.rect.x, self.player.rect.y)

                    self.all.add(d)
                    self.fx.add(d)
        
        def win_lose_game():
            if self.player.health <= 0:
                self.running = 0

            if len(PENALTY) > 1:
                self.score -= PENALTY[1]
                PENALTY.pop()

            if self.accuracy[1] != 0:
                self.acccalc = self.accuracy[0] * 1.0 / self.accuracy[1]*100
        
        def go_to_next_level():
            if self.timer == 0:
                levelup = True
                newlevel = self.level + 1
                while levelup:
                    SCREEN.fill((0,0,0))
                    GAMEFONT.render_to(SCREEN, (100,470), "Press Any Key to Continue to Level: " + str(self.level - 3), (255,0,0), None, size=40)
                    GAMEFONT.render_to(SCREEN, (400,550), "SCORE: " + str(self.score), (255,0,0), None, size=40)
                    
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
        
        def draw_to_screen():
            SCREEN.fill((0,0,0))
            SCREEN.blit(self.healthbar.image,(5,5))
            for i in range(self.player.health):
                SCREEN.blit(self.healthbar.health, (i+8,8))

            GAMEFONT.render_to(SCREEN, (875,15), "'Esc' to Quit", (255,0,0), None, size=18)
            GAMEFONT.render_to(SCREEN, (200,700), "Score: " + str(self.score), (255,0,0), None, size=18)            
            GAMEFONT.render_to(SCREEN, (10,700), "Level: " + str(self.level - 3), (255,0,0), None, size=18)
            GAMEFONT.render_to(SCREEN, (400,700), "Round: " + str(self.timer), (255,0,0), None, size=18) 
            GAMEFONT.render_to(SCREEN, (700,700), "Accuracy: " + str(round(self.acccalc, 2)) + "%", (255,0,0), None, size=18)          
            if self.timer < 3.0:
                GAMEFONT.render_to(SCREEN, (500,300), str(int(self.timer)), (255,0,0), None, size=40)

            if int(self.clock.get_fps()) > 58:
                self.newdebris = SpaceDebris()
                self.debris.add(self.newdebris)
                self.all.add(self.newdebris)

            self.all.draw(SCREEN)

            if DEBUG:
                #pygame.draw.circle(SCREEN, (0,255,0), (self.player.rect.centerx, self.player.rect.centery), 42, 1)
                #for sprite in self.asteroids:
                #    pygame.draw.circle(SCREEN, (255,0,0), (sprite.rect.centerx, sprite.rect.centery), 44, 1)
                #for sprite in self.enemies:
                #    pygame.draw.circle(SCREEN, (255,0,0), (sprite.rect.centerx, sprite.rect.centery), 44, 1)
                GAMEFONT.render_to(SCREEN, (250,10), "DEBUG MODE ON", (255,0,0), None, size=18)
                GAMEFONT.render_to(SCREEN, (10,650), "Enemies: " + str(len(self.enemies)), (255,0,0), None, size=18)   
                GAMEFONT.render_to(SCREEN, (700,650), str(self.clock), (255,0,0), None, size=18)
        
        def set_score():
            global SCORE 
            SCORE = self.score  

            global ACCBONUS
            ACCBONUS = self.acccalc * 10 * (self.level - 3)

        while self.running:       
            timed_and_random_events()
            player_controls()
            pause_game()
            enemy_hit_by_bullet()
            player_shoot_enemy()
            player_shoot_asteroid()
            player_health_pickup()
            player_asteroid_collide()
            player_enemy_collide()
            win_lose_game()
            go_to_next_level()              
            draw_to_screen()
            self.all.update()
            pygame.display.flip()

        set_score()

class End_Game_Screen(object):
    def __init__(self):
        self.running = True
        self.timer = 1200

    def run(self):
        while self.running:
            SCREEN.fill((0,0,0))
            GAMEFONT.render_to(SCREEN, (400,300), f"GAME OVER", (255,0,0), None, size=40)
            #GAMEFONT.render_to(SCREEN, (350,350), "Final Score: " + str(score), (255,0,0), None, size=40)
            
            if self.timer > 0:
                self.timer -= 1

            if self.timer <= 0:
                GAMEFONT.render_to(SCREEN, (390,410), "Press 'esc' to quit", (255,0,0), None, size=20)
                GAMEFONT.render_to(SCREEN, (340,450), "Press 'any key' to continue", (255,0,0), None, size=20)
                for e in pygame.event.get():
                    if e.type == pygame.KEYDOWN:
                        self.running = False
                        pygame.time.set_timer(pygame.KEYDOWN, 0)

                    if e.type == pygame.KEYDOWN:
                        if e.key == K_ESCAPE:
                            pygame.quit()

            pygame.display.flip()                        

def main_game_loop(running):
    pygame.display.set_caption("SPACE BEHOLDERS")
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    if SOUND > 0: 
        pygame.mixer.music.load(path.join(SOUND_FOLDER,"space track.ogg"))
        pygame.mixer.music.play(loops = -1)        

    while running:
        Splashscreen().run() 
        PlayGame().run() 
        End_Game_Screen().run()
        # if firstrun:
        #     score = SCORE
        #     accbonus = ACCBONUS
        #     firstrun = False  
        
        # if timer < 1500 and accbonus >= 0:
        #     accbonus -= 1
        #     if score > 0:
        #         score += 1
        #     else:
        #         score -=1
    
    pygame.quit()

main_game_loop(True)