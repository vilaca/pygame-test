import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Bros")

# Clock
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5
        self.jump_speed = 15
        self.gravity = 0.8
        self.vel_y = 0
        self.on_ground = False

    def update(self, platforms, foes):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        
        self.vel_y += self.gravity
        self.rect.y += self.vel_y
        
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0
            self.on_ground = True
        
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y > 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.on_ground = True
        
        for foe in foes:
            if self.rect.colliderect(foe.rect):
                if self.vel_y > 0:  # Falling down
                    foes.remove(foe)
                    foe.kill()  # Remove the foe completely
                    self.vel_y = -self.jump_speed
                    self.on_ground = False
                else:  # Horizontal collision
                    if keys[pygame.K_LEFT]:
                        self.rect.left = foe.rect.right
                    if keys[pygame.K_RIGHT]:
                        self.rect.right = foe.rect.left

    def jump(self):
        if self.on_ground:
            self.vel_y = -self.jump_speed
            self.on_ground = False

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class FloatingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Foe(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 2
        self.direction = 1

    def update(self,platforms, foes):
        self.rect.x += self.speed * self.direction
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.direction *= -1

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

        x = min(0, x)  # left side of the level
        x = max(-(self.width - SCREEN_WIDTH), x)  # right side of the level
        y = min(0, y)  # top of the level
        y = max(-(self.height - SCREEN_HEIGHT), y)  # bottom of the level

        self.camera = pygame.Rect(x, y, self.width, self.height)

def main():
    player = Player()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    platforms = pygame.sprite.Group()
    ground = Platform(0, SCREEN_HEIGHT - 50, 1600, 50)  # Single ground platform
    platforms.add(ground)
    all_sprites.add(ground)

    # Adding floating platforms
    floating_platform_positions = [
        (300, 400), (600, 300), (900, 450), (1200, 350)
    ]
    for pos in floating_platform_positions:
        platform = FloatingPlatform(pos[0], pos[1], 150, 20)
        platforms.add(platform)
        all_sprites.add(platform)

    foes = pygame.sprite.Group()
    foe_positions = [
        (400, SCREEN_HEIGHT - 100), (700, SCREEN_HEIGHT - 100),
        (1000, SCREEN_HEIGHT - 100), (1300, SCREEN_HEIGHT - 100),
        (350, 350), (650, 250), (950, 400), (1250, 300)
    ]
    for pos in foe_positions:
        foe = Foe(pos[0], pos[1], 50, 50)
        foes.add(foe)
        all_sprites.add(foe)

    camera = Camera(1600, SCREEN_HEIGHT)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()

        all_sprites.update(platforms, foes)
        player.update(platforms, foes)
        camera.update(player)

        screen.fill(WHITE)
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
