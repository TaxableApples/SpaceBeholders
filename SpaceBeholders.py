import pygame
import pygame.freetype
import random as rd
import numpy as np
import sys

from pygame.locals import *
from os import path
pygame.init()
pygame.freetype.init()
WIDTH, HEIGHT = 1280, 720
SOUND = True
SCORE = 0
HIGHSCORE = 0
GAME_FOLDER = path.dirname(__file__)
RESOURCES_FOLDER = path.join(GAME_FOLDER, "resources")
IMG_FOLDER = path.join(RESOURCES_FOLDER, "images")
SOUND_FOLDER = path.join(RESOURCES_FOLDER, "audio")
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), 32) #FULLSCREEN | DOUBLEBUF, 
GAMEFONT = pygame.freetype.Font(path.join(RESOURCES_FOLDER, "Retro Gaming.ttf"), 22)

#Fix no sound card bug in pygame
try:
    pygame.mixer.init()
except:
    SOUND = False
    print("Failed to load audio device!")

class Read_Sprite_sheet():
    def __init__(self, image, height, width):        
        self.image = pygame.image.load(path.join(IMG_FOLDER,image)).convert()
        self.size = self.image.get_size()
        self.sheet = pygame.transform.scale(self.image, (int(self.size[0]*3), int(self.size[1]*3)))
        self.height = height
        self.width = width

    def get_image(self, row, frame):
        image = pygame.Surface((self.height, self.width))
        image.blit(self.sheet, (0,0), ((frame * self.height), (row * self.width), self.height, self.width))
        image.set_colorkey((255,255,255))

        return image

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = [[], [], [], []]
        for i in range(4):
            for j in range(4):
                self.images[j].append(Read_Sprite_sheet("ship_pixel.png", 72, 48).get_image(j,i))
        self.image = self.images[0][0]
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.radius = 44
        self.rect.center = (WIDTH/2-150, HEIGHT/2+10)
        self.speedx = 0
        self.speedy = 0
        self.health = 196
        self.damage = 0
        self.last_update = pygame.time.get_ticks()
        self._layer = 0
        self.image_index = 0
        self.image_row = 0
        self.hit = False
        self.hit_timer = 0
        self.shooting = False
        self.damage_mod = 0

        self.light_sm = pygame.image.load(path.join(IMG_FOLDER, "light.png")).convert()
        self.light_size = self.light_sm.get_size()
        self.light = pygame.transform.scale(self.light_sm, (self.light_size[0]*2, self.light_size[1]*2))
        self.light_rect = self.light.get_rect()
        self.light.set_colorkey((255,255,255))
        self.left_turn = False
        self.right_turn = False

    def update_image(self):
        now = pygame.time.get_ticks()
        self.image_index += 1
        if self.image_index >= 3:
            self.image_index = 0

        if self.speedx > 4:
            self.image_row = 1

        elif self.speedx < -4:
            self.image_row = 2
        else:
            self.image_row = 0

        if self.hit_timer > 0:
            self.image_row = 3

        if now - self.last_update > 80:
            self.image = self.images[self.image_row][self.image_index]
            self.last_update = now
            
        SCREEN.blit(self.light, (self.rect.x-WIDTH*2, self.rect.y-HEIGHT*2), special_flags=BLEND_MULT)

    def take_damage(self):
        if self.damage > 0 or self.damage_mod > 0:
            self.health-=self.damage
            self.health-=self.damage_mod
            self.damage_mod-=self.damage_mod
            self.damage-=self.damage
            self.hit_timer = 20

        if self.hit_timer > 0:
            self.hit_timer -= 1

    def move(self):
        if self.speedx > 0:
            self.speedx -= .16
        if self.speedx < 0:
            self.speedx += .16
        if self.speedy > 0:
            self.speedy -= .16
        if self.speedy < 0:
            self.speedy += .16
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a]:
            self.speedx = -10
        if keystate[pygame.K_d]:
            self.speedx = 10
        if keystate[pygame.K_w]:
            self.speedy = -10
        if keystate[pygame.K_s]:
            self.speedy = 10

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
        self.take_damage()
        self.rect = self.image.get_rect(center=self.rect.center)
        self.move()
        
class Particles(pygame.sprite.Sprite):
    def __init__(self, x, y, xspeed, yspeed, color, lifespan):
        pygame.sprite.Sprite.__init__(self)
        self.r=rd.randint(1,6)
        self.image = pygame.Surface((self.r,self.r))

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
        
        if self.timer > self.lifespan:
            self.kill()

        if self.rect.y > HEIGHT or self.rect.y < 0:
            self.kill()

        if self.rect.x < 0 or self.rect.x > WIDTH:
            self.kill()

class Show_Hit_Score(pygame.sprite.Sprite):
    def __init__(self, speedx, speedy, x, y, score):
        pygame.sprite.Sprite.__init__(self)
        self.score = str(int(score-9))
        self.timeout = 30
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

class Shoot(pygame.sprite.Sprite):
    def __init__(self, x, y, mouse_x, mouse_y, bullet_color, glow_color):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((6,6))
        self.glow_seed = pygame.Surface((26,26))
        self.image.fill((bullet_color))
        self.rect = self.image.get_rect()
        self.rect.centery = y
        self.rect.centerx = x
        self.x = float(self.rect.centerx)
        self.y = float(self.rect.centery)
        self.velx = mouse_x - self.rect.centerx
        self.vely = mouse_y - self.rect.centery
        self.velocity = np.array([self.velx, self.vely])
        self.velocity = 20 * self.velocity / np.linalg.norm(self.velocity)
        self._layer = 0
        self.glow = pygame.draw.circle(self.glow_seed, glow_color, (13, 13), 12)

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
        SCREEN.blit(self.glow_seed, (self.rect.x-11, self.rect.y-11), special_flags=BLEND_RGB_ADD)
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
        self.glow_seed = pygame.Surface((44,44))
        self.glow = pygame.draw.circle(self.glow_seed, (0,40,0), (22, 22), 22)
        self.rect = self.image.get_rect()
        self.speedy = rd.randint(8,20)
        self.rect.y = -100
        self.rect.x = rd.randint(0,WIDTH)
        self._layer = 0

    def update(self):
        SCREEN.blit(self.glow_seed, (self.rect.x-4, self.rect.y-4), special_flags=BLEND_RGB_ADD)
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

class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, image_range, height, width, speedx ,speedy, hitpoints, bonus):
        pygame.sprite.Sprite.__init__(self)
        self.images=[[],[]]
        for i in range(image_range):
            for j in range(2):
                self.images[j].append(Read_Sprite_sheet(image, height, width).get_image(j,i))
        self.image = self.images[0][0]
        self.frame = 0
        self.rect = self.image.get_rect()
        self.rect.x = rd.randrange(0, WIDTH - self.rect.width)
        self.rect.y = rd.randrange(-340, -140)
        self.speedy = speedy
        self.speedx = speedx
        self.last_update = pygame.time.get_ticks()
        self.hit = False
        self.death = False
        self.shooting = False
        self.hp = hitpoints;
        self.hit_timer = 15
        self.penalty = 0
        self.score = 0
        self.bonus = bonus
        self.image_range = image_range-1
        self.image_row = 0
        self.mod = 0
        self.damage = 0
        self.damage_mod = 1
        
    def take_damage(self):
        if self.damage > 0:
            self.hp-=self.damage
            self.damage-=self.damage
            self.hit_timer = 8

        if self.hit_timer > 0:
            self.hit_timer -= 1
            self.image_row = 1
        else:
            self.image_row = 0

        if self.hp <= 0:
            if self.speedx == 0 or self.speedy == 0:
                self.mod = 1
            self.score += abs(1553 * (self.speedx + self.mod) * (self.speedy + self.mod) + self.bonus) * self.damage_mod
            
            if self.hit_timer <= 0:
                self.kill()

    def shoot(self):
        r = rd.randint(1,10000)

        if r > 9600:
            self.shooting = True
        else:
            self.shooting = False

    def update_image(self):
        now = pygame.time.get_ticks()

        if now - self.last_update > 40:
            if self.frame >= self.image_range:
                self.frame = 0
            self.frame +=1
            self.last_update = now

        self.image = self.images[self.image_row][self.frame]
        
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

        if self.rect.top > HEIGHT + 10 and self.penalty <=0:
            self.kill()

    def update(self):
        self.update_image()
        self.take_damage()
        self.shoot()
        self.move()

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x):
        pygame.sprite.Sprite.__init__(self)
        self.images = ["asteroid_lg.png","asteroid_lg2.png","asteroid_md.png","asteroid_sm.png"]  
        self.randomize = rd.randint(0,3)
        self.image = pygame.image.load(path.join(IMG_FOLDER, self.images[self.randomize])).convert()
        self.size = self.image.get_size()
        self.upsize = pygame.transform.scale(self.image, (int(self.size[0]*3), int(self.size[1]*3)))
        self.image = self.upsize
        self.image.set_colorkey((255,255,255))
        self.rect = self.image.get_rect()
        self.radius = 44
        self.rect.y = -100
        self.rect.x = x
        self.speedy = rd.randrange(2, 16)
        self.last_update = pygame.time.get_ticks()
        self.random = rd.randint(1, 20)
        self._layer = 3
        self.damage_mod = 0
        self.damage = 0
        self.hit = False

        if self.random > 18:
            self.rect.x = x
        else:
            self.rect.x = rd.randint(0, WIDTH)

    def update(self):
        self.rect.y += self.speedy
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
        self.logo = Read_Sprite_sheet("Beholder.png", 75, 84).get_image(0,1)
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
            if int(self.clock.get_fps()) > 29:
                starseed = rd.randint(5,255)
                self.stars = Particles(rd.randint(0,WIDTH),0,0,rd.randint(5,10),(starseed,starseed,rd.randint(5,255)),500)
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
        
            GAMEFONT.render_to(SCREEN, (287,HEIGHT / 2), "SPACE BEHOLDERS", (255,0,0), None, size=64)
            GAMEFONT.render_to(SCREEN, (self.center_text, 450), "High Score: " + str(HIGHSCORE), (255,255,255), size=22)
            GAMEFONT.render_to(SCREEN, (513 , 600), "Press Any Key to Play", (255,0,0), None, size=18)
            GAMEFONT.render_to(SCREEN, (391 , 630), "Use Mouse to aim and shoot, Use keys A,S,D,W to fly", (255,0,0), None, size=16)
            GAMEFONT.render_to(SCREEN, (495, 658), "Press the Spacebar to pause", (255,0,0), None, size=16)
            GAMEFONT.render_to(SCREEN, (1150,10), "'Esc' to Quit", (255,255,255), None, size=16)
            self.all.update()
            SCREEN.set_alpha(0)
            self.all.draw(SCREEN)

        while self.running:                  
            player_controls()
            timed_events()
            draw_to_screen()
            pygame.display.flip()

class Gameplay(object):
    def __init__(self):
        self.running = True
        self.score = 0
        self.scorebank = 0
        self.score_display = 0
        self.level = 1
        self.levelup = False
        self.die = False
        self.timer = 2000
        self.pause = False
        self.fadein_delay = True
        self.fadeout = 50
        self.fps = 30
        self.hp_pool = 0
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        self.clock = pygame.time.Clock()
        self.all = pygame.sprite.LayeredUpdates()
        self.fx = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.enemyships = pygame.sprite.Group()
        self.all_enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.powerup = pygame.sprite.Group()
        self.fade = pygame.sprite.Group()
        self.enemybullet = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.player = Player()
        self.cursor = Cursor()
        self.healthbar = Healthbar([5,5])
        self.bullet_timer = 0.5
        self.fadein = Scene_Fade_In(300)      
        self.fade.add(self.fadein)
        self.all.add(self.player, self.cursor, self.fadein)
        self.players.add(self.player)

    def run(self):
        
        WHITE, RED, PURPLE, GREEN, GREY, ORANGE, RED_GLOW, GREEN_GLOW = (255,255,255), (255,0,0), (147,112,219), (0,255,0), (100,100,100), (255, 165, 0), (40,0,0), (0,40,0)
        ZEROSCORE, ALLOWSCORE = 0, 1
        B_FRAMELIMIT, B_WIDTH, B_HEIGHT, BEHOLDER_HP = 9, 75, 84, 15
        S_FRAMELIMIT, S_WIDTH, S_HEIGHT, ENEMYSHIP_HP = 4, 84,84, 45

        def game_time():
            self.clock.tick(self.fps)

            self.timer -=1

            if self.timer <= 0:
                self.timer = 1000
                self.level += 1

            if self.fadein_delay == True:
                self.timer = 500

            #start the clock when the fade in dies...
            if len(self.fade.sprites()) == 0:
                self.fadein_delay = False

        def spawn(thing, spawn_limit, sprite_group, isenemy):
            if self.fadein_delay == False:

                if (len(sprite_group) > 20 + self.level * 2):
                    return

                self.random = rd.randint(1,10000)
                if self.random >= spawn_limit:
                    self.all.add(thing)
                    sprite_group.add(thing)

                    if isenemy == True:
                        self.all_enemies.add(thing)

        def player_controls():
            self.mouse_x, self.mouse_y = pygame.mouse.get_pos()

            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == K_ESCAPE:
                        self.running = False

                if e.type == pygame.MOUSEBUTTONDOWN:
                    self.bullet_timer = 0
                    self.player.shooting = True
                
                if e.type == pygame.MOUSEBUTTONUP:
                    self.player.shooting = False

                if e.type == pygame.KEYDOWN:
                    if e.key == K_SPACE:
                        self.pause = True
                        GAMEFONT.render_to(SCREEN, (400,300), "PAUSED", (255,0,0), None, size=40)
                        pygame.display.flip()
                        while self.pause:
                            for e in pygame.event.get():
                                if e.type == pygame.KEYDOWN:
                                    self.pause = False
                
        def shooting(sprites, target_x, target_y, color, glow, group):
            self.bullet_timer -= 0.025

            for sprite in sprites:
                if sprite.shooting:
                    if self.bullet_timer <= 0:
                        self.bullet_timer = 1
                        
                        bullet = Shoot(sprite.rect.centerx, sprite.rect.centery, target_x, target_y, color, glow)
                        self.all.add(bullet)
                        group.add(bullet)

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
      
        def bullet_collide(sprite_a, sprite_b, color_a, color_b, color_c, mod):
                bullet_hit = pygame.sprite.groupcollide(sprite_a, sprite_b, False, False)
                for bullet in bullet_hit:
                    bulletx = bullet.rect.x
                    bullety = bullet.rect.y
                    bulletvely = bullet.velocity[1]

                    explosion = pygame.sprite.groupcollide(sprite_b, sprite_a, False, True)
                    for sprite in explosion:
                        r = rd.randint(3,6)
                        for _ in range(r):
                            a = Particles(bulletx, bullety, rd.randint(-5,5), rd.randint(-2,2) + bulletvely + sprite.speedy, color_a, rd.randint(25,100))
                            b = Particles(bulletx, bullety, rd.randint(-5,5), rd.randint(-1,1) + sprite.speedy, color_b, rd.randint(25,100))
                            c = Particles(bulletx, bullety, rd.randint(-5,5), rd.randint(-1,1) + sprite.speedy, color_c, rd.randint(25,100))
                            self.all.add(a, b, c)

                        if sprite.hit == False:
                            sprite.hit = True

                        sprite.damage_mod = mod
                        sprite.damage += 15

        def player_health_pickup():
            player_health_pickup = pygame.sprite.spritecollide(self.player, self.powerup, True, pygame.sprite.collide_circle)
            if player_health_pickup and self.die == False:
                self.hp_pool = 196
                
            if self.hp_pool > 0 and self.player.health < 196:
                self.hp_pool -= 1
                self.player.health += 1

            if self.player.health >= 196:
                self.hp_pool = 0

        def player_collide(sprite, health):
            collision = pygame.sprite.spritecollide(self.player, sprite, False, pygame.sprite.collide_mask)

            if collision:
                self.player.hit = True
                self.player.damage += health

        def draw_to_screen():
            SCREEN.fill((0,0,0))
            self.all.draw(SCREEN)
        
        def calculate_score():
            for sprite in self.all_enemies:
                if sprite.penalty > 0:
                    self.score_display -= int(sprite.penalty*0.10)
                    sprite.penalty -= int(sprite.penalty*0.10)-9

                if sprite.score > 0 and sprite.death == False:
                    self.scorebank += sprite.score
                    sprite.death = True
                    if sprite.rect.y > 0 and sprite.rect.y < HEIGHT:
                        hit = Show_Hit_Score(sprite.speedx, sprite.speedy, sprite.rect.x, sprite.rect.y, sprite.score)
                        self.all.add(hit)

            if self.scorebank > 0:
                self.score_display += int(self.scorebank*0.10)
                self.scorebank -= int(self.scorebank*0.10)

                if self.scorebank == 9:
                    self.scorebank = 0
        
        def hud_display():
            SCREEN.blit(self.healthbar.image,(25,5))
            for i in range(self.player.health):
                SCREEN.blit(self.healthbar.health, (i+28,8))

            GAMEFONT.render_to(SCREEN, (1150,10), "'Esc' to Quit", (255,255,255), None, size=12)
            GAMEFONT.render_to(SCREEN, (35,30), "Score: " + str(self.score_display), (255,255,255), None, size=25)            
            GAMEFONT.render_to(SCREEN, (35,60), "Level: " + str(self.level), (255,255,255), None, size=25)       

            if self.timer <= 100:
                GAMEFONT.render_to(SCREEN, (470,300), "Level " + str(self.level+1), (rd.randint(10,255),rd.randint(10,255),rd.randint(10,255)), None, size=48)

        while self.running:
            exhaust_x, exhaust_y, exhaust_speed_x, exhaust_speed_y = (self.player.rect.centerx+rd.randint(-25,+25)), (self.player.rect.centery+25), 0, rd.randint(5,10)
            starseed = rd.randint(5,255)
            star_color = (starseed,starseed,rd.randint(5,255))
            lifespan = 50
            standard_damage = rd.randint(5,10)
            high_damage = rd.randint(7,15)
            common = (9700-self.level*100)
            uncommon = (9990-self.level*10)
            rare = (10000-self.level)

            beholder = Enemy("beholder.png", B_FRAMELIMIT, B_WIDTH, B_HEIGHT, rd.randint(-6,6), rd.randint(2,16), BEHOLDER_HP, ZEROSCORE)
            enemyship = Enemy("enemy_ship.png", S_FRAMELIMIT, S_WIDTH, S_HEIGHT, rd.randint(-6,6), rd.randint(1,2), ENEMYSHIP_HP, 10000)
            asteroid = Asteroid(self.player.rect.centerx)
            exhaust = Particles(exhaust_x, exhaust_y, exhaust_speed_x, exhaust_speed_y, ORANGE, lifespan)
            star = Particles(rd.randint(0,WIDTH), 0, 0, rd.randint(10,20), star_color, lifespan)

            game_time()
            player_controls()

            shooting(self.players, self.mouse_x, self.mouse_y, GREEN, GREEN_GLOW, self.bullets)
            shooting(self.enemyships, self.player.rect.centerx, self.player.rect.centery, RED, RED_GLOW, self.enemybullet)

            bullet_collide(self.bullets, self.enemies, GREEN, RED, PURPLE, ALLOWSCORE)
            bullet_collide(self.bullets, self.enemyships, GREEN, RED, GREY, ALLOWSCORE)
            bullet_collide(self.bullets, self.asteroids, GREEN, WHITE, GREY, ZEROSCORE)
            bullet_collide(self.enemybullet, self.players, RED, RED, GREY, ALLOWSCORE)
            bullet_collide(self.enemybullet, self.asteroids, RED, WHITE, GREY, ZEROSCORE)
            bullet_collide(self.enemybullet, self.enemies, RED, RED, PURPLE, ZEROSCORE)

            player_collide(self.enemies, standard_damage)
            player_collide(self.enemyships, standard_damage)
            player_collide(self.asteroids, high_damage)

            player_health_pickup()

            spawn(beholder, common, self.enemies, True)
            spawn(enemyship, uncommon, self.enemyships, True)
            spawn(asteroid, uncommon, self.asteroids, False)
            spawn(Healthpack(), rare, self.powerup, False) 
            spawn(exhaust, common, self.fx, False)
            spawn(star, 1, self.fx, False)    

            for sprite in self.powerup:
                greenpower = Particles((sprite.rect.x + rd.randint(0,20)), sprite.rect.y, 0, sprite.speedy-rd.randint(1,3), GREEN, lifespan)
                spawn(greenpower, 0, self.fx, False)

            lose_game() 
            calculate_score()

            draw_to_screen()            
            self.all.update()
            hud_display()
            pygame.display.flip()

        global SCORE
        SCORE = self.score_display
        return SCORE

class End_Game_Screen(object):
    def __init__(self):
        self.running = True
        self.timer = 1200
        self.save_score()

    def save_score(self):
        if SCORE > HIGHSCORE:
            self.highscore = SCORE
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
            self.hs_text = GAMEFONT.render("Score: " + str(SCORE), 1, (0,0,0), size=20)
            self.center_text = (WIDTH - self.hs_text[1][2]) / 2

            if SCORE > HIGHSCORE:
                GAMEFONT.render_to(SCREEN, (434,250), "NEW HIGH SCORE!", (0,255,0), None, size=40)    
            GAMEFONT.render_to(SCREEN, (510,300), "GAME OVER", (255,0,0), None, size=40)
            GAMEFONT.render_to(SCREEN, (self.center_text,370), "Score: " + str(SCORE), (255,0,0), None, size=20)

            if self.timer <= 0:
                GAMEFONT.render_to(SCREEN, (521,410), "Press 'esc' to quit", (255,0,0), None, size=20)
                GAMEFONT.render_to(SCREEN, (463,450), "Press 'any key' to continue", (255,0,0), None, size=20)

        while self.running:
            timed_events()
            get_user_input()
            draw_to_screen()
            pygame.display.flip()  

class Main(object):
    def __init__(self):
        pygame.display.set_caption("SPACE BEHOLDERS")
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP])
        
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