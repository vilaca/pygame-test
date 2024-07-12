import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1024
GAME_WIDTH = SCREEN_WIDTH * 8  # Extended game area
FPS = 60

# Colors
SKY_COLOR = (64, 200, 255)
PLAYER_COLOR = (255, 176, 176)
GREEN = (64, 200, 64)
FOE_COLOR = (255, 32, 64)
WHITE = (240, 255, 240)

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("Super Mario Bros")

# Clock and Font
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 72)

def display_message(message):
    text = font.render(message, True, (0, 0, 0))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()

def game_over_screen():
    display_message("Press R to Restart or Q to Quit")
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 100))
        self.image.fill(PLAYER_COLOR)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5
        self.jump_speed = 20
        self.gravity = 0.5
        self.vel_y = 0
        self.on_ground = False
        self.dead = False
        #self.on_moving_platform = None

    def update(self, platforms, foes):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        if self.on_ground:
            self.image.fill((255, 176, 176))
        else:
            self.image.fill((255, 128 , 128))

        self.vel_y += -self.gravity
        self.rect.y -= self.vel_y

        #self.on_ground = False
        #self.on_moving_platform = None
        self.check_platforms(platforms)
        self.check_foes(foes)

    def check_platforms(self, platforms):
        if self.vel_y > 0:
            return
        for platform in pygame.sprite.spritecollide(self, platforms, False):
            if self.vel_y < 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.on_ground = True
                if isinstance(platform, MovingPlatform):
                    #self.on_moving_platform = platform
                    self.rect.x += platform.speed * platform.direction

    def check_foes(self, foes):
        foe_hit_list = pygame.sprite.spritecollide(self, foes, False)
        for foe in foe_hit_list:
            #if self.vel_y > 0 and self.rect.bottom <= foe.rect.top + self.vel_y:
            if self.rect.bottom <= foe.rect.top - self.vel_y:
                self.vel_y = -self.jump_speed
                foe.kill()
                self.on_ground = False
            else:
                self.kill()
                self.dead = True

    def jump(self):
        if self.on_ground and not self.vel_y < 0:
            self.vel_y = self.jump_speed
            self.on_ground = False

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=WHITE, rounded=False):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        #self.image.fill((0, 0, 0, 0))
        if rounded:
            pygame.draw.ellipse(self.image, color, self.image.get_rect())
        else:
            self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, SCREEN_HEIGHT -y)

class MovingPlatform(Platform):
    def __init__(self, x, y, width, height, boundary_left, boundary_right, speed):
        super().__init__(x, y, width, height, WHITE, True)
        self.boundary_left = boundary_left
        self.boundary_right = boundary_right
        self.speed = speed
        self.direction = 1

    def update(self):
        old_x = self.rect.x
        self.rect.x += self.speed * self.direction
        if self.rect.left < self.boundary_left or self.rect.right > self.boundary_right:
            self.direction *= -1
        return self.rect.x - old_x  # Return the delta x

class Foe(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, min_x, max_x):
        super().__init__()
        self.image = pygame.Surface((width*1.5, height*1.5))
        self.image.fill(FOE_COLOR)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 2
        self.direction = 1
        self.gravity = 0.5
        self.vel_y = 0
        self.on_ground = False
        self.min_x = min_x
        self.max_x = max_x + width
        #self.on_moving_platform = None

    def update(self, platforms):
        self.rect.x += self.speed * self.direction
        if self.rect.x < self.min_x or self.rect.x > self.max_x:
            self.direction *= -1

        self.vel_y += -self.gravity
        self.rect.y -= self.vel_y

        self.on_ground = False
        #self.on_moving_platform = None
        for platform in pygame.sprite.spritecollide(self, platforms, False):
            #if self.rect.colliderect(platform.rect):# and self.vel_y > 0:
            self.rect.bottom = platform.rect.top
            self.vel_y = 0
            self.on_ground = True
            if isinstance(platform, MovingPlatform):
                self.on_moving_platform = platform
                self.rect.x += platform.speed * platform.direction

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)
        x = min(0, x)
        x = max(-(self.width - SCREEN_WIDTH), x)
        #y = max(-(self.height - SCREEN_HEIGHT), y)
        y = max(0, y)
#       x = -x
#       x -= x % (SCREEN_WIDTH * .8)
#       x += SCREEN_WIDTH / 2.5
#       x = -x
        self.camera = pygame.Rect(x, y, self.width, self.height)

def main():
    player = Player()
    platforms = pygame.sprite.Group()
    moving_platforms = pygame.sprite.Group()
    foes = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)

    # Ground platform
    ground = Platform(0, 50, GAME_WIDTH, 50, GREEN)
    platforms.add(ground)
    all_sprites.add(ground)

    # Static platforms
    static_platforms = [
        (300, 750), 
        (350, 1050), 
        (400, 1350), 
        (500, 1650), 
        (500, 1950), 
        (550, 2250), 
        
        (800, 600), (1400, 450),
        (1800, 700), (2200, 500), (2600, 350),
        (3000, 600), (3400, 750), (3800, 500),
        (4200, 650), (4600, 300), (5000, 550),
        (5400, 400), (5800, 250), (6200, 500),
        (6600, 750)
    ]
    # Additional higher platforms
    static_platforms.extend([
        (200, 400), (500, 300), (900, 200),
        (1300, 100), (1700, 200), (2100, 300)
    ])
    for x, y in static_platforms:
        plat = Platform(x, y, 200, 50, WHITE, True)
        platforms.add(plat)
        all_sprites.add(plat)

    # Moving platforms
    moving_platform_details = [
        (500, 800, 400, 800, 2), (1200, 300, 1100, 1500, 3),
        (2300, 450, 2200, 2600, 2), (3400, 500, 3300, 3700, 4),
        (4500, 700, 4400, 4800, 2), (5700, 400, 5600, 6000, 3)
    ]
    for x, y, min_x, max_x, speed in moving_platform_details:
        mplat = MovingPlatform(x, y, 300, 50, min_x, max_x, speed)
        moving_platforms.add(mplat)
        platforms.add(mplat)
        all_sprites.add(mplat)

    # Foes with specific movement ranges
    foe_positions = [
        (300, 250, 200, 600), (1600, 250, 1500, 1700),
        (2600, 450, 2500, 2700), (1200, 380, 1100, 1300), (4500, 500, 4400, 4600),
        (5500, 300, 5400, 5600), (500, 760, 400, 800), (1200, 260, 1100, 1500)
    ]
    for x, y, min_x, max_x in foe_positions:
        foe = Foe(x, y, 50, 50, min_x, max_x)
        foes.add(foe)
        all_sprites.add(foe)

    camera = Camera(GAME_WIDTH, SCREEN_HEIGHT)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

        # Update all sprites
        for sprite in all_sprites:
            if isinstance(sprite, Player):
                sprite.update(platforms, foes)
            elif isinstance(sprite, Foe):
                sprite.update(platforms)
            elif isinstance(sprite, MovingPlatform):
                sprite.update()

        camera.update(player)

        screen.fill((64, 200 , 255))
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))

        pygame.display.flip()

        clock.tick(FPS)

        if player.dead:
            break

if __name__ == "__main__":
    while True:
        main()
        game_over_screen()

