import pygame,os,random,time,sys

''' Initilaize pygame font & sound library'''
pygame.font.init() 
pygame.mixer.init()

''' CONSTANTS '''
GAME_WIDTH = 1280
GAME_HEIGHT = 720
FPS = 60
WHITE = (255,255,255)
SPACESHIP_WIDTH = 80
SPACESHIP_HEIGHT = 89
BACKGROUND_COLOR = (20,20,20)
SPACESHIP_VELOCITY = 6
BULLETS = []
BULLET_VELOCITY = 10
BULLETS_COLOR = (255,55,0)
BULLET_WIDTH = 10
BULLET_HEIGHT = 26
HEALTH = 5
ENEMIES = []
WAVE_LENGTH = 0
LEVEL = 0
ENEMY_VELOCITY = 1
LOST = False
LOST_COUNT = 0


''' IMAGES '''
ICON = (pygame.image.load('assets/icon.png'))
BACKGROUND_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join('assets','bg.jpg')),(GAME_WIDTH,GAME_HEIGHT))
SPACESHIP_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join('assets/ship/smallship.png')),(SPACESHIP_WIDTH,SPACESHIP_HEIGHT))            # SPACESHIP = pygame.transform.rotate(pygame.transform.scale(SPACESHIP_IMAGE,(width,height)),90)
BULLET_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join('assets','ship','bullet.png')),(BULLET_WIDTH,BULLET_HEIGHT))
ENEMY1_IMAGE = pygame.image.load('assets/enemies/enemy1.png')
ENEMY2_IMAGE = pygame.image.load('assets/enemies/enemy2.png')
ENEMY3_IMAGE = pygame.image.load('assets/enemies/enemy4.png')
ENEMY4_IMAGE = pygame.image.load('assets/enemies/enemy5.png')
ENEMY5_IMAGE = pygame.image.load('assets/enemies/enemy6.png')
ENEMY6_IMAGE = pygame.image.load('assets/enemies/enemy7.png')
ENEMY_BULLET_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join('assets','enemies','enemy_bullet.png')),(BULLET_WIDTH,BULLET_HEIGHT))
''' UNIQUE EVENTS '''
SPACESHIP_HIT = pygame.USEREVENT + 1
''' FONTS '''
HEALTH_FONT = pygame.font.Font('assets/font/Minecraft.ttf',30)
LEVEL_FONT = pygame.font.Font('assets/font/Minecraft.ttf',40)
DIED_FONT = pygame.font.Font('assets/font/Minecraft.ttf',105)
''' AUDIO'''
# BULLET_HIT_SOUND = pygame.mixer.load(path)
BULLET_FIRE_SOUND = pygame.mixer.Sound('assets/audio/shoot.wav')
BACKGROUND_MUSIC = pygame.mixer.Sound('assets/audio/bg_music.mp3')
pygame.mixer.Sound.set_volume(BACKGROUND_MUSIC,0.5)
BACKGROUND_MUSIC.play(loops=-1)
    
''' CREATE WINDOW '''
WINDOW = pygame.display.set_mode((GAME_WIDTH,GAME_HEIGHT))
pygame.display.set_caption("Space Invaders")
pygame.display.set_icon(ICON)


''' CLASSES '''
class Ship:

    COOLDOWN = 20
    def __init__(self,x,y,health=HEALTH):
        self.x = x
        self.y = y
        self.health = HEALTH
        self.ship_img = None
        self.bullets_img = None
        self.bullets = []
        self.cool_down_counter = 0

    def draw(self,screen):
        screen.blit(self.ship_img,(self.x,self.y))
        for bullet in self.bullets:bullet.draw(WINDOW)
    
    def move_lasers(self, vel, obj):
        global HEALTH
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(vel)
            if bullet.off_screen(GAME_HEIGHT):
                self.bullets.remove(bullet)
            elif bullet.collision(obj):
                HEALTH-=1
                self.bullets.remove(bullet)
    
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
    
    def shoot(self):
        if self.cool_down_counter == 0:
            bullet = Bullet(self.x + self.get_width()//2-3, self.y, self.bullets_img)
            self.bullets.append(bullet)
            self.cool_down_counter = 1
            BULLET_FIRE_SOUND.play()
                
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()
        
        
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = SPACESHIP_IMAGE
        self.bullets_img = BULLET_IMAGE
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for bullet in self.bullets:
            bullet.move(vel)
            if bullet.off_screen(GAME_HEIGHT):
                self.bullets.remove(bullet)
            else:
                for obj in objs:
                    if bullet.collision(obj):
                        objs.remove(obj)
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                            
class Enemy(Ship):
    ENEMY_MAP = {
                "1":ENEMY1_IMAGE,"2":ENEMY2_IMAGE,
                "3":ENEMY3_IMAGE,"4":ENEMY4_IMAGE,
                "5":ENEMY5_IMAGE,"6":ENEMY6_IMAGE
                }
    
    def __init__(self, x, y, type, health=100):
        super().__init__(x, y, health)  
        self.ship_img,self.bullets_img = self.ENEMY_MAP[type],ENEMY_BULLET_IMAGE
        self.mask = pygame.mask.from_surface(self.ship_img)
    
    def move(self,velocity):
        self.y += velocity
        
    def shoot(self):
        if self.cool_down_counter == 0:
            bullet = Bullet(self.x + self.get_width()//2-3, self.y + self.get_height()+ 10, self.bullets_img)
            self.bullets.append(bullet)
            self.cool_down_counter = 1       
class Bullet:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)
          


''' FUNCTIONS '''
def draw_window(player,bullets,health,enemies,level):

    # WINDOW.fill((BACKGROUND_COLOR))
    WINDOW.blit(BACKGROUND_IMAGE,(0,0))
    player.draw(WINDOW)
    
    level_text = LEVEL_FONT.render('Level: ' + str(level),1,WHITE)
    WINDOW.blit(level_text,(45,20))
    health_text = HEALTH_FONT.render('Lives: ' + str(health),1,WHITE)
    WINDOW.blit(health_text,(45,20+level_text.get_height()))
    
    if LOST:
        died_text = DIED_FONT.render('YOU DIED',1,(255,0,0))
        died_text_behind = DIED_FONT.render('YOU DIED',1,(50,50,50))
        WINDOW.blit(died_text_behind,((GAME_WIDTH//2-died_text.get_width()//2)+4,(GAME_HEIGHT//2-died_text.get_height()//2)+4))
        WINDOW.blit(died_text,(GAME_WIDTH//2-died_text.get_width()//2,GAME_HEIGHT//2-died_text.get_height()//2))
        pygame.display.update()
        pygame.time.wait(3000)
        restart()
        
    
    for enemy in enemies:
        enemy.draw(WINDOW)
    
    for bullet in bullets:
        WINDOW.blit(BULLET_IMAGE, bullet)
    pygame.display.update()
    
def movement(keys_pressed,pos):
    if keys_pressed[pygame.K_a] and pos.x - SPACESHIP_VELOCITY > 0: pos.x -= SPACESHIP_VELOCITY                              # LEFT
    if keys_pressed[pygame.K_d] and pos.x + pos.get_width() + SPACESHIP_VELOCITY < GAME_WIDTH: pos.x += SPACESHIP_VELOCITY   # RIGHT
    if keys_pressed[pygame.K_w] and pos.y - SPACESHIP_VELOCITY > 0: pos.y -= SPACESHIP_VELOCITY                              # UP
    if keys_pressed[pygame.K_s] and pos.y + pos.get_height() + SPACESHIP_VELOCITY < GAME_HEIGHT: pos.y += SPACESHIP_VELOCITY # DOWN

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


''' MAIN '''
def main():
    
    global HEALTH
    global ENEMIES
    global WAVE_LENGTH
    global LEVEL
    global ENEMY_VELOCITY
    global LOST
    global LOST_COUNT
    LOST= False
    player = Player(GAME_WIDTH//2-SPACESHIP_WIDTH//2,GAME_HEIGHT//2+150)
    
    ''' MAINLOOP '''
    
    clock = pygame.time.Clock()
    run = True

    while run:
        clock.tick(FPS)
        draw_window(player,BULLETS,HEALTH,ENEMIES,LEVEL)
        if HEALTH == 0:
            HEALTH=5
            LEVEL = 0
            WAVE_LENGTH=5
            ENEMIES.clear()
            LOST = True
            LOST_COUNT += 1
            
        
        ''' LEVEL & ENEMIES '''
        if len(ENEMIES) == 0:
            LEVEL+=1
            WAVE_LENGTH +=5
            for i in range(WAVE_LENGTH):
                enemy = Enemy(random.randrange(100,GAME_WIDTH-100),random.randrange(-1200,-100),random.choice(['1','2','3','4','5','6']))
                ENEMIES.append(enemy)
        
        for enemy in ENEMIES[:]:
            enemy.move(ENEMY_VELOCITY)  
            enemy.move_lasers(BULLET_VELOCITY,player)
            if random.randrange(0,2*FPS) == 1:
                enemy.shoot()
            if collide(enemy,player):
                HEALTH -=1
                ENEMIES.remove(enemy)
            elif enemy.y + enemy.get_height() > GAME_HEIGHT:
                HEALTH-=1
                ENEMIES.remove(enemy)
            
        player.move_lasers(-BULLET_VELOCITY,ENEMIES)
        
        ''' Events '''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                            
            # ''' BULLET '''
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_SPACE and len(BULLETS) < BULLETS_NUM:
            #         bullet = pygame.Rect(player.x + SPACESHIP_WIDTH//2-4,player.y-3,BULLET_WIDTH,BULLET_HEIGHT)
            #         BULLETS.append(bullet)
            #         BULLET_FIRE_SOUND.play()
            
        keys_pressed = pygame.key.get_pressed()
          
        ''' CALLING FUNCTIONS '''
        movement(keys_pressed,player)
        if keys_pressed[pygame.K_SPACE]:
            player.shoot()

def main_menu():
    
    title_font = pygame.font.Font("assets/font/Minecraft.ttf", 70)
    run = True
    

    while run:
        WINDOW.blit(BACKGROUND_IMAGE, (0,0))
        title_label = title_font.render("Press any key to begin...", 1, (255,255,255))
        WINDOW.blit(title_label, (GAME_WIDTH//2 - title_label.get_width()//2, 360))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()

def restart():
    
    title_font = pygame.font.Font("assets/font/Minecraft.ttf", 70)
    run = True

    while run:
        WINDOW.blit(BACKGROUND_IMAGE, (0,0))
        title_label = title_font.render("Press R to restart...", 1, (255,255,255))
        WINDOW.blit(title_label, (GAME_WIDTH//2 - title_label.get_width()//2, 360))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[pygame.K_r]:
                main()
    pygame.quit()
    pygame.quit()
    
''' START '''
if __name__ == '__main__':main_menu()