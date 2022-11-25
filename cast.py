"""
Raycaster
@author Marco Jurado 20308
"""
import pygame
from OpenGL.GL import * 
from math import *
import random

WHITE,BLACK,RED,GREEN,BLUE = (255,255,255),(0,0,0),(255,0,0),(0,255,0),(0,0,255) #BASIC COLORS 
CYAN = (0, 255, 255)
SKY = (60,90,200)
GRASS = (0,150,25)
w,h = 1200,600

# Game's walls
walls = {
    "1" : pygame.image.load('./textures/brick.png'),
    "2" : pygame.image.load('./textures/bushed_brick.png'),
    "3" : pygame.image.load('./textures/pirelli_brick.png'),
    "4" : pygame.image.load('./textures/finish_brick.png'),
    "5" : pygame.image.load('./textures/f1_drivers.png')
}

sprite1 = pygame.image.load('./sprites/driver_enemy_1.png')
sprite2 = pygame.image.load('./sprites/driver_enemy_2.png')

# Game's enemies
enemies = [
    {"n" : "s1", "x" : 80, "y" : 150, "sprite" : sprite1},
    {"n" : "s1", "x" : 80, "y" : 170, "sprite" : sprite2},
]

pygame.init()
pantalla = pygame.display.set_mode((w,h))
pygame.mouse.set_visible(True)
backgr = pygame.image.load('./textures/Home_screen.png').convert()


class Raycaster(object):
    def __init__(self, screen):
        self.screen = screen
        x, y, self.width, self.height = screen.get_rect()
        self.block_size = 50
        self.map = []
        self.player = {
            "x": int(self.block_size + (self.block_size / 2)),
            "y": int(self.block_size + (self.block_size / 2)),
            "FOV": int(pi / 3),
            "Angle": int(pi / 3)
        }
        self.kda = 0 # enemies defeated
        self.win = False # para saber si termina el juego
        self.blksize = 40
    
    def point(self, x, y, c=WHITE):
        self.screen.set_at((x, y), c)
    
    def checkWin(self):
        return self.finished
    
    def block(self, x, y, wall):
        for i in range(x, x + self.blksize):
            for j in range(y, y + self.blksize):
                tx = int((i - x) * 128 / self.blksize)
                ty = int((j - y) * 128 / self.blksize)
                c = wall.get_at((tx, ty))
                self.point(int(i), int(j), c)
    
    def loadmap(self, filename):
        with open(filename) as f:
            for line in f.readlines():
                self.map.append(list(line))

    # draw functions

    def draw_stake(self, x, h, c, tx):
        start_y = int(self.height / 2 - h / 2)
        end_y = int(self.height / 2 + h / 2)
        height = end_y - start_y
        for y in range(start_y, end_y):
            ty = int((y - start_y) * 128 / height)
            color = walls[c].get_at((tx, ty))
            self.point(x, y, color)

    def draw_enemies_characters_stake(self):
        for i in range(0, int(self.width)):
            a = self.player["Angle"] - self.player["FOV"] / 2 + self.player["FOV"] * i / (self.width / 2)
            d, c, tx = self.cast_ray(a)
            x = int(self.width / 2) + i
            h = (self.height / (d * cos(a - self.player["Angle"]))) * self.height / 5

            if self.zbuffer[i] > d:
                self.draw_stake(x, h, c, tx)
                self.zbuffer[i] = d

        for e in enemies:
            self.draw_sprite(e)

    def draw_map(self):
        for x in range(0, 100, int(self.blksize)):
            for y in range(0, 100, int(self.blksize)):
                i = int(x / self.blksize)
                j = int(y / self.blksize)

                if self.map[j][i] !=  ' ':
                    self.block(x, y, walls[self.map[j][i]])

    def draw_player(self):
        self.point(self.player.get("x"), self.player.get("y"))

    def draw_sprite(self, sprite):
        #verif
        sprite_a = atan2(sprite["y"] - self.player["y"], sprite["x"] - self.player["x"])
        d = ((self.player["x"] - sprite["x"]) ** 2 + (self.player["y"] - sprite["y"]) ** 2) ** 0.5
        size = int(500/d * (500/self.blksize))
        sprite_x = int(500 + (sprite_a - self.player["Angle"]) * 500 / self.player["FOV"] + (size / 2))
        sprite_y = int(500 / 2 - size / 2)

        for x in range(sprite_x, sprite_x + size):
            for y in range(sprite_y, sprite_y + size):
                tx = int((x - sprite_x) * 128 / size)
                ty = int((y - sprite_y) * 128 / size)
                c = sprite["sprite"].get_at((tx, ty))
                if x > 500:
                    if self.zbuffer[x-500] >= d:
                        self.point(x, y, c)
                        self.zbuffer[x-500] = d
    
    def zbuffed(self):
        self.zbuffer = [9999999999 for z in range(0, int(self.width))]

    # cast rays
    def cast_ray(self, a):
        d = 0
        ox = self.player["x"]
        oy = self.player["y"]

        while True:
            x = int(ox + d * cos(a))
            y = int(oy + d * sin(a))

            i = int(x / self.blksize)
            j = int(y / self.blksize)

            if self.map[j][i] != " ":
                hitx = x - i * self.blksize
                hity = y - j * self.blksize

                if 1 < hitx < self.blksize - 1:
                    maxhit = hitx
                else:
                    maxhit = hity

                tx = int(maxhit * 128 / self.blksize)
                return d, self.map[j][i], tx

            self.point(x, y, CYAN)
            self.screen.set_at((x, y), CYAN)

            d += 1

    
# create raycaster
r = Raycaster(pantalla)

# create map
r.loadmap('mapa.txt')
reloj = pygame.time.Clock()
running = True
startgame = False #verifica si comienza el juego

pygame.mixer.music.load('./sound/f1theme.mp3')
pygame.mixer.music.play(-1)
pantalla.blit(backgr,(0,0))
pygame.display.flip()

# start menu
while startgame == False:
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            running = False
            startgame = True
        if (event.type == pygame.KEYDOWN):
            startgame = event.key == pygame.K_SPACE

# run game
while running:
    pantalla.fill(BLACK)
    pantalla.fill(SKY, (r.width / 2, 0, r.width, r.height / 2))
    pantalla.fill(GRASS, (r.width / 2, r.height / 2, r.width, r.height / 2))
    
    r.draw_map()
    r.draw_player()
    r.zbuffed()
    r.draw_enemies_characters_stake()

    #fps counter
    tipo_letra = pygame.font.Font('freesansbold.ttf', 30)
    fpsss = tipo_letra.render(str(reloj.get_fps()) + 'fps', True, WHITE, BLACK)
    fpsrect = fpsss.get_rect()
    fpsrect.center = (600//2, 600//2)
    pantalla.blit(fpsss,fpsrect)

    # flip
    pygame.display.flip()
    reloj.tick()

    # events
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            running = False

        if (event.type == pygame.KEYDOWN):
            if event.key == pygame.K_RIGHT:
                r.player["Angle"] += pi / 10

            elif event.key == pygame.K_LEFT:
                r.player["Angle"] -= pi / 10

            elif event.key == pygame.K_w:
                r.player["y"] += 10

            elif event.key == pygame.K_s:
                r.player["y"] -= 10

            elif event.key == pygame.K_a:
                r.player["x"] -= 10

            elif event.key == pygame.K_d:
                r.player["x"] += 10

startgame = False
backgr = pygame.image.load('./textures/Win_screen.png').convert()
pantalla.blit(backgr, (0,0))
pygame.display.flip()
while startgame == False:
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            # the end
            startgame = True 