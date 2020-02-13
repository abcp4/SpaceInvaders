import pygame
import time
import random
from constants import *
from game_objects import *
import numpy as np
from src import nn_play

pygame.init()

laser_sound = pygame.mixer.Sound("assets/sndLaser.wav")

click_sound = pygame.mixer.Sound("assets/sndBtnDown.wav")


gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('A basic space invaders')
 
# Definir ícone do jogo e papel de parede do menu
menu_background = pygame.image.load("assets/menu_background.png")
gameIcon = pygame.image.load('assets/icon.png')
pygame.display.set_icon(gameIcon)



clock = pygame.time.Clock()

def quitgame():
    pygame.quit()
    quit()

def text_objects(text, font, color = white):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()


def button(msg, x, y, w, h, ic, ac, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(gameDisplay, ac,(x,y,w,h))

        if click[0] == 1 and action != None:
            pygame.mixer.Sound.play(click_sound)
            pygame.mixer.music.stop()
            action()
    else:
        pygame.draw.rect(gameDisplay, ic,(x,y,w,h))
       

    smallText = pygame.font.Font("assets/Art Class.ttf",20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ( (x+(w/2)), (y+(h/2)) )
    gameDisplay.blit(textSurf, textRect)

def game_intro():
    intro = True

    menu_sound = pygame.mixer.music.load("assets/menuSound.mp3")
    pygame.mixer.music.play()

    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        gameDisplay.blit(menu_background, (0, 0))
        #largeText = pygame.font.Font('Sketch Pad.ttf',40)
        largeText = pygame.font.SysFont("comicsansms",40)
        TextSurf, TextRect = text_objects("Space Invaders", largeText)
        TextRect.center = ((display_width/2),(display_height/4))
        gameDisplay.blit(TextSurf, TextRect)

        mouse = pygame.mouse.get_pos()

        # Adicionar menu com opções
        button("Start!", 130, 300, 200, 50, ac=bright_green, ic=green, action = game_ia)
        button("Quit", 130, 380, 200, 50, ac=bright_red, ic=red, action=quitgame)

        pygame.display.update()
        clock.tick(15)

# def game_options():
#     options = True

#     while  options:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 quit()
#             if event.type == pygame.KEYDOWN:
#                if event.key == pygame.K_ESCAPE:
#                     game_intro()   

#         gameDisplay.fill(white)
#         pygame.display.update()
#         clock.tick(15)

def unpause():
    global pause
    pause = False

def paused():
    largeText = pygame.font.SysFont("comicsansms",90)
    TextSurf, TextRect = text_objects("Paused", largeText)
    TextRect.center = ((display_width/2),(display_height//3))
    gameDisplay.blit(TextSurf, TextRect)
    
    while pause:
        for event in pygame.event.get():
            #print(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        #gameDisplay.fill(white)
        button("Continue",180,375,100,50,green,bright_green,unpause)
        button("Quit",180,450,100,50,red,bright_red,quitgame)

        pygame.display.update()
        clock.tick(15) 


def matriz2canvas(x,y):
    canvas_x = 0
    canvas_y = 0

    #o espaco de coordenadas e invertido, ver SpaceCoord.txt
    canvas_x = (y/20)*460
    canvas_y = (x/30)*680

    canvas_y-= 650 #680
    canvas_y=abs(canvas_y)

    canvas_x-= 445 #460
    canvas_x=abs(canvas_x)


    return [canvas_x,canvas_y]


def finished(win=False):

    background = pygame.image.load("assets/background.png")
    gameDisplay.blit(background, (0, 0))

    
    largeText = pygame.font.SysFont("comicsansms",75)

    text = "You won."
    color = white
    if win is False:
        text = "Game Over."
        color = red
        largeText = pygame.font.Font('assets/Art Class.ttf',60)
        background = pygame.image.load("assets/game-over.png")
        gameDisplay.blit(background, (0, -50))
        game_over_sound = pygame.mixer.music.load("assets/gameOver.mp3")
        pygame.mixer.music.play()

    #gameDisplay.fill(black)

    

    
    TextSurf, TextRect = text_objects(text, largeText, color = color)
    TextRect.center = ((display_width/2),(display_height//3))
    gameDisplay.blit(TextSurf, TextRect)
    

    while True:
        for event in pygame.event.get():
            #print(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                

        button("Play Again!", 130, 300, 200, 50, ac=bright_green, ic=green, action = game_ia)
        button("Quit", 130, 380, 200, 50, ac=bright_red, ic=red, action=quitgame)

        pygame.display.update()
        clock.tick(15) 

def life_count(count):
    font = pygame.font.SysFont(None, 30)
    text = font.render("Life: "+str(count), True, white)
    gameDisplay.blit(text,(0,0))

def game_ia():
    global pause
    global bullets
    # Limpa a lista no começo de cada jogo
    bullets.clear()

    gameExit = False
    life = 10
    reward = 0

    max_shoots = 100
    #Criar n bullets
    for i in range(max_shoots):
        new_bullet = Bullet(pygame, (-1,-1), 0)
        bullets.append(new_bullet)

    x_change = 0
    y_change = 0

    background = pygame.image.load("assets/background.png")
    background_y  = display_height - background.get_height()

    player_life = np.array([1])
    ship = Ship(pygame=pygame, 
                img_path='assets/nave.png', 
                start_x=(display_width // 2), 
                start_y=display_height - ship_height,
                bullet_speed = -10, ship_type = "player")

    enemy_width = 80
    enemy_speed = 20
    enemies_life = np.ones(3)

    enemies = [Ship(pygame=pygame, img_path='assets/enemy_ship.png', 
                    start_x = (display_width // 2), start_y = 15, 
                    speed =enemy_speed, width = enemy_width), 
               Ship(pygame=pygame, img_path='assets/enemy_ship.png', 
                    start_x = 50, start_y = 15, width=enemy_width,
                    speed =enemy_speed),
               Ship(pygame=pygame, img_path='assets/enemy_ship.png', 
                    start_x = 400, start_y = 15, width=enemy_width,
                    speed =enemy_speed),
              ]

    count = 0
    nn_game = nn_play.NN_GAME()


    while not gameExit:
        count+=1
        act = 9999
        # termina o jogo
        if(reward == 100):
            finished(win=False)
        elif(reward == -100):
            finished(win=True)

        if(count>9999999999999):
            count = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = -ship_speed
                    act = 2
                if event.key == pygame.K_RIGHT:
                    x_change = ship_speed
                    act = 3
                if event.key == pygame.K_UP:
                    y_change = -ship_speed
                    act = 0
                if event.key == pygame.K_DOWN:
                    y_change = ship_speed
                    act = 1
                if event.key == pygame.K_SPACE:
                    #ship.shoot()
                    act = 4
                    pygame.mixer.Sound.play(laser_sound)
                    pygame.mixer.music.stop()
                if event.key == pygame.K_p:
                    pause = True
                    paused()
                if event.key == pygame.K_ESCAPE:
                    game_intro()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    x_change = 0
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    y_change = 0

        #player action            
        if(act!=9999):
            r,enemies_acts,enemy_coords,player_coord,shoots_coords = nn_game.play_nn(act)
            ship.set_pos(matriz2canvas(player_coord[0],player_coord[1]))
            reward = r
            


        #enemies actions
        if(count%10==0):
            act = 9999
            #r,enemies_acts,enemy_coords,player_coord,shoots_coords = nn_game.play_nn(act)
            #r,enemies_acts,enemy_coords,player_coord,shoots_coords = nn_game.play_mc(act)
            r,enemies_acts,enemy_coords,player_coord,shoots_coords = nn_game.play_mcts(act)
            reward = r      
            #for i in range(len(enemies_acts)):
            #    enemies[i].move_act(enemies_acts[i])
            e_i = 0
            for i in range(len(enemies)):
                e_pos = matriz2canvas(enemy_coords[e_i],enemy_coords[e_i+1])
                #print("Enemy ",str(i)," Canvas Coord: ",str(e_pos))

                #fix enemy pos: a little to left
                e_pos[0] = e_pos[0]-20

                enemies[i].set_pos(e_pos)
                e_i+=2

        #Shoots movement
        if(count%2==0):
            r,enemies_life,player_life,shoots_coords = nn_game.move_shoots_only()
            life = player_life[0]

            print(enemies_life, player_life)
            num_shoots = int(shoots_coords[0])
            reward = r    

            s_i=1#pos 0 e o num de tiros, logo comeca do 1

            for i in range(num_shoots):
                s_pos = matriz2canvas(shoots_coords[s_i],shoots_coords[s_i+1])
                #fix: bala muito distante da nave e um pouco a esq
                s_pos= (int(s_pos[0]+17),int(s_pos[1]))
                #s_pos= (int(s_pos[0]+17),int(s_pos[1])+80)
                
                #print(" Shoot ",str(i)," pos: ",str(s_pos))
                bullets[i].set_pos(s_pos)
                s_i+=2
                #a=2/0 
            remain_shoots = max_shoots-num_shoots
            if(remain_shoots>0):
                for i in range(remain_shoots):
                    bullets[num_shoots+i].set_pos((-1,-1))


        # desenha background
        gameDisplay.blit(background, (0, background_y))

        # Desenha a nave
        if(player_life[0]>0):
            ship.draw(gameDisplay)

        # Desenha naves inimigas
        for i in range(len(enemies)):
            if(enemies_life[i]>0):
                enemies[i].draw(gameDisplay)
                enemies[i].set_health(enemies_life[i])


        # Desenha as balas
        for bullet in bullets:
            bullet.draw(gameDisplay)

            # Remove as balas da lista que saíram da tela
            #if bullet.position[1] > display_height or bullet.position[1] < 0:
            #    bullets.remove(bullet)


        # Move o background
        background_y += bg_speed
        if background_y > 0:
            background_y =  display_height - background.get_height()
            
        life_count(life)
        pygame.display.update()
        clock.tick(60)
    



game_intro()
game_ia()
#finished()
pygame.quit()
quit()