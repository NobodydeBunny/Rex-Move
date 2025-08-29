from main import Game
import pygame
import sys
import os

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rex Move")

start_bg = pygame.image.load("assets/images/Home.png")
start_button = pygame.image.load("assets/images/Start.png")

start_bg = pygame.transform.scale(start_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
button_width, button_height = start_button.get_size()
button_x = SCREEN_WIDTH // 2 - button_width // 2
button_y = 525 - button_height // 2

button_click_sound = pygame.mixer.Sound("assets/sounds/button_click.wav")
button_click_sound.set_volume(0.5)

bg_music_file = "assets/sounds/start_bg.mp3"
if os.path.exists(bg_music_file):
    pygame.mixer.music.load(bg_music_file)
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)

def draw_start_screen():
    mouse_pos = pygame.mouse.get_pos()
    
    hovered = (button_x <= mouse_pos[0] <= button_x + button_width) and \
                (button_y <= mouse_pos[1] <= button_y + button_height)
    
    screen.blit(start_bg, (0, 0))
    
    if hovered:
        # Scale up 10% when hovering
        hover_img = pygame.transform.scale(start_button,
                                           (int(button_width * 1.1),
                                            int(button_height * 1.1)))
        hover_rect = hover_img.get_rect(center=(button_x + button_width//2,
                                                button_y + button_height//2))
        screen.blit(hover_img, hover_rect)
    else:
        screen.blit(start_button, (button_x, button_y))
    
    pygame.display.update()

def start_screen_loop():
    while True:
        draw_start_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                hovered = (button_x <= mouse_pos[0] <= button_x + button_width) and \
                          (button_y <= mouse_pos[1] <= button_y + button_height)
                if hovered:
                    button_click_sound.play()  # Play click sound
                    Game().run()  
                    return

if __name__ == "__main__":
    start_screen_loop()
    print("Game would start here...")
