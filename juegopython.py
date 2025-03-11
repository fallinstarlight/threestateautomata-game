import pygame
import numpy as np
import time

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((1440, 810))
pygame.display.set_caption("Game usign three state finite automata")

#images/sprites
playerimg = pygame.image.load("juegoautomata/assets/img/player.webp")
creeper = pygame.image.load("juegoautomata/assets/img/creeper.png")
spider = pygame.image.load("juegoautomata/assets/img/spider.webp")
zombie = pygame.image.load("juegoautomata/assets/img/zombie.webp")
skeleton = pygame.image.load("juegoautomata/assets/img/skeleton.webp")
background = pygame.image.load("juegoautomata/assets/img/background.png")
cob = pygame.image.load("juegoautomata/assets/img/obstacle.png")
lava = pygame.image.load("juegoautomata/assets/img/lava.jpg")
full = pygame.image.load("juegoautomata/assets/img/full.png")
twoleft = pygame.image.load("juegoautomata/assets/img/2left.png")
oneleft = pygame.image.load("juegoautomata/assets/img/1left.png")
dead = pygame.image.load("juegoautomata/assets/img/dead.jpg")

# Font
pygame.font.init()
fuente = pygame.font.Font("juegoautomata/assets/fonts/Fanfarron.ttf", 36)

#global variable
hp = 3
hp_decrease = time.time()

#defines the enemies
class mob:
    #initializer, sprite is the image used for the mob, state defines if the mob wanders, chases or attacks, based on distance to the player
    def __init__(self, x, y, sprite, creeper):
        #used for horizontal and vertical movement
        self.x = x 
        self.y = y
        self.sprite = sprite
        self.state = "Wandering" #the initial state is wandering
        #count is used for the movement alongside dist, dist determines how far the mob will go, count will increment by 1
        # and once is equal to dist the movement will cease
        self.count = 0 
        self.dist = np.random.randint(50, 201)
        self.direction = np.random.randint(1, 5)
        self.creeper = creeper


    def update(self, jugador_x, jugador_y, obstacles):
        global hp, hp_decrease
        if self.state == "Wandering":
            # choses randomly between up, down, left, rigth
            # direction will increment or decrement by 1 in that specific direction until count reaches distance
            # new_x and new_y are used for collision detection
            match self.direction:
                case 1:
                    new_x = self.x + 1
                    new_y = self.y
                case 2:
                    new_x = self.x - 1
                    new_y = self.y
                case 3:
                    new_x = self.x
                    new_y = self.y + 1
                case 4:
                    new_x = self.x
                    new_y = self.y - 1
            
            # if a collision is not detected, new_x/y will pass its value to self.x/y to allow movement
            if not self.check_collision(new_x, new_y, obstacles):
                self.x = new_x
                self.y = new_y

            #increase count by 1 after each iteration
            self.count += 1

            # movement stops when count equals dist, gets initialized again, a new direction and distance are choosen
            if self.count >= self.dist:
                self.direction = np.random.randint(1, 5)
                self.dist = np.random.randint(50, 201)
                self.count = 0

            # if the distance to the player is less than 90 vertically and 160 horizontally, (50 diagonally) the mob starts chasing
            if abs(self.x - jugador_x) < 160 and abs(self.y - jugador_y) < 90:
                self.state = "Chasing"

        elif self.state == "Chasing":
            # used for collision detection
            new_x = self.x
            new_y = self.y

            # change the possition of the mob based on the distance to the player
            # creeper moves faster than other mobs
            if self.x < jugador_x:
                new_x += 2 if not self.creeper else 5
            else:
                new_x -= 2 if not self.creeper else 5

            if self.y < jugador_y:
                new_y += 2 if not self.creeper else 5
            else:
                new_y -= 2 if not self.creeper else 5
            
            # collision detection
            if not self.check_collision(new_x, new_y, obstacles):
                self.x = new_x
                self.y = new_y

            # start attack mode when the distance to the player is almost 0
            if abs(self.x - jugador_x) < 30 and abs(self.y - jugador_y) < 30:
                self.state = "Attacking"
            # stop attacking if entering a colission, to avoid mobs getting stuck
            elif self.check_collision(new_x, new_y, obstacles):
                self.state = "Wandering" 
                
        
        elif self.state == "Attacking":
            # damage is dealt every two seconds, player has 3 hp, creeper instakills
            current_time = time.time()
            if current_time - hp_decrease >= 2: 
                # hp: amount of hitpoints, hp_decrease: last time when damage was dealt (timestamp)
                hp -= 1 if not self.creeper else 3  
                hp_decrease = current_time
            # stop attacking if the distance increases     
            if abs(self.x - jugador_x) > 50 or abs(self.y - jugador_y) > 50:
                self.state = "Chasing"
    
        # avoid mobs to get out of screen bounds    
        self.x = max(0, min(self.x, screen.get_width() - self.sprite.get_width()))
        self.y = max(0, min(self.y, screen.get_height() - self.sprite.get_height()))

    # draw the mob using the sprite
    def draw(self):
        screen.blit(self.sprite, (self.x, self.y))
        self.mostrar_estado()
    
    # mostrar.estado shows the state the mob is in as a text above it
    def mostrar_estado(self):
        match self.state:
            case 'Wandering':
                color = "#0FA11B"
            case 'Chasing':
                color = "#F8F802"
            case 'Attacking':
                color ="#9F0505"
        texto_estado = fuente.render(self.state, True, color)
        screen.blit(texto_estado, (self.x - 30, self.y - 40))
    
    # checks for collision using the potential new x and y values, doesn't allow those values to be passed to the actual x and y variables
    # if a collision is detected
    def check_collision(self, new_x, new_y, obstacles):
        # Create a rect for the mob's new position
        mob_rect = pygame.Rect(new_x, new_y, self.sprite.get_width(), self.sprite.get_height())
        for obstacle in obstacles:
            # Create a rect for the obstacle
            obstacle_rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.sprite.get_width(), obstacle.sprite.get_height())
            if mob_rect.colliderect(obstacle_rect):
                return True  # Collision detected
        return False  # No collision

# defines the player
class player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5

    # detects the keys pressed and change direction based on them
    def move(self, keys, obstacles):
        new_x = self.x
        new_y = self.y

        if keys[pygame.K_LEFT]:
            new_x -= self.speed
        if keys[pygame.K_RIGHT]:
            new_x += self.speed
        if keys[pygame.K_UP]:
            new_y -= self.speed
        if keys[pygame.K_DOWN]:
            new_y += self.speed
        
        # checks collisions
        if not self.check_collision(new_x, new_y, obstacles):
            self.x = new_x
            self.y = new_y
        
        # checks if not out of bounds
        self.x = max(0, min(self.x, screen.get_width() - creeper.get_width()))
        self.y = max(0, min(self.y, screen.get_height() - creeper.get_height()))

    # draws the player
    def draw(self):
        screen.blit(playerimg, (self.x, self.y))
    
    # same function to check for collitions
    def check_collision(self, new_x, new_y, obstacles):
        # Create a rect for the player's new position
        player_rect = pygame.Rect(new_x, new_y, playerimg.get_width(), playerimg.get_height())
        for obstacle in obstacles:
            # Create a rect for the obstacle
            obstacle_rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.sprite.get_width(), obstacle.sprite.get_height())
            if player_rect.colliderect(obstacle_rect):
                return True  # Collision detected
        return False  # No collision

# defines the obstacles (lava and rock walls)
class obstacle:
    def __init__(self, x, y, sprite):
        self.x = x
        self.y = y
        self.sprite = sprite

    def draw(self):
        screen.blit(self.sprite, (self.x, self.y))


# Initialize objects, 4 mobs, one player, 5 obstacles
moba = mob(100, 300, creeper, True)
mobb = mob(1200, 400, spider, False)
mobc = mob(720, 600, zombie, False)
mobd = mob(920, 60, skeleton, False)

player1 = player(400, 300)

obstacleslist = [
    obstacle(300, 720, cob),
    obstacle(300, 680, cob),
    obstacle(300, 640, cob),
    obstacle(300, 600, cob),
    obstacle(340, 720, cob),
    obstacle(340, 680, cob),
    obstacle(340, 640, cob),
    obstacle(340, 600, cob),

    obstacle(1160, 70, cob),
    obstacle(1180, 70, cob),
    obstacle(1200, 70, cob),
    obstacle(1240, 70, cob),
    obstacle(1280, 70, cob),

    obstacle(840, 560, cob),
    obstacle(880, 560, cob),
    obstacle(880, 520, cob),

    obstacle(610, 190, cob),
    obstacle(610, 230, cob),
    obstacle(610, 270, cob),
    obstacle(610, 310, cob),
    obstacle(610, 350, cob),
    obstacle(610, 390, cob),

    obstacle(150, 80, lava),
    obstacle(190, 80, lava),
    obstacle(230, 80, lava),
    obstacle(270, 120, lava),
    obstacle(230, 120, lava),
    obstacle(190, 120, lava),
    obstacle(230, 160, lava),
    obstacle(190, 160, lava),
    obstacle(150, 160, lava),
    obstacle(150, 200, lava),

]

# game
game = True
alive = 1
while game:
    # checks if the player is alive (has >= 1 hp)
    if alive:
        # sprites drawn in order to avoid overlaping
        # background image
        screen.blit(background, (0, 0))

        keys = pygame.key.get_pressed()
        player1.move(keys, obstacleslist)

        # shows a different health bar depending on the hp
        match hp:
            case 3:
                screen.blit(full, (1300, 10))
            case 2: 
                screen.blit(twoleft, (1300, 10))
            case 1:
                screen.blit(oneleft, (1300, 10))

        # control and draw the mobs
        moba.update(player1.x, player1.y, obstacleslist)
        moba.draw()
        mobb.update(player1.x, player1.y, obstacleslist)
        mobb.draw()
        mobc.update(player1.x, player1.y, obstacleslist)
        mobc.draw()
        mobd.update(player1.x, player1.y, obstacleslist)
        mobd.draw()
        player1.draw()
        for obs in obstacleslist:
            obs.draw()

        # kills the player if hp = 0 and shows deathscreen
        if hp <= 0:
            screen.blit(dead, (0, 0))
            alive = 0

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            game = False

    pygame.display.flip()
    pygame.time.delay(50)

pygame.quit()
