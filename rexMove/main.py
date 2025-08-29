import pygame
import random
import sys
import os

pygame.mixer.init()

WIDTH, HEIGHT = 600, 800
FPS = 60
GROUND_HEIGHT = 90


def load_image(path, size=None, fallback_color=(200, 200, 200)):
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    surf = pygame.Surface((64, 64), pygame.SRCALPHA)
    surf.fill(fallback_color)
    return surf

class Dino(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = [
            load_image("assets/images/dino_run1.png", size=(96, 64))
        ]
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.hitbox = self.rect.inflate(-20, -10)
        self.speed = 320
        self.anim_timer = 0
        self.anim_speed = 0.12
        self.facing = "right"

    def update(self, keys, dt):
        dx = 0
        if keys[pygame.K_a]:
            dx -= self.speed * dt
            self.facing = "left"
        elif keys[pygame.K_d]:
            dx += self.speed * dt
            self.facing = "right"

        self.rect.x += int(dx)
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)
        self.rect.bottom = HEIGHT - GROUND_HEIGHT
        self.hitbox.center = self.rect.center

        if dx != 0:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]
                if self.facing == "left":
                    self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.image = self.frames[0]
            if self.facing == "left":
                self.image = pygame.transform.flip(self.image, True, False)

class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("assets/images/meteor.png", size=(64, 128))
        self.rect = self.image.get_rect(midtop=(random.randint(50, WIDTH-50), -150))
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.speed_y = random.uniform(260, 520)
        self.speed_x = random.uniform(-60, 60)
        self.hitbox = self.rect.inflate(-10, -10)

    def update(self, dt):
        self.pos_y += self.speed_y * dt
        self.pos_x += self.speed_x * dt
        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)
        self.hitbox.center = self.rect.center
        if self.rect.top > HEIGHT + 50:
            self.kill()

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Rex_Move")
        self.clock = pygame.time.Clock()

        # High score
        self.highscore_file = "saves/save.txt"
        os.makedirs("saves", exist_ok=True)
        self.highscore = self.load_highscore()

        # Background
        self.bg = load_image("assets/images/bg.png", size=(WIDTH, HEIGHT))
        self.game_over_bg = load_image("assets/images/game_over.png", size=(WIDTH, HEIGHT))

        # Buttons
        self.restart_button = load_image("assets/images/Restart.png")
        self.quit_button = load_image("assets/images/Quit.png")
        self.restart_rect = self.restart_button.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))
        self.quit_rect = self.quit_button.get_rect(center=(WIDTH//2, HEIGHT//2 + 180))

        # Sprites
        self.all_sprites = pygame.sprite.Group()
        self.meteors = pygame.sprite.Group()
        self.dino = Dino(WIDTH//2, HEIGHT - GROUND_HEIGHT)
        self.all_sprites.add(self.dino)

        self.score = 0
        self.font = pygame.font.Font("assets/Anton-Regular.ttf", 40)
        self.spawn_timer = 0.8
        self.spawn_accumulator = 0

        # Sounds
        self.bg_music_file = "assets/sounds/bg_music.mp3"
        if os.path.exists(self.bg_music_file):
            pygame.mixer.music.load(self.bg_music_file)
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)

        self.button_click_sound = pygame.mixer.Sound("assets/sounds/button_click.wav")
        self.button_click_sound.set_volume(0.5)

        self.game_over_voice_sound = pygame.mixer.Sound("assets/sounds/game_over.wav")
        self.game_over_voice_sound.set_volume(0.6)

        self.game_over_bg_music = pygame.mixer.Sound("assets/sounds/game_over_bg.wav")
        self.game_over_bg_music.set_volume(0.3)

    def load_highscore(self):
        if os.path.exists(self.highscore_file):
            with open(self.highscore_file, "r") as f:
                try:
                    return int(f.read())
                except:
                    return 0
        return 0

    def save_highscore(self):
        with open(self.highscore_file, "w") as f:
            f.write(str(self.highscore))

    # Spawn meteors
    def spawn_meteor(self):
        meteor = Meteor()
        self.all_sprites.add(meteor)
        self.meteors.add(meteor)

    # Main loop
    def run(self):
        game_over = False
        played_game_over_sound = False

        while True:
            dt = self.clock.tick(FPS) / 1000
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if game_over and event.type == pygame.MOUSEBUTTONDOWN:
                    if self.restart_rect.collidepoint(mouse_pos):
                        self.button_click_sound.play()
                        self.game_over_bg_music.stop()
                        self.game_over_voice_sound.stop()
                        self.__init__()
                        return self.run()
                    elif self.quit_rect.collidepoint(mouse_pos):
                        self.button_click_sound.play()
                        pygame.quit()
                        sys.exit()

            keys = pygame.key.get_pressed()

            # Game logic
            if not game_over:
                self.spawn_accumulator += dt
                if self.spawn_accumulator >= self.spawn_timer:
                    self.spawn_meteor()
                    self.spawn_accumulator = 0

                self.dino.update(keys, dt)
                for meteor in self.meteors:
                    meteor.update(dt)

                # Collision detection
                for meteor in self.meteors:
                    if self.dino.hitbox.colliderect(meteor.hitbox):
                        if not game_over:
                            game_over = True
                            pygame.mixer.music.stop()  
                            self.game_over_voice_sound.play() 
                            self.game_over_bg_music.play(-1)
                        break
                        

                # Update score
                self.score += dt * 10

            # Draw
            self.screen.blit(self.bg, (0, 0))
            self.all_sprites.draw(self.screen)

            # Score on top left during gameplay
            if not game_over:
                score_text = self.font.render(f"Score: {int(self.score)}", True, (200, 200, 90))
                self.screen.blit(score_text, (10, 10))

            # Game Over screen
            if game_over:
                self.screen.blit(self.game_over_bg, (0, 0))

                # Update high score
                if int(self.score) > self.highscore:
                    self.highscore = int(self.score)
                    self.save_highscore()

                game_over_font = pygame.font.Font("assets/Anton-Regular.ttf", 28)
                score_text = game_over_font.render(f"Your Score : {int(self.score)}", True, (87, 55, 6))
                score_rect = score_text.get_rect(topleft=(150, HEIGHT//2 - 110))
                self.screen.blit(score_text, score_rect)

                # High score
                high_text = game_over_font.render(f"High Score : {self.highscore}", True, (87, 55, 6))
                high_rect = high_text.get_rect(topleft=(150, HEIGHT//2 - 55))
                self.screen.blit(high_text, high_rect)

                # Hover effect on buttons
                for btn, rect in [(self.restart_button, self.restart_rect), (self.quit_button, self.quit_rect)]:
                    hovered = rect.collidepoint(mouse_pos)
                    if hovered:
                        hover_img = pygame.transform.scale(btn, (int(rect.width * 1.1), int(rect.height * 1.1)))
                        hover_rect = hover_img.get_rect(center=rect.center)
                        self.screen.blit(hover_img, hover_rect)
                    else:
                        self.screen.blit(btn, rect)

            pygame.display.flip()

if __name__ == "__main__":
    Game().run()
