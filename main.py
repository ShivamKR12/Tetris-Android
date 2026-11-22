import sys
from random import randrange
import pygame

from settings import (
    RESOLUTION, GAME_RESOLUTION, FPS,
    resource_path
)
from game import TetrisGame

class App:
    """Core running application setup wrapper."""
    def __init__(self):
        pygame.init()

        info = pygame.display.Info()
        self.window_width = info.current_w if info.current_w else RESOLUTION[0]
        self.window_height = info.current_h if info.current_h else RESOLUTION[1]

        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        self.virtual_screen = pygame.Surface(RESOLUTION)
        self.game_screen = pygame.Surface(GAME_RESOLUTION)
        self.clock = pygame.time.Clock()

        # Set launcher icon
        try:
            icon_img = pygame.image.load(resource_path('img/Tetris-icon.png')).convert_alpha()
            pygame.display.set_icon(icon_img)
        except Exception:
            pass

        self.calculate_scale_and_margins()

        try:
            self.bg = pygame.image.load(resource_path('img/bg.jpg')).convert()
            self.game_bg = pygame.image.load(resource_path('img/bg2.jpg')).convert()
        except Exception:
            self.bg = pygame.Surface(RESOLUTION)
            self.bg.fill((20, 20, 30))
            self.game_bg = pygame.Surface(GAME_RESOLUTION)
            self.game_bg.fill((5, 5, 5))

        try:
            self.main_font = pygame.font.Font(resource_path('font/font.ttf'), 65)
            self.font = pygame.font.Font(resource_path('font/font.ttf'), 45)
        except Exception:
            self.main_font = pygame.font.SysFont('sans-serif', 65, bold=True)
            self.font = pygame.font.SysFont('sans-serif', 45)

        self.title_tetris = self.main_font.render('TETRIS', True, pygame.Color('darkorange'))
        self.title_score = self.font.render('score:', True, pygame.Color('green'))
        self.title_record = self.font.render('record:', True, pygame.Color('purple'))

        self.game = TetrisGame()

    def calculate_scale_and_margins(self):
        """Calculates dynamic scale targets to eliminate layout distortion."""
        scale_width = self.window_width / RESOLUTION[0]
        scale_height = self.window_height / RESOLUTION[1]
        self.scale = min(scale_width, scale_height)

        self.scaled_width = int(RESOLUTION[0] * self.scale)
        self.scaled_height = int(RESOLUTION[1] * self.scale)

        self.margin_x = (self.window_width - self.scaled_width) // 2
        self.margin_y = (self.window_height - self.scaled_height) // 2

    def run(self):
        running = True
        while running:
            running = self.game.process_input()
            
            for _ in range(self.game.lines_cleared_this_frame):
                pygame.time.wait(200)

            if not self.game.game_over_flag:
                self.game.update()
            else:
                for i_rect in self.game.grid:
                    pygame.draw.rect(self.game_screen, (randrange(30, 256), randrange(30, 256), randrange(30, 256)), i_rect)
                    self.virtual_screen.blit(self.game_screen, (20, 20))
                    
                    scaled_surface = pygame.transform.scale(self.virtual_screen, (self.scaled_width, self.scaled_height))
                    self.screen.fill((0, 0, 0))
                    self.screen.blit(scaled_surface, (self.margin_x, self.margin_y))
                    
                    pygame.display.flip()
                    self.clock.tick(200)
                self.game.reset_game()

            self.virtual_screen.blit(self.bg, (0, 0))
            self.virtual_screen.blit(self.game_screen, (20, 20))
            self.game_screen.blit(self.game_bg, (0, 0))

            self.game.draw(
                self.game_screen, self.virtual_screen, self.font, self.main_font,
                self.title_tetris, self.title_score, self.title_record
            )

            self.screen.fill((0, 0, 0))
            scaled_surface = pygame.transform.scale(self.virtual_screen, (self.scaled_width, self.scaled_height))
            self.screen.blit(scaled_surface, (self.margin_x, self.margin_y))
            
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = App()
    app.run()
