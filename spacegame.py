"""
new words:
constructor function,
typecasting


"""

# 1 Import stuff
import pygame
import math
from pygame.locals import *
import random

# 2 init the game
pygame.init()
width, height = 1024, 768
screen = pygame.display.set_mode((width, height))
keys = [False, False, False, False]
playerpos=[500,400]
inc = 0
acc = [0,0]
arrows = []
badtimer=100
badtimer1=0
atimer=100
atimer1=0
badguys=[[1054,100]]
asteroids=[[1050,55]]
healthvalue=194
pygame.mixer.init()
frame=0
framecount=0
angle=0
clock = pygame.time.Clock()

# 3 load images
player = pygame.image.load("resources/images/ship.png")
space = pygame.image.load("resources/images/space.png")
arrow = pygame.image.load("resources/images/bullet.png")
asteroidimg1 = pygame.image.load("resources/images/asteroid.png")
asteroidimg = asteroidimg1 
healthbar = pygame.image.load("resources/images/healthbar.png")
health = pygame.image.load("resources/images/health.png")
badguyimg1 = pygame.image.load("resources/images/alien.png")
badguyimg2 = pygame.image.load("resources/images/alien2.png")
badguyimg = badguyimg1
gameover = pygame.image.load("resources/images/gameover.png")
youwin = pygame.image.load("resources/images/youwin.png")
# 3.1 load audio
#shoot = pygame.mixer.Sound("resources/audio/laser.mp3")
#pygame.mixer.music.load("resources/audio/Nebula.mp3")
#pygame.mixer.music.play(-1, 0.0)
#shoot.set_volume(0.5)
#pygame.mixer.music.set_volume(0.25)

splash = 1
running = 0

# def backdrop():
#   global inc
#   for x in range(width/space.get_width()+1):
#     for y in range(height/space.get_height()+1):
#       inc += .01
#       if inc > 100:
#         inc = 0
#       screen.blit(space,(x*100+inc,y*100+inc)) 

while splash:
  screen.fill(0)
  # backdrop()
  
  font = pygame.font.Font(None, 54)
  splashtext = font.render("SPACE BEHOLDERS", True, (255,0,0))
  screen.blit(splashtext, (screen.get_rect().centerx-165,screen.get_rect().centery))
  font = pygame.font.Font(None, 32)
  splashtext = font.render("press any key to start", True, (255,255,255))
  screen.blit(splashtext, (screen.get_rect().centerx-75,screen.get_rect().centery+50))
  pygame.display.flip()
  
  for event in pygame.event.get():
    if event.type == pygame.KEYDOWN:
      splash = 0
      running = 1
      pygame.time.set_timer(pygame.KEYDOWN, 0)
  
# 4 game loop
exitcode = 0
while running:
  badtimer-=1
  atimer-=1
  # 5 clear the screen
  screen.fill(0)
  # 6 draw the screen elements
  # backdrop()
  
  font = pygame.font.Font(None, 24)
  t = font.render("Controls W = up, S = down, A = left, D = right, aim and shoot with the mouse", True, (255,0,0))
  screen.blit(t, (10,700))
  
  # 6.1 - Draw bullets
  for bullet in arrows:
    index=0
    velx=math.cos(bullet[0])*10
    vely=math.sin(bullet[0])*10
    bullet[1]+=velx
    bullet[2]+=vely
    if bullet[1]<-64 or bullet[1]>1024 or bullet[2]<-64 or bullet[2]>768:
      arrows.pop(index)
    index+=1
    for projectile in arrows:
      arrow1 = pygame.transform.rotate(arrow, 360-projectile[0]*57.29)
      screen.blit(arrow1, (projectile[1], projectile[2]))
  # 6.2 - Set player position and rotation 
  position = pygame.mouse.get_pos()
  angle = math.atan2(position[1]-(playerpos[1]+32),position[0]-(playerpos[0]+26))
  playerrot = pygame.transform.rotate(player, 360-angle*57.29)
  playerpos1 = (playerpos[0]-playerrot.get_rect().width/2, playerpos[1]-playerrot.get_rect().height/2)
  screen.blit(playerrot, playerpos1) 
  
  # 6.2.1 - Draw Asteroids
  if atimer==0:
    asteroids.append([1024, playerpos[1]])
    atimer=325-(atimer1*2)
    if atimer1>=35:
      atimer1=35
    else:
      atimer1+=5
  aindex=0
  for asteroid in asteroids:
    if asteroid[0]<-0:
      asteroids.pop(aindex)
    asteroid[0]-=7
    arect=pygame.Rect(asteroidimg.get_rect())
    arect.top=asteroid[1]
    arect.left=asteroid[0]
    if arect.left<0:
      asteroids.pop(aindex)
      
    prect=pygame.Rect(player.get_rect())
    if prect.colliderect(arect):
      asteroids.pop(aindex)
      
  # 6.3 - Draw Aliens
  if badtimer==0:
    badguys.append([1024, random.randint(50,700)])
    badtimer=100-(badtimer1*2)
    if badtimer1>=35:
      badtimer1=35
    else:
      badtimer1+=5
  index=0
  for badguy in badguys:
    if badguy[0]<-0:
      badguys.pop(index)
    badguy[0]-=7
    # 6.3.1 - Attack
    badrect=pygame.Rect(badguyimg.get_rect())
    badrect.top=badguy[1]
    badrect.left=badguy[0]
    if badrect.left<-0:
      healthvalue -= random.randint(5,20)
      badguys.pop(index)
      
    #6.3.2 - Check for collisions
    index1=0
    for bullet in arrows:
      bullrect=pygame.Rect(arrow.get_rect())
      bullrect.left=bullet[1]
      bullrect.top=bullet[2]
      if badrect.colliderect(bullrect):
        y = badrect[0]
        x = badrect[1]
        z = [y, x]
        hit = badguys.index(z)
        acc[0]+=1
        if badguys[hit]:
          badguys.pop(hit)
          arrows.pop(index1)
        
  # 6.3.3 - Next bad guy 
    index1+=1
    
  for asteroid in asteroids:
    screen.blit(asteroidimg, asteroid)

  for badguy in badguys:
    framecount+=1
    if framecount>=10: 
      badguyimg=badguyimg1
    else:
      badguyimg=badguyimg2
    if framecount>=20:
      framecount=0
    
    screen.blit(badguyimg, badguy)
  # 6.4 Draw Clock
  frame+=1
  font = pygame.font.Font(None, 24)
  #survivedtext = font.render(str((90000-pygame.time.get_ticks())/60000)+":"+str((90000-pygame.time.get_ticks())/1000%60).zfill(2), True, (0,255,255))
  survivedtext = font.render(str(frame), True, (255, 0, 0))
  textRect = survivedtext.get_rect()
  textRect.topright=[1000,5]
  screen.blit(survivedtext, textRect)
  #6.5 - Draw Health Bar
  screen.blit(healthbar, (5,5))
  for health1 in range(healthvalue):
    screen.blit(health, (health1+8,8))
  # 7 update the screen
  pygame.display.flip()
  clock.tick(60)
  # 8 event handlers
  for event in pygame.event.get():
    if event.type==pygame.KEYDOWN:
      if event.key==K_w:
        keys[0]=True
      elif event.key==K_a:
        keys[1]=True
      elif event.key==K_s:
        keys[2]=True
      elif event.key==K_d:
        keys[3]=True 
    if event.type==pygame.KEYUP:
      if event.key==pygame.K_w:
        keys[0]=False
      elif event.key==pygame.K_a:
        keys[1]=False
      elif event.key==pygame.K_s:
        keys[2]=False
      elif event.key==pygame.K_d:
        keys[3]=False
    if event.type==pygame.MOUSEBUTTONDOWN:
      #shoot.play()
      position=pygame.mouse.get_pos()
      acc[1]+=1
      arrows.append([math.atan2(position[1]-(playerpos1[1]+32),position[0]-(playerpos1[0]+26)),playerpos1[0]+32,playerpos1[1]+32])     
    if event.type == pygame.QUIT:
      pygame.quit()
      exit(0)
      
  # 9 Move Player
  if keys[0]:
    if playerpos[1] >= 45: 
      playerpos[1]-=5
  elif keys[2]:
    if playerpos[1] <= 720:
      playerpos[1]+=5
  if keys[1]:
    if playerpos[0] >=45: 
      playerpos[0]-=5
  elif keys[3]:
    if playerpos[0] <= 740:
      playerpos[0]+=5
      
  #10 - Win/Lose check
  #if pygame.time.get_ticks()>=80000:
  if frame >= 2700:
    badtimer=100
    atimer=100
  #if pygame.time.get_ticks()>=90000:
  if frame == 3000:
    running=0
    exitcode=1
  if healthvalue<=0:
    running=0
    exitcode=0
  if acc[1]!=0:
    accuracy=acc[0]*1.0/acc[1]*100
  else:
    accuracy=0
  
# 11 - Win/lose display        
if exitcode==0:
  pygame.font.init()
  font = pygame.font.Font(None, 24)
  text = font.render("Accuracy: "+str(accuracy)+"%", True, (255,0,0))
  textRect = text.get_rect()
  textRect.centerx = screen.get_rect().centerx
  textRect.centery = screen.get_rect().centery+24
  screen.blit(gameover, (0,0))
  screen.blit(text, textRect)
else:
  pygame.font.init()
  font = pygame.font.Font(None, 24)
  text = font.render("Accuracy: "+str(accuracy)+"%", True, (0,255,0))
  textRect = text.get_rect()
  textRect.centerx = screen.get_rect().centerx
  textRect.centery = screen.get_rect().centery+24
  screen.blit(youwin, (0,0))
  screen.blit(text, textRect)
while 1:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      exit(0)
    pygame.display.flip()