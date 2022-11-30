"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Title: cast.py

    Description: simple caster for a playable game

    @author Marco Antonio Jurado 20308
    last update: 29/11/2022
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import pygame
from math import pi, cos, sin, atan2


WHITE, BLACK, RED, GREEN, BLUE = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)  # BASIC COLORS
CYAN = (0, 255, 255)
SKY = (60, 90, 200)
GRASS = (0, 150, 25)
BACKGROUND = (0, 150, 150)


# Game's walls
walls = {
    "1": pygame.image.load('./textures/brick.png'),
    "2": pygame.image.load('./textures/bushed_brick.png'),
    "3": pygame.image.load('./textures/pirelli_brick.png'),
    "4": pygame.image.load('./textures/finish_brick.png'),
    "5": pygame.image.load('./textures/f1_drivers.png')
}

wheel = pygame.image.load('./sprites/player.png')

enemies = [
  {
    "x": 100,
    "y": 200,
    "texture": pygame.image.load('./sprites/driver_enemy_2.png')
  }
]


pygame.init()
pantalla = pygame.display.set_mode(
    (1000, 600), pygame.DOUBLEBUF | pygame.HWACCEL | pygame.HWSURFACE)
pantalla.set_alpha(None)
pygame.mouse.set_visible(True)
backgr = pygame.image.load('./textures/Home_screen.png').convert()
reloj = pygame.time.Clock()


class Raycaster(object):
    def __init__(self, pantalla):
        _, _, self.width, self.height = pantalla.get_rect()
        self.pantalla = pantalla
        self.blocksize = 50
        self.player = {
            "x": int(self.blocksize + self.blocksize /2),
            "y": int(self.blocksize + self.blocksize /2),
            "Angle": pi/3,
            "fov": pi/3
        }
        self.map = []
        self.zbuffer = [-float('inf') for z in range(0, 500)]
        self.win = False  # para saber si termina el juego
        self.a = 0
        # self.clear()

    def clear(self):
        for x in range(self.width):
            for y in range(self.height):
                r = int((x/self.width)*255) if x/self.width < 1 else 1
                g = int((y/self.height)*255) if y/self.height < 1 else 1
                b = 0
                color = (r, g, b)
                self.point(x, y, color)

    def point(self, x, y, c=WHITE):
        self.pantalla.set_at((x, y), c)
    
    def checkWin(self):
        return self.win

    def load_map(self, filename):
        with open(filename) as f:
            for line in f.readlines():
                self.map.append(list(line))

    def cast_ray(self, a):
        d = 0
        while True:
            x = self.player["x"] + d*cos(a)
            y = self.player["y"] + d*sin(a)

            i = int(x/50)
            j = int(y/50)

            if self.map[j][i] != ' ':
                hitx = x - i*50
                hity = y - j*50

                if 1 < hitx < 49:
                    maxhit = hitx
                else:
                    maxhit = hity

                tx = int(maxhit * 128 / 50)

                return d, self.map[j][i], tx

            self.point(int(x), int(y), (255, 255, 255))
            d += 1


    def draw_blocks(self, x, y, walls):
        for i in range(x, x + 50):
            for j in range(y, y + 50):
                tx = int((i - x)*128 / 50)
                ty = int((j - y)*128 / 50)


                c = walls.get_at((tx, ty))
                self.point(i, j, c)


    def draw_stake(self, x, h, tex, tx):
        #check
        start = int(250 - h/2)
        end = int(250 + h/2)
        diff = end - start
        for y in range(start, end):
            ty = int( (y-start) * 128 / diff )
            c = tex.get_at((tx, ty))
            self.point(x, y, c)

    def draw_sprite(self, sprite):
        spriteX = 500
        spriteY = 0
        spriteSize = 128
        for x in range(spriteX, spriteX + spriteSize):
            for y in range(spriteY, spriteY + spriteSize):
                tx = int((x - spriteX) * 128 / spriteSize)
                ty = int((y - spriteY) * 128 / spriteSize)
                c = sprite["sprite"].get_at((tx, ty))
                if x > 500:
                    self.point(x,y,c)

    def draw_player(self, xi, yi, w, h):
        for x in range(xi, xi + w):
            for y in range(yi, yi + h):
                tx = int((x - xi) * 32/w)
                ty = int((y - yi) * 32/h)
                c = wheel.get_at((tx, ty))
                if c != (152, 0, 136, 255):
                    self.point(x, y, c)
    
    def checkloose(self):
        if self.a == 1:
            return False, False
        else:
            return True,True
        

    def render(self):
        for x in range(0, 500, 50):
            for y in range(0, 500, 50):
                i = int(x/50)
                j = int(y/50)
                if self.map[j][i] != ' ':
                    self.draw_blocks(x, y, walls[self.map[j][i]])

        self.point(self.player["x"], self.player["y"])

        for i in range(0, 500):
            self.point(500, i, (0, 0, 0))
            self.point(501, i, (0, 0, 0))
            self.point(499, i, (0, 0, 0))

        for i in range(0, 500):
            try:
                a =  self.player["Angle"] - self.player["fov"]/2 + self.player["fov"]*i/500
                d, c, tx = self.cast_ray(a)
                x = 500 + i
                h = 500/(d*cos(a-self.player["Angle"])) * 70
                self.draw_stake(x, h, walls[c], tx)
                self.zbuffer[i] = d
            except:
                self.player["x"] = 75
                self.player["y"] = 75
                self.a = 1
                

        self.draw_player(560, 500, 400, 100)

r = Raycaster(pantalla)
r.load_map('mapa2.txt')

# musica
pygame.mixer.music.load('./sound/f1theme.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
pantalla.blit(backgr,(0,0))
pygame.display.flip()

start = False
# start menu
while start == False:
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            running = False
            start = True
        if (event.type == pygame.KEYDOWN):
            start = event.key == pygame.K_SPACE


# game
pygame.mixer.music.load('./sound/keys.mp3')
pygame.mixer.music.set_volume(1)
pygame.mixer.music.play(start=0, loops=0,fade_ms=50)
c = 0
fail_game = True
startgame = True
running = True
while running == True:
    pantalla.fill(BLACK)
    pantalla.fill(SKY, (r.width / 2, 0, r.width, r.height / 3))
    pantalla.fill(GRASS, (r.width / 2, r.height / 2, r.width, r.height / 2))

    mouse = pygame.mouse.get_rel()

    running, fail_game = r.checkloose()
    if r.player["x"] <= 395 and r.player["x"] >= 355:
        if r.player["y"] <= 445 and r.player["y"] >= 405:
            running = False
            startgame = False

    
    
    r.render()

    tipo_letra = pygame.font.Font('freesansbold.ttf', 30)
    fpsss = tipo_letra.render(str(reloj.get_fps()) + 'fps', True, WHITE, BLACK)
    fpsrect = fpsss.get_rect()
    fpsrect.center = (600//2, 600//2)
    pantalla.blit(fpsss,fpsrect)

    for e in pygame.event.get():

        r.player["Angle"] += mouse[0]/30

        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
            running = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_a:
                r.player["Angle"] -= pi/10
            elif e.key == pygame.K_d:
                r.player["Angle"] += pi/10

            elif e.key == pygame.K_RIGHT:
                pygame.mixer.music.load('./sound/revcar.mp3')
                pygame.mixer.music.set_volume(0.8)
                pygame.mixer.music.play(start=0, loops=0,fade_ms=50)
                r.player["x"] += 10
            elif e.key == pygame.K_LEFT:
                pygame.mixer.music.load('./sound/revcar.mp3')
                pygame.mixer.music.set_volume(0.8)
                pygame.mixer.music.play(start=0, loops=0,fade_ms=50)
                r.player["x"] -= 10
            elif e.key == pygame.K_UP:
                pygame.mixer.music.load('./sound/revcar.mp3')
                pygame.mixer.music.set_volume(0.8)
                pygame.mixer.music.play(start=0, loops=0,fade_ms=50)
                r.player["y"] += 10
            elif e.key == pygame.K_DOWN:
                pygame.mixer.music.load('./sound/revcar.mp3')
                pygame.mixer.music.set_volume(0.8)
                pygame.mixer.music.play(start=0, loops=0,fade_ms=50)
                r.player["y"] -= 10

            if e.key == pygame.K_f:
                if pantalla.get_flags() and pygame.FULLSCREEN:
                    pygame.display.set_mode((1000, 500))
                else:
                    pygame.display.set_mode((1000, 500),  pygame.DOUBLEBUF|pygame.HWACCEL|pygame.FULLSCREEN)

    pygame.display.flip()
    reloj.tick()

# win screen
pantalla.fill(BLACK)
pygame.display.flip()
backgr = pygame.image.load('./textures/Win_screen.png').convert()
pygame.mixer.music.load('./sound/f1theme.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
pantalla.blit(backgr, (0,0))
pygame.display.flip()
while startgame == False:
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            # the end
            startgame = True 


# loose screen
pantalla.fill(BLACK)
pygame.display.flip()
backgr = pygame.image.load('./textures/Loose.png').convert()
pygame.mixer.music.load('./sound/f1theme.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
pantalla.blit(backgr, (0,0))
pygame.display.flip()
while fail_game == False:
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            # the end
            fail_game = True 