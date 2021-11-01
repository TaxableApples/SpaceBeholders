import pygame
import pygame.freetype
from pygame.locals import *
import random as rd
import math
import numpy as np
from os import path

WIDTH, HEIGHT = 1024, 768
FPS = 60
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
YELLOW = (255, 255, 0)

SPAWN = pygame.USEREVENT + 1
PENALTY = [0]
GAME = True
LEVEL = 4
DEBUG = True
RUNNING = 1

game_folder = path.dirname(__file__)
resources_folder = path.join(game_folder, "resources")
img_folder = path.join(resources_folder, "images")

# initialize pygame and make a window
pygame.init()
#pygame.mixer.init()
pygame.freetype.init();
pygame.display.set_caption("SPACE BEHOLDERS")
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

gamefont = pygame.freetype.Font(path.join(resources_folder, "AlloyInk.ttf"), 22)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
#gameover = pygame.image.load(path.join(img_folder, "gameover.png"))
#youwin = pygame.image.load(path.join(img_folder, "youwin.png"))



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
            PENALTY.append(self.penalty)
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

splash = True

class Splashscreen(object):
    def __init__(self):
        self.running = True

    def run(self):
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    self.running = False
                    pygame.time.set_timer(pygame.KEYDOWN, 0)
                    print(self.running)

            screen.fill(0)
            gamefont.render_to(screen, (210 ,HEIGHT / 2), "SPACE BEHOLDERS", RED, None, size=64)
            gamefont.render_to(screen, (370 , 500), "Press Any Key to Play", RED, None, size=22)
            gamefont.render_to(screen, (190 , 600), "Use Mouse to aim and shoot, Use keys A,S,D,W to fly", RED, None, size=22)
            pygame.display.flip()


class Game(object):
    def __init__(self):
        self.running = True
        self.score = 0
        self.deaths = -1
        self.level = 4
        self.timer = 20.00

        self.clock = pygame.time.Clock()
        self.all = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        self.space = Background("space.png", [0,0])
        self.player = Player("ship.png")
        self.cursor = Cursor("cursor.png")
        self.healthbar = Healthbar("healthbar.png", "health.png", [5,5])

        self.all.add(self.player)
        self.all.add(self.cursor)

        for _ in range(self.level):
            self.m = Mob("alien.png", "alien2.png")
            self.all.add(self.m)
            self.enemies.add(self.m)

    def restart(self):
        pygame.time.set_timer(SPAWN, 1000 - self.score * 2)

    def run(self):
        while self.running:
            screen.fill(0)
            self.clock.tick(FPS)
            if self.timer < 0.0:
                self.timer = 20.00

            self.timer = round(self.timer - .01, 2)
            #self.timer = round((90000-pygame.time.get_ticks())/1000%60, 1)

            # Control
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == K_ESCAPE:
                        self.running = False

                if e.type == pygame.MOUSEBUTTONDOWN or e.type == pygame.K_m:
                    self.bullet = Bullet(self.player.rect.centerx, self.player.rect.centery, GREEN)
                    self.all.add(self.bullet)
                    self.bullets.add(self.bullet)

            self.all.update()

            # Collisions
            hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
            for _ in hits:
                if self.timer > 5.0 and len(self.enemies) <= self.level:
                    m = Mob("alien.png", "alien2.png")
                    self.all.add(m)
                    self.enemies.add(m)
                    self.score += rd.randint(5,20)

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
                    screen.fill(BLACK)
                    gamefont.render_to(screen, (150,470), "Press Any Key to Continue to the next Level: " + str(self.level - 3), RED, None, size=18)
                    if self.level != newlevel:
                        self.level += 1
                        for _ in range(self.level):
                            m = Mob("alien.png", "alien2.png")
                            self.all.add(m)
                            self.enemies.add(m)
                    
                    for e in pygame.event.get():
                        if e.type == pygame.KEYDOWN:
                            levelup = False
                    pygame.display.flip()
                           
            # Draw
            screen.fill(BLACK)
            screen.blit(self.space.image,self.space.rect)
            screen.blit(self.healthbar.image,(5,5))
            for i in range(self.player.health):
                screen.blit(self.healthbar.health, (i+8,8))

            gamefont.render_to(screen, (875,15), "'Esc' to Quit", RED, None, size=18)
            gamefont.render_to(screen, (500,700), "Score: " + str(self.score), RED, None, size=18)            
            gamefont.render_to(screen, (500,650), "Level: " + str(self.level - 3), RED, None, size=18)
            gamefont.render_to(screen, (500,600), "Round: " + str(self.timer), RED, None, size=18)            
            if self.timer < 3.0:
                gamefont.render_to(screen, (500,300), str(round(self.timer, 0)), RED, None, size=40)
            if DEBUG:
                gamefont.render_to(screen, (700,600), "Enemies: " + str(len(self.enemies)), RED, None, size=18)    

            self.all.draw(screen)
            pygame.display.flip()

while RUNNING:
    if splash: Splashscreen().run()
    splash = False

    if GAME: Game().run()
    GAME = False

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            RUNNING = False
        if e.type == pygame.KEYDOWN:
            if e.key == K_ESCAPE:
                RUNNING = False
            else:
                splash = True
                GAME = True

    screen.fill(BLACK)
    gamefont.render_to(screen, (300,300), "You quit... or died!", RED, None, size=40)
    gamefont.render_to(screen, (270,400), "Press 'esc' to quit or any key to continue", RED, None, size=20)
    pygame.display.flip()

pygame.quit()