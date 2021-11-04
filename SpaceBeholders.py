from operator import xor
import pygame
import pygame.freetype
from pygame.locals import *
import random as rd
import math
import numpy as np
from os import path

pygame.freetype.init();

WIDTH, HEIGHT = 1024, 768
FPS = 60
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
YELLOW = (255, 255, 0)

LEVEL = 4
DEBUG = True
PENALTY = [0]

GAME_FOLDER = path.dirname(__file__)
RESOURCES_FOLDER = path.join(GAME_FOLDER, "resources")
IMG_FOLDER = path.join(RESOURCES_FOLDER, "images")

# ALIEN_SHEET_IMAGE = pygame.image.load(path.join(IMG_FOLDER,'beholder.png')).convert_alpha()
# ALIEN_SHEET = Aliensheet(ALIEN_SHEET_IMAGE)

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
GAMEFONT = pygame.freetype.Font(path.join(RESOURCES_FOLDER, "AlloyInk.ttf"), 22)

class Player(pygame.sprite.Sprite):
    def __init__(self, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(IMG_FOLDER, img)).convert()
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

class Aliensheet():
    def __init__(self):
        self.sheet = pygame.image.load(path.join(IMG_FOLDER,'beholder.png')).convert_alpha()

    def get_image(self, row, frame):
        image = pygame.Surface((100, 100)).convert_alpha()
        image.blit(self.sheet, (0,0), ((frame * 100), (row * 100), 100, 100))
        image.set_colorkey(WHITE)

        return image

class Alien(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image1 = Aliensheet().get_image(0,0)
        self.image2 = Aliensheet().get_image(0,1)
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
            else:
                self.image = self.image1
            self.last_update = now
    
    def update(self):
        self.update_image()
        self.rect.y += self.speedy
        self.rect.x += self.speedx

        if self.rect.top > HEIGHT + 10:
            self.penalty = rd.randint(5,20)
            #self.rec = self.image.get_rect()
            self.rect.x = rd.randrange(0, WIDTH - self.rect.width)
            self.rect.y = rd.randrange(-600, -300)
            self.speedy = rd.randrange(1, 8)
            PENALTY.append(self.penalty)

        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speedx = -self.speedx

class AlienDeath(pygame.sprite.Sprite):
    def __init__(self, x, y, velx, vely):
        pygame.sprite.Sprite.__init__(self)
        
        self.image1 = Aliensheet().get_image(0,2)
        self.image2 = Aliensheet().get_image(0,3)
        self.image3 = Aliensheet().get_image(1,0)
        self.image4 = Aliensheet().get_image(1,1)
        self.image5 = Aliensheet().get_image(1,2)
        self.image6 = Aliensheet().get_image(1,3)
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
            self.kill()
            

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load(path.join(IMG_FOLDER, "asteroid2.png"))
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

class Background(pygame.sprite.Sprite):
    def __init__(self, img, loc):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(IMG_FOLDER, img)).convert()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = loc

class Splashscreen(object):
    def __init__(self):
        self.running = True
        self.logo = pygame.image.load(path.join(IMG_FOLDER, "beholder1.png"))
        self.logo.set_colorkey(WHITE)

    def run(self):
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    self.running = False
                    pygame.time.set_timer(pygame.KEYDOWN, 0)

            SCREEN.fill(0)
            SCREEN.blit(self.logo, (440, 200))
            GAMEFONT.render_to(SCREEN, (210 ,HEIGHT / 2), "SPACE BEHOLDERS", RED, None, size=64)
            GAMEFONT.render_to(SCREEN, (370 , 500), "Press Any Key to Play", RED, None, size=22)
            GAMEFONT.render_to(SCREEN, (190 , 600), "Use Mouse to aim and shoot, Use keys A,S,D,W to fly", RED, None, size=22)
            pygame.display.flip()

class Game(object):
    def __init__(self):
        self.running = True
        self.score = 0
        self.deaths = -1
        self.level = 4
        self.timer = 20.00
        self.accuracy = [0,0]
        self.acccalc = 0

        self.spawn = pygame.USEREVENT + 1
        self.clock = pygame.time.Clock()
        self.all = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()

        self.space = Background("space.png", [0,0])
        self.player = Player("ship2.png")
        self.cursor = Cursor("cursor.png")
        self.healthbar = Healthbar("healthbar.png", "health.png", [5,5])
        self.shooting = False
        self.bullet_timer = 0.5
        self.shoot_if = 0

        self.all.add(self.player)
        self.all.add(self.cursor)

        for _ in range(self.level):
            self.m = Alien()
            self.all.add(self.m)
            self.enemies.add(self.m)

    def restart(self):
        pygame.time.set_timer(self.spawn, 1000 - self.score * 2)

    def run(self):
        while self.running:
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

            # Control
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == K_ESCAPE:
                        self.running = False

                if e.type == pygame.MOUSEBUTTONDOWN:
                    self.bullet_timer = 0
                    self.shooting = True
                
                if e.type == pygame.MOUSEBUTTONUP:
                    self.shooting = False

                if self.shooting:
                    self.bullet_timer -= self.shoot_if
                    if self.bullet_timer <= 0:
                        self.bullet_timer = 0.5
                        self.bullet = Bullet(self.player.rect.centerx, self.player.rect.centery, GREEN)
                        self.all.add(self.bullet)
                        self.bullets.add(self.bullet)
                        self.accuracy[1] += 1

            self.all.update()

            # Collisions
            hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
            for sprite in hits:
                if dict[sprite]:
                    d = AlienDeath(sprite.rect.x, sprite.rect.y, sprite.speedx, sprite.speedy)
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
                self.player.health -= rd.randint(5,20)

            collide = pygame.sprite.spritecollide(self.player, self.enemies, False, pygame.sprite.collide_circle)
            if collide:
                self.player.health -= rd.randint(5,20)

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
            SCREEN.blit(self.space.image,self.space.rect)
            SCREEN.blit(self.healthbar.image,(5,5))
            for i in range(self.player.health):
                SCREEN.blit(self.healthbar.health, (i+8,8))

            GAMEFONT.render_to(SCREEN, (875,15), "'Esc' to Quit", RED, None, size=18)
            GAMEFONT.render_to(SCREEN, (500,700), "Score: " + str(self.score), RED, None, size=18)            
            GAMEFONT.render_to(SCREEN, (500,650), "Level: " + str(self.level - 3), RED, None, size=18)
            GAMEFONT.render_to(SCREEN, (500,600), "Round: " + str(self.timer), RED, None, size=18)            
            if self.timer < 3.0:
                GAMEFONT.render_to(SCREEN, (500,300), str(int(self.timer)), RED, None, size=40)
            if DEBUG:
                GAMEFONT.render_to(SCREEN, (700,600), "Enemies: " + str(len(self.enemies)), RED, None, size=18)
                GAMEFONT.render_to(SCREEN, (700,650), "Accuracy: " + str(round(self.acccalc, 2)) + "%", RED, None, size=18)
                GAMEFONT.render_to(SCREEN, (700,700), str(self.clock), RED, None, size=18)    

            self.all.draw(SCREEN)
            pygame.display.flip()
        
        global SCORE 
        SCORE = self.score

# class Deathscreen(object):
#     def __init__(self):

def main():
    pygame.init()
    #pygame.mixer.init() #breaks when user device doesn't have a sound card installed...
    splash = True
    game = True 
    running = True
    
    
    pygame.display.set_caption("SPACE BEHOLDERS")
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    while running:
        if splash: Splashscreen().run()
        splash = False

        if game: Game().run()
        game = False

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == K_ESCAPE:
                    running = False
                else:
                    splash = True
                    game = True
                    
        SCREEN.fill(BLACK)
        GAMEFONT.render_to(SCREEN, (370,300), "Did you die?", RED, None, size=40)
        GAMEFONT.render_to(SCREEN, (350,350), "Final Score: " + str(SCORE), RED, None, size=40) 
        GAMEFONT.render_to(SCREEN, (390,410), "Press 'esc' to quit", RED, None, size=20)
        GAMEFONT.render_to(SCREEN, (340,450), "Press 'any key' to continue", RED, None, size=20)
        pygame.display.flip()

    pygame.quit()

main()