import pygame
import pygame.freetype
import random as rd
import numpy as np
import sys

from pygame.locals import *
from os import path

pygame.init()
pygame.freetype.init()

DEBUG = False
SAFE_MODE = False
FR_TEST_MODE = False

WIDTH, HEIGHT = 1280, 720
SOUND = True
SCORE = 0
HIGHSCORE = 0
GAME_FOLDER = path.dirname(__file__)
RESOURCES_FOLDER = path.join(GAME_FOLDER, "resources")
IMG_FOLDER = path.join(RESOURCES_FOLDER, "images")
SOUND_FOLDER = path.join(RESOURCES_FOLDER, "audio")
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))#, FULLSCREEN)
GAMEFONT = pygame.freetype.Font(path.join(RESOURCES_FOLDER, "Retro Gaming.ttf"), 22)

#Fix no sound card bug in pygame
try:
    pygame.mixer.init()
except:
    SOUND = False
    print("Failed to load audio device!")

class Player_Sprite_sheet:
    def __init__(self):        
        self.image = pygame.image.load(path.join(IMG_FOLDER,"ship_pixel.png")).convert()
        self.size = self.image.get_size()
        self.sheet = pygame.transform.scale(self.image, (int(self.size[0]*4), int(self.size[1]*4)))

    def get_image(self, row, frame):
        image = pygame.Surface((96, 96))
        image.blit(self.sheet, (0,0), ((frame * 96), (row * 96), 96, 96))
        image.set_colorkey((255,255,255))

        return image

class Alien_Sprite_sheet:
    def __init__(self):
        self.image = pygame.image.load(path.join(IMG_FOLDER, "beholder_pixel.png")).convert()
        self.size = self.image.get_size()
        self.sheet = pygame.transform.scale(self.image, (int(self.size[0]*4), int(self.size[1]*4)))

    def get_image(self, row, frame):
        image = pygame.Surface((96, 96))
        image.blit(self.sheet, (0,0), ((frame * 96), (row * 96), 96, 96))
        image.set_colorkey((255,255,255))

        return image

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = [Player_Sprite_sheet().get_image(0,0), Player_Sprite_sheet().get_image(0,1), Player_Sprite_sheet().get_image(0,2), Player_Sprite_sheet().get_image(1,0), Player_Sprite_sheet().get_image(1,1)]
        self.image = self.images[0]
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.radius = 44
        self.rect.center = (WIDTH/2-150, HEIGHT/2+10)
        self.speedx = 0
        self.speedy = 0
        self.health = 196
        self.last_update = pygame.time.get_ticks()
        self._layer = 0
        self.image_index = 0

        self.light_sm = pygame.image.load(path.join(IMG_FOLDER, "light.png")).convert()
        self.light_size = self.light_sm.get_size()
        self.light = pygame.transform.scale(self.light_sm, (self.light_size[0]*2, self.light_size[1]*2))
        self.light_rect = self.light.get_rect()
        self.light.set_colorkey((255,255,255))

    def update_image(self):
        now = pygame.time.get_ticks()
        self.image_index += 1
        
        if self.image_index > 4:
            self.image_index = 0

        if now - self.last_update > 80:
            self.image = self.images[self.image_index]
            self.last_update = now

        SCREEN.blit(self.light, (self.rect.x-WIDTH*2, self.rect.y-HEIGHT*2), special_flags=BLEND_MULT)

    def move(self):
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
        if self.rect.right >= WIDTH:
            self.rect.right = WIDTH
        if self.rect.top <= 5:
            self.rect.top = 5
        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT       
        self.rect.x += self.speedx
        self.rect.y += self.speedy

    def update(self):
        self.update_image()
        self.rect = self.image.get_rect(center=self.rect.center)
        self.move()
        
class Playerdamage(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = [Player_Sprite_sheet().get_image(1,2), Player_Sprite_sheet().get_image(2,0)]
        self.image = self.images[0]
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.timer = 60
        self._layer = 3
    
    def update(self):
        self.timer -= 1

        if self.timer > 0:
            if self.image == self.images[0]:
                self.image = self.images[1]
            elif self.image == self.images[1]:
                self.image = self.images[0]
        else:
            self.kill()

class Particles(pygame.sprite.Sprite):
    def __init__(self, x, y, xspeed, yspeed, color, lifespan):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((rd.randint(1,6),(rd.randint(1,6))))
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
        self._layer = 4

    def update(self):
        self.timer += 1

        self.rect.y += self.yspeed
        self.rect.x += self.xspeed
        if self.rect.y > HEIGHT or self.timer > self.lifespan:
            self.kill()

class Show_Hit_Score(pygame.sprite.Sprite):
    def __init__(self, speedx, speedy, x, y, score):
        pygame.sprite.Sprite.__init__(self)
        self.score = str(int(score))
        self.timeout = 60
        self.image = pygame.Surface((1,1))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedx = speedx
        self.speedy = speedy

    def update(self):
        self.timeout -= 1
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        GAMEFONT.render_to(SCREEN, (self.rect.x, self.rect.y), str(self.score),(0,255,0), size=18)

        if self.timeout <= 0 or self.rect.x > WIDTH or self.rect.x < 0:
            self.kill()

class Player_Shoot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((6,6))
        self.image.fill((0,255,0))
        self.rect = self.image.get_rect()
        self.rect.centery = y
        self.rect.centerx = x
        self.x = float(self.rect.centerx)
        self.y = float(self.rect.centery)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.velx = mouse_x - self.rect.centerx
        self.vely = mouse_y - self.rect.centery
        self.velocity = np.array([self.velx, self.vely])
        self.velocity = 10 * self.velocity / np.linalg.norm(self.velocity)
        self._layer = 1

    def kill_bullet(self):
        if self.rect.bottom < 0:
            self.kill()
        if self.rect.top > HEIGHT:
            self.kill()
        if self.rect.left < 0:
            self.kill()
        if self.rect.right > WIDTH:
            self.kill()

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]  
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)  
        self.kill_bullet()

class Healthpack(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(IMG_FOLDER, "healthpack.png")).convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.speedy = rd.randint(4,10)
        self.rect.y = -100
        self.rect.x = rd.randint(0,WIDTH)
        self._layer = 0

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
        self._layer = 2

class Alien(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for i in range(11):
            self.images.append(Alien_Sprite_sheet().get_image(0,i))
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.death = False
        self.deathtimer = 14
        self.radius = 44
        self.rect.x = rd.randrange(0, WIDTH - self.rect.width)
        self.rect.y = rd.randrange(-340, -140)
        self.speedy = rd.randrange(1, 8)
        self.speedx = rd.randrange(-3, 3)
        self.penalty = 0
        self.last_update = pygame.time.get_ticks()
        self._layer = 0
        
    def update_image(self):
        now = pygame.time.get_ticks()
        if self.death == False:
            if now - self.last_update > 80:
                r = rd.randint(0,8)
                self.image = self.images[r]
                self.last_update = now
        
        if self.death == True:
            self.deathtimer -= 1.5
            if self.deathtimer > 0:
                r = rd.randint(9,10)
                self.image = self.images[r]
            if self.deathtimer <= 0:
                self.kill()
    
    def move(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx

        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speedx = -self.speedx

        if self.rect.top > HEIGHT + 10:
            self.rect.x = rd.randrange(0, WIDTH - self.rect.width)
            self.rect.y = rd.randrange(-600, -300)
            self.speedy = rd.randrange(1, 8)
            self.penalty += (self.speedy*1100)

    def update(self):
        self.update_image()
        self.move()
            
class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x):
        pygame.sprite.Sprite.__init__(self)
        self.images = ["asteroid_lg.png","asteroid_lg2.png","asteroid_md.png","asteroid_sm.png"]  
        self.randomize = rd.randint(0,3)
        self.image = pygame.image.load(path.join(IMG_FOLDER, self.images[self.randomize])).convert()
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
        self._layer = 3
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
        self._layer = 0

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT + 10:
            self.kill()

class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(IMG_FOLDER, "cursor.png")).convert()
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self._layer = 0
    
    def update(self):
        x, y = pygame.mouse.get_pos()
        self.rect.x = x - 35
        self.rect.y = y - 35

class Scene_Fade_In(pygame.sprite.Sprite):
    def __init__(self, timer):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((WIDTH+30,HEIGHT))
        self.image.fill((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH/2
        self.rect.centery = HEIGHT/2
        self.timer = timer
        self._layer = 5

    def update(self):
        self.timer -= 1
        if self.timer > 0:
            self.image.set_alpha(self.timer)
        if self.timer < 0:
            self.kill()

class Scene_Fade_Out(pygame.sprite.Sprite):
    def __init__(self, maxtime):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((WIDTH+20,HEIGHT+20))
        self.image.fill((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH/2
        self.rect.centery = HEIGHT/2
        self.maxtime = maxtime
        self.timer = 0
        self._layer = 5

    def update(self):
        self.timer += 5
        if self.timer < self.maxtime:
            self.image.set_alpha(self.timer)

class Splashscreen(object):
    def __init__(self):
        self.running = True
        self.all = pygame.sprite.LayeredUpdates()
        self.logo = Alien_Sprite_sheet().get_image(0,1)
        self.logo.set_colorkey((255,255,255))
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.fade = pygame.sprite.Group()
        self.fadetimer = 100
        self.setfadeout = False
        self.fadein = Scene_Fade_In(300)
        self.fadeout = Scene_Fade_Out(self.fadetimer)
        self.all.add(self.fadein)
        self.highscore = 0
        self.load_score()
        
        global HIGHSCORE
        HIGHSCORE = self.highscore
 
    def load_score(self):
                try:
                    with open(path.join(GAME_FOLDER, "gamedata.txt"), "r") as f:
                        self.highscore = int(str(f.read()))
                except:
                    with open(path.join(GAME_FOLDER, "gamedata.txt"), "w") as file:
                        file.write(str(0))
                        self.highscore = 0

    def run(self):
        def player_controls():
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == K_ESCAPE:
                            self.running = False
                            Main().run(False)
                    else:
                        if self.setfadeout == False:
                            self.setfadeout = True
                            self.all.add(self.fadeout)
                            pygame.time.set_timer(pygame.KEYDOWN, 0)

        def timed_events():
            self.clock.tick(self.fps)
            if int(self.clock.get_fps()) > 59.0:
                r = rd.randint(5,255)
                self.stars = Particles(rd.randint(0,WIDTH),0,0,rd.randint(5,10),(r,r,r),1000)
                self.all.add(self.stars)

            if self.setfadeout == True:
                self.fadetimer -= 1
            
            if self.fadetimer <= 0:
                self.running = False

        def draw_to_screen():
            SCREEN.fill((0,0,0))
            SCREEN.blit(self.logo, (592, 200))

            self.hs_text = GAMEFONT.render("High Score: " + str(HIGHSCORE), 1, (0,0,0), size=22)
            self.center_text = (WIDTH - self.hs_text[1][2]) / 2
        
            GAMEFONT.render_to(SCREEN, (298,HEIGHT / 2), "SPACE BEHOLDERS", (255,0,0), None, size=64)
            GAMEFONT.render_to(SCREEN, (self.center_text, 450), "High Score: " + str(HIGHSCORE), (255,0,0), size=22)
            GAMEFONT.render_to(SCREEN, (496 , 500), "Press Any Key to Play", (255,0,0), None, size=22)
            GAMEFONT.render_to(SCREEN, (298 , 600), "Use Mouse to aim and shoot, Use keys A,S,D,W to fly", (255,0,0), None, size=22)
            GAMEFONT.render_to(SCREEN, (444, 650), "Press the Spacebar to pause", (255,0,0), None, size=22)
            self.all.update()
            SCREEN.set_alpha(0)
            self.all.draw(SCREEN)

        while self.running:  
                   
            player_controls()
            timed_events()
            draw_to_screen()
            pygame.display.flip()

class End_Game_Screen(object):
    def __init__(self):
        self.running = True
        self.timer = 1200
        self.save_score()

    def save_score(self):
        print(SCORE, HIGHSCORE)
        if SCORE > HIGHSCORE:
            self.highscore = SCORE
            #GAMEFONT.render_to(SCREEN, (495,300), "NEW HIGH SCORE!", (0,255,0), None, size=30)
            print(self.highscore)
            try:
                with open(path.join(GAME_FOLDER, "gamedata.txt"), "w") as f:
                    f.write(str(self.highscore))
            except:
                print ("I/O Error: Score not saved!")

    def run(self):
        def timed_events():
            if self.timer > 0:
                self.timer -= 1

        def get_user_input():
            if self.timer <= 0:
                for e in pygame.event.get():
                        if e.type == pygame.KEYDOWN:
                            self.running = False
                            pygame.time.set_timer(pygame.KEYDOWN, 0)

                        if e.type == pygame.KEYDOWN:
                            if e.key == K_ESCAPE:
                                self.running = False
                                Main().run(False)

        def draw_to_screen():
            SCREEN.fill((0,0,0))
            if SCORE > HIGHSCORE:
                GAMEFONT.render_to(SCREEN, (419,250), "NEW HIGH SCORE!", (0,255,0), None, size=40)    
            GAMEFONT.render_to(SCREEN, (495,300), "GAME OVER", (255,0,0), None, size=40)
            GAMEFONT.render_to(SCREEN, (540,370), "Score: " + str(SCORE) + "!", (255,0,0), None, size=20)

            if self.timer <= 0:
                GAMEFONT.render_to(SCREEN, (505,410), "Press 'esc' to quit", (255,0,0), None, size=20)
                GAMEFONT.render_to(SCREEN, (455,450), "Press 'any key' to continue", (255,0,0), None, size=20)

        while self.running:
            timed_events()
            get_user_input()
            draw_to_screen()
            pygame.display.flip()  

class Gameplay(object):
    def __init__(self):
        self.running = True
        self.score = 0
        self.random = 0
        self.score_display = 0
        self.level = 4
        self.timer = 0
        self.accuracy = [1,1]
        self.acccalc = 300
        self.pause = False
        self.start_timer = 5.0
        self.fadein_delay = True
        self.fadeout = 50
        self.start = True
        self.die = False
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.all = pygame.sprite.LayeredUpdates()
        self.fx = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.powerup = pygame.sprite.Group()
        self.fade = pygame.sprite.Group()
        self.player = Player()
        self.cursor = Cursor()
        self.healthbar = Healthbar([5,5])
        self.shooting = False
        self.bullet_timer = 0.5
        self.fadein = Scene_Fade_In(300)      
        self.fade.add(self.fadein)
        self.all.add(self.player, self.cursor, self.fadein)
        self.all.add()

    def run(self):

        def timed_events():
            self.clock.tick(self.fps)

            if self.timer < 0.0:
                self.timer = 20.00

            if self.fadein_delay == True:
                self.timer = 20.01
           
            if len(self.fade.sprites()) == 0:
                if SAFE_MODE:
                    self.fadein_delay = True
                else:
                    self.fadein_delay = False

        def create_enemies():
            if self.start == True and self.fadein_delay == False:
                for _ in range(self.level):
                    enemy = Alien()
                    self.all.add(enemy)
                    self.enemies.add(enemy)
                self.start = False
            
            if FR_TEST_MODE:
                if int(self.clock.get_fps()) > 59: 
                    enemy = Alien()
                    self.all.add(enemy)
                    self.enemies.add(enemy)

        def create_asteroid():
            if self.fadein_delay == False and self.timer > 5.0 and self.random > 9950:
                self.asteroid = Asteroid(self.player.rect.centerx)
                self.asteroids.add(self.asteroid)
                self.all.add(self.asteroid)

        def create_healthpack():
            if self.fadein_delay == False and self.random > (10003 - self.level):
                self.healthpack = Healthpack()
                self.powerup.add(self.healthpack)
                self.all.add(self.healthpack)

        def create_particles():
            self.random = rd.randint(1,10000)

            if self.random > 8000:
                self.exhaust = Particles((self.player.rect.centerx+rd.randint(-25,+25)), (self.player.rect.centery+25), 0, rd.randint(5,10), (255, 165, 0), rd.randint(25,100)) #Orange
                self.fx.add(self.exhaust)
                self.all.add(self.exhaust)
         
            if int(self.clock.get_fps()) > 59:
                r = rd.randint(5,255)
                self.stars = Particles(rd.randint(0,WIDTH),0,0,rd.randint(5,10),(r,r,r),1000)
                self.all.add(self.stars)

        def player_controls():
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == K_ESCAPE:
                        self.running = False

                if e.type == pygame.MOUSEBUTTONDOWN:
                    self.bullet_timer = 0
                    self.shooting = True
                
                if e.type == pygame.MOUSEBUTTONUP:
                    self.shooting = False

                if e.type == pygame.KEYDOWN:
                    if e.key == K_SPACE:
                        self.pause = True
                        GAMEFONT.render_to(SCREEN, (400,300), "PAUSED", (255,0,0), None, size=40)
                        pygame.display.flip()
                        while self.pause:
                            for e in pygame.event.get():
                                if e.type == pygame.KEYDOWN:
                                    self.pause = False

        def player_shoot():
            self.bullet_timer -= 0.025
            self.timer = round(self.timer - .01, 2)
            
            if self.shooting:
                if self.bullet_timer <= 0:
                    self.bullet_timer = 0.5
                    self.bullet = Player_Shoot(self.player.rect.centerx, self.player.rect.centery)
                    self.all.add(self.bullet)
                    self.bullets.add(self.bullet)
                    if SOUND: 
                        pygame.mixer.Channel(0).play(pygame.mixer.Sound(path.join(SOUND_FOLDER, "shoot.ogg")))
                    self.accuracy[1] += 1

        def lose_game():
            if self.player.health <= 0:
                self.fadeout -= 1
                if self.die == False:
                    self.fadeout_display = Scene_Fade_Out(300)
                    self.all.add(self.fadeout_display)
                    self.die = True
                    self.fps = 10
                    self.player.kill()

                if self.fadeout <= 0:
                    self.running = 0

            if self.accuracy[1] != 0:
                self.acccalc = self.accuracy[0] * 1.0 / self.accuracy[1]*100
        
        def go_to_next_level():
            if self.timer == 0:
                levelup = True
                newlevel = self.level + 1
                while levelup:
                    if self.level != newlevel:
                        self.level += 1
                        for _ in range(self.level*2):
                            m = Alien()
                            self.all.add(m)
                            self.enemies.add(m)
                    
                    levelup = False                
                    pygame.display.flip()
        
        def calculate_score():
            for sprite in self.enemies:
                if sprite.penalty > 0:
                    self.score_display -= int(sprite.penalty*0.10)
                    sprite.penalty -= int(sprite.penalty*0.10)

            transferscore = int(self.score*0.1)

            if self.score > 0:
                self.score -= transferscore
                self.score_display += transferscore
                
        def player_shoot_enemy():
                enemy_hit_by_bullet = pygame.sprite.groupcollide(self.bullets, self.enemies, False, False)
                for sprite in enemy_hit_by_bullet:
                    bulletx = sprite.rect.x
                    bullety = sprite.rect.y
                    bulletvely = sprite.velocity[1]
                    enemy_gets_shot(bulletx, bullety, bulletvely)
        
        def enemy_gets_shot(bulletx, bullety, bulletvely):
            player_shoot_enemy = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
            for sprite in player_shoot_enemy:
                if SOUND: 
                    pygame.mixer.Channel(1).play(pygame.mixer.Sound(path.join(SOUND_FOLDER, "explosion.ogg")))
                r = rd.randint(3,6)
                for _ in range(r):
                    laser = Particles(bulletx, bullety, rd.randint(-5,5), rd.randint(-2,2) + bulletvely + sprite.speedy, (0,rd.randint(100,255),0), rd.randint(25,100))
                    blood = Particles(bulletx, bullety, rd.randint(-5,5), rd.randint(-1,1) + sprite.speedy, (rd.randint(100,255),0,0), rd.randint(25,100))
                    purplegoo = Particles(bulletx, bullety, rd.randint(-5,5), rd.randint(-1,1) + sprite.speedy, (147,112,219), rd.randint(25,100))
                    self.all.add(laser, blood, purplegoo)

                if sprite.death == False:
                    self.accuracy[0] += 1
                    mod = 0
                    if sprite.speedx == 0 or sprite.speedy == 0:
                        mod = 1
                    self.score += abs(15* (sprite.speedx+mod) * (sprite.speedy+mod) * self.acccalc)

                    if sprite.rect.y > 0:
                        show_hit = Show_Hit_Score(sprite.speedx, sprite.speedy, sprite.rect.x+15, sprite.rect.y+15, (self.score-9))
                        self.all.add(show_hit)
                        
                    if self.timer > 5.0 and len(self.enemies) <= self.level*2:
                        m = Alien()
                        self.all.add(m)
                        self.enemies.add(m)
                
                sprite.death = True
        
        def player_shoot_asteroid():
            player_shoot_asteroid = pygame.sprite.groupcollide(self.bullets, self.asteroids, True, False)
            for sprite in player_shoot_asteroid:
                x = sprite.rect.x  
                y = sprite.rect.y
                r = rd.randint(3,6)
                for i in range(r):
                    laser_particles = Particles(x, y, rd.randint(-5,5), rd.randint(-5,5), (0,(rd.randint(100,255)),0), rd.randint(25,100))
                    rock_particles = Particles(x, y, rd.randint(-5,5), rd.randint(-5,5), (220,220,220), rd.randint(25,100))
                    self.all.add(laser_particles, rock_particles)
        
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
                    d = Playerdamage(self.player.rect.x, self.player.rect.y)

                    self.all.add(d)
        
        def player_enemy_collide():
            player_enemy_collide = pygame.sprite.spritecollide(self.player, self.enemies, False, pygame.sprite.collide_circle)
            if player_enemy_collide:
                if FR_TEST_MODE == False:
                    self.player.health -= rd.randint(5,10)
            
            for sprite in player_enemy_collide:
                if dict[sprite]:
                    d = Playerdamage(self.player.rect.x, self.player.rect.y)

                    self.all.add(d)
        
        def draw_to_screen():
            SCREEN.fill((0,0,0))
            self.all.draw(SCREEN)

        def hud_display():
            SCREEN.blit(self.healthbar.image,(25,5))
            for i in range(self.player.health):
                SCREEN.blit(self.healthbar.health, (i+28,8))

            GAMEFONT.render_to(SCREEN, (1150,10), "'Esc' to Quit", (255,255,255), None, size=12)
            GAMEFONT.render_to(SCREEN, (35,30), "Score: " + str(self.score_display), (255,255,255), None, size=25)            
            GAMEFONT.render_to(SCREEN, (35,60), "Level: " + str(self.level - 3), (255,255,255), None, size=25)       
            if self.timer < 3.0:
                GAMEFONT.render_to(SCREEN, (470,300), "Next Wave In " + str(int(self.timer)), (255,255,255), None, size=27)

            if DEBUG:
                GAMEFONT.render_to(SCREEN, (10,550), "DEBUG MODE ON", (255,0,0), None, size=18)
                GAMEFONT.render_to(SCREEN, (10,600), str(self.clock), (255,0,0), None, size=18)
                GAMEFONT.render_to(SCREEN, (10,625), "Enemies: " + str(len(self.enemies)), (255,0,0), None, size=18)
                GAMEFONT.render_to(SCREEN, (10,650), "Round: " + str(self.timer), (255,0,0), None, size=18) 
                GAMEFONT.render_to(SCREEN, (10,675), "Accuracy: " + str(round(self.acccalc, 2)) + "%", (255,0,0), None, size=18)

        while self.running:       
            timed_events()
            create_enemies()
            create_asteroid()
            create_healthpack()
            create_particles()
            player_controls()
            player_shoot()
            player_shoot_enemy()
            player_shoot_asteroid()
            player_health_pickup()
            player_asteroid_collide()
            player_enemy_collide()
            lose_game()
            go_to_next_level()  
            calculate_score()
            draw_to_screen()            
            self.all.update()
            hud_display()
            pygame.display.flip()                

        global SCORE
        SCORE = self.score_display
        return SCORE

class Main(object):
    def __init__(self):
        pygame.display.set_caption("SPACE BEHOLDERS")
        pygame.mouse.set_visible(False)

        # disallow the sharing of input devices with other applications
        pygame.event.set_grab(True)
        
        # if SOUND: 
        #     pygame.mixer.music.load(path.join(SOUND_FOLDER,"space track.ogg"))
        #     pygame.mixer.music.play(loops = -1)
  
    def run(self, running):
        while running:
            Splashscreen().run() 
            Gameplay().run() 
            End_Game_Screen().run()
    
        pygame.quit()
        sys.exit(0)

Main().run(True)