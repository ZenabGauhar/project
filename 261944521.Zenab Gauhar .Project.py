import pygame
import os
import time
import random
pygame.font.init()
pygame.mixer.init()

# Set up the display window
WIDTH, HEIGHT = 1500, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Load images
SHIP_IMG = pygame.image.load(os.path.join("assets", "player.png"))
ENEMY_IMG = pygame.image.load(os.path.join("assets", "enemy.png"))
LASER_IMG = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
BG_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "space.bg.jpg")), (WIDTH, HEIGHT))
GEM_IMG = pygame.image.load(os.path.join("assets", "gem.png"))

# Load sounds
SHOOT_SOUND = pygame.mixer.Sound(os.path.join("assets", "audio_laser.wav"))
EXPLOSION_SOUND = pygame.mixer.Sound(os.path.join("assets", "audio_explosion.wav"))
COLLECT_SOUND = pygame.mixer.Sound(os.path.join("assets", "coins.wav"))
pygame.mixer.music.load("bg.mp3")
pygame.mixer.music.play(-1)

# Ship class
COOLDOWN = 30
class Ship:
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = SHIP_IMG
        self.laser_img = LASER_IMG
        self.lasers = []
        self.cooldown_counter = 0
        self.mask= pygame.mask.from_surface(self.ship_img)
       
       

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        EXPLOSION_SOUND.play()
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            self.health += 10
                            global score
                            score+=10
                            
                            

    def cooldown(self):
        if self.cooldown_counter >= 20:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 1

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1
            SHOOT_SOUND.play()

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

# Laser class
class Laser:
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
        return not (height >= self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)



# Enemy class(Inherited from ship class)

class Enemy(Ship):
    def __init__(self, x, y, health=100):
        super().__init__( x, y, health=100)
        self.x = x
        self.y = y
        self.health = health
        self.enemy_img = ENEMY_IMG
        self.laser_img = LASER_IMG
        self.lasers = []
        self.cooldown_counter = 0
        self.mask= pygame.mask.from_surface(self.enemy_img)

    def draw(self, window):
        window.blit(self.enemy_img, (self.x, self.y))
       
        for laser in self.lasers:
            laser.draw(window)

    def move(self, vel):
        self.y += vel

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cooldown_counter >= 20:
            self.cooldown_counter = 0
        elif self.cooldown_counter > 0:
            self.cooldown_counter += 1

    def shoot(self):
        if self.cooldown_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter = 1

    def get_width(self):
        return self.enemy_img.get_width()

    def get_height(self):
        return self.enemy_img.get_height()
    
    def collide(obj1, obj2):
        offset_x = obj2.x - obj1.x
        offset_y = obj2.y - obj1.y
        return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None





# Gem class
class Gem:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel = 3
        self.gem_img = GEM_IMG
        self.mask = pygame.mask.from_surface(self.gem_img)

    def draw(self, window):
        window.blit(self.gem_img, (self.x, self.y))

    def move(self):
        self.y += self.vel

    def off_screen(self, height):
        return self.y >= height

    def collision(self, obj):
        return collide(self, obj)

    def get_width(self):
        return self.gem_img.get_width()

    def get_height(self):
        return self.gem_img.get_height()

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


#File handling to display high score

def load_highest_score():
    try:
        with open("highest_score.txt", "r") as file:
            highest_score = int(file.read())
    except FileNotFoundError:
        highest_score = 0

    return highest_score

def update_score(highest_score):
    with open("highest_score.txt", "w") as file:
        file.write(str(highest_score))

#Main class
def main():
    run = True
    FPS = 60
    level = 0
    lives = 3
    global score
    score = 0

    enemies = []
    gems = []
    wave_length = 5
    enemy_vel = 2

    player_vel = 5
    laser_vel = 5

    player = Ship(300, 650)

    clock = pygame.time.Clock()
    highest_score = load_highest_score()

    lost = False
    lost_count = 0
    collision_count=0
    

    def redraw_window():
        WIN.blit(BG_IMG, (0, 0))

        
        # Draw text
        lives_label = pygame.font.SysFont("comicsans", 30).render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = pygame.font.SysFont("comicsans", 30).render(f"Level: {level}", 1, (255, 255, 255))
        score_label = pygame.font.SysFont("comicsans", 30).render(f"Score: {score}", 1, (255, 255, 255))
        Afont=pygame.font.SysFont("comicsans", 30)

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(score_label, (WIDTH // 2 - score_label.get_width() // 2, 10))


        highest_score_label =  Afont.render(f"Highest Score: {highest_score}", 1, (255, 255, 255))
       
       
        WIN.blit(highest_score_label, (10, 70))

        for enemy in enemies:
            enemy.draw(WIN)

        for gem in gems:
            gem.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = pygame.font.SysFont("comicsans", 50).render("You Lost!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH // 2 - lost_label.get_width() // 2, HEIGHT // 2 - lost_label.get_height() // 2))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

    
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0 :
            level += 1
            wave_length += 5
            for _ in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
            SHOOT_SOUND.play()
            

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                collision_count+=1
                enemies.remove(enemy)
                EXPLOSION_SOUND.play()

            if enemy.y + enemy.get_height() > HEIGHT:
                enemies.remove(enemy)
                
        if collision_count>=5:
            lives-1
            collision_count=0
            pygame.display.update()

             # I'm create new Gem objects and adding them to the gems list
        if len(gems) == 0:
           
            for _ in range(wave_length):
                gem = Gem(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
                gems.append(gem)


        for gem in gems[:]:
            gem.move()
            if collide(gem, player):
                score += 2
                gems.remove(gem)
                COLLECT_SOUND.play()

            if gem.y + gem.get_height() > HEIGHT:
                gems.remove(gem)

        player.move_lasers(-laser_vel, enemies)
        if score> highest_score:
           #updating highscore
            update_score(score)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG_IMG, (0, 0))
        title_label = title_font.render("Let the BATTLE begin...", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH // 2 - title_label.get_width() // 2, HEIGHT // 2 - title_label.get_height() // 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()
