import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
GAME_WIDTH = SCREEN_WIDTH * 8  # Extended game area
FPS = 60

# Colors
CYAN = (0, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_YELLOW = (204, 204, 0)

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Bros")

# Clock and Font
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 36)

def display_message(message):
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()

def game_over_screen():
    display_message("Game Over! Press R to Restart or Q to Quit")
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                    main()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5
        self.jump_speed = 20
        self.gravity = 0.5
        self.vel_y = 0
        self.on_ground = False
        self.on_moving_platform = None

    def update(self, platforms, foes):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        self.on_ground = False
        self.on_moving_platform = None
        self.check_platforms(platforms)
        self.check_foes(foes)

    def check_platforms(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y > 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.on_ground = True
                if isinstance(platform, MovingPlatform):
                    self.on_moving_platform = platform

    def check_foes(self, foes):
        foe_hit_list = pygame.sprite.spritecollide(self, foes, False)
        for foe in foe_hit_list:
            if self.vel_y > 0 and self.rect.bottom <= foe.rect.top + self.vel_y:
                self.vel_y = -self.jump_speed
                foe.kill()
                self.on_ground = False
            else:
                self.kill()
                game_over_screen()

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

class MovingPlatform(Platform):
    def __init__(self, x, y, width, height, boundary_left, boundary_right, speed):
        super().__init__(x, y, width, height)
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
        self.image = pygame.Surface((width, height))
        self.image.fill(DARK_YELLOW)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 2
        self.direction = 1
        self.gravity = 0.5
        self.vel_y = 0
        self.on_ground = False
        self.min_x = min_x
        self.max_x = max_x
        self.on_moving_platform = None

    def update(self, platforms, _):
        self.rect.x += self.speed * self.direction
        if self.rect.x < self.min_x or self.rect.x > self.max_x:
            self.direction *= -1

        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        self.on_ground = False
        self.on_moving_platform = None
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y > 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.on_ground = True
                if isinstance(platform, MovingPlatform):
                    self.on_moving_platform = platform

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
        y = min(0, y)
        y = max(-(self.height - SCREEN_HEIGHT), y)
        self.camera = pygame.Rect(x, y, self.width, self.height)

def main():
    player = Player()
    platforms = pygame.sprite.Group()
    moving_platforms = pygame.sprite.Group()
    foes = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group(player)

    # Ground platform
    ground = Platform(0, SCREEN_HEIGHT - 50, GAME_WIDTH, 50)
    platforms.add(ground)
    all_sprites.add(ground)

    # Static platforms
    static_platforms = [
        (300, 750, 200, 20), (800, 600, 200, 20), (1400, 450, 200, 20),
        (1800, 700, 200, 20), (2200, 500, 200, 20), (2600, 350, 200, 20),
        (3000, 600, 200, 20), (3400, 750, 200, 20), (3800, 500, 200, 20),
        (4200, 650, 200, 20), (4600, 300, 200, 20), (5000, 550, 200, 20),
        (5400, 400, 200, 20), (5800, 250, 200, 20), (6200, 500, 200, 20),
        (6600, 750, 200, 20)
    ]
    for x, y, w, h in static_platforms:
        plat = Platform(x, y, w, h)
        platforms.add(plat)
        all_sprites.add(plat)

    # Moving platforms
    moving_platform_details = [
        (500, 800, 300, 20, 400, 800, 2), (1200, 300, 300, 20, 1100, 1500, 3),
        (2300, 450, 300, 20, 2200, 2600, 2), (3400, 500, 300, 20, 3300, 3700, 4),
        (4500, 700, 300, 20, 4400, 4800, 2), (5700, 400, 300, 20, 5600, 6000, 3)
    ]
    for x, y, w, h, min_x, max_x, speed in moving_platform_details:
        mplat = MovingPlatform(x, y, w, h, min_x, max_x, speed)
        moving_platforms.add(mplat)
        platforms.add(mplat)
        all_sprites.add(mplat)

    # Foes with specific movement ranges
    foe_positions = [
        (300, SCREEN_HEIGHT - 150, 200, 600), (1600, 250, 1500, 1700),
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
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        # Update all sprites
        for sprite in all_sprites:
            if isinstance(sprite, Player) or isinstance(sprite, Foe):
                sprite.update(platforms, foes)
            elif isinstance(sprite, MovingPlatform):
                sprite.update()

        # Move entities with their platforms
        for platform in moving_platforms:
            delta_x = platform.update()
            for entity in [player] + [foe for foe in foes]:
                if entity.on_moving_platform == platform:
                    entity.rect.x += delta_x * 2

        camera.update(player)

        screen.fill(CYAN)
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
