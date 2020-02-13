import copy
from constants import *

bullets = []

class Bullet:
    def __init__(self, pygame, position, speed):
        self.speed = speed
        self.position = position
        self.pygame = pygame

    def move(self):
        self.position[1] += self.speed

    def set_pos(self,pos):
        self.position=pos

    def draw(self,screen):
        self.pygame.draw.circle(screen, white, self.position, 5)





class Ship:
    def __init__(self,pygame, img_path, start_x, start_y, width = 30, speed = 5, bullet_speed = 7, health = 2, ship_type = "enemy"):
        self.position = [start_x, start_y]
        self.bullet_speed = bullet_speed
        self.speed = speed
        self.img = pygame.image.load(img_path)
        ship_width, ship_height = self.img.get_rect().size
        ratio = ship_width // width
        self.img = pygame.transform.scale(self.img, (ship_width//ratio, ship_height//ratio))
        self.pygame = pygame
        self.bullet_adj = width // 2
        self.hitbox = (self.position[0] + 17, self.position[1] + 2, 31, 57)
        self.type = ship_type
        self.hmax = health
        self.health = health

    def set_health(self, value):
        self.health = value

    def draw(self, screen):
        screen.blit(self.img, self.position)
        if(self.type == "enemy"):
            self.pygame.draw.rect(screen, (255,0,0), (self.hitbox[0], self.hitbox[1] - 20, 50, 10))
            self.pygame.draw.rect(screen, (0,128,0), (self.hitbox[0], self.hitbox[1] - 20, 50 - (50*(self.hmax - self.health))/self.hmax, 10))
            self.hitbox = (self.position[0] + 17, self.position[1] + 2, 31, 57)

    def set_ship_speed(self,speed):
        self.speed = speed

    def set_bullet_speed(self,speed):
        self.bullet_speed = speed

    def move_horizontal(self, value):
        self.position[0] += value

    def move_vertical(self, value):
        self.position[1] += value

    def set_pos(self,pos):
        self.position[0] = pos[0]
        self.position[1] = pos[1]

    # def move_act(self,act):
    #     x_change = 0
    #     y_change = 0
    #     if act == 0:
    #         x_change = -self.speed
    #     if act == 1:
    #         x_change = self.speed
    #     if act == 2:
    #         y_change = -self.speed
    #     if act == 3:
    #         y_change = self.speed
    #     if act == 4:
    #         self.shoot()

    #     self.move_horizontal(x_change)
    #     self.move_vertical(y_change)
        
    # def shoot(self):
    #     position = copy.copy(self.position)
    #     position[0]+= self.bullet_adj
    #     new_bullet = Bullet(self.pygame, position, self.bullet_speed)
    #     bullets.append(new_bullet)