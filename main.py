import pygame
from copy import deepcopy
from random import choice, randrange
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource on Android """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# CONFIGURATION CONSTANTS
WIDTH, HEIGHT = 10, 20
TILE = 45
GAME_RESOLUTION = WIDTH * TILE, HEIGHT * TILE
RESOLUTION = 750, 940
FPS = 60

FIGURES_POS = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)]]

SCORES_TABLE = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}


class Tetromino:
    """Handles the creation, movement, and rotation of the falling piece."""
    def __init__(self):
        self.shape_pos = choice(FIGURES_POS)
        self.blocks = [pygame.Rect(x + WIDTH // 2, y + 1, 1, 1) for x, y in self.shape_pos]
        self.color = (randrange(30, 256), randrange(30, 256), randrange(30, 256))

    def move(self, dx, dy):
        for block in self.blocks:
            block.x += dx
            block.y += dy

    def rotate(self):
        center = self.blocks[0]
        for block in self.blocks:
            x = block.y - center.y
            y = block.x - center.x
            block.x = center.x - x
            block.y = center.y + y


class TetrisGame:
    """Manages the board state, scores, rules, and touch gestures."""
    def __init__(self):
        self.field = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(WIDTH) for y in range(HEIGHT)]
        self.figure_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
        
        self.score = 0
        self.lines_cleared_this_frame = 0
        self.record = self.get_record()
        
        self.animation_count = 0
        self.animation_speed = 60
        self.animation_limit = 2000
        
        self.current_piece = Tetromino()
        self.next_piece = Tetromino()
        
        # Touch mechanics variables
        self.touch_start_x = 0
        self.touch_start_y = 0
        self.is_tap = False
        
        self.game_over_flag = False

    def get_record(self):
        try:
            with open('record') as f:
                return f.readline().strip()
        except FileNotFoundError:
            with open('record', 'w') as f:
                f.write('0')
            return '0'

    def set_record(self):
        rec = max(int(self.record), self.score)
        with open('record', 'w') as f:
            f.write(str(rec))
        self.record = str(rec)

    def check_borders(self, blocks):
        for block in blocks:
            if block.x < 0 or block.x > WIDTH - 1:
                return False
            if block.y > HEIGHT - 1 or (block.y >= 0 and self.field[block.y][block.x]):
                return False
        return True

    def process_input(self):
        dx, rotate_piece = 0, False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_AC_BACK):
                return False
                
            elif event.type == pygame.FINGERDOWN:
                self.touch_start_x = event.x
                self.touch_start_y = event.y
                self.is_tap = True
                
            elif event.type == pygame.FINGERMOTION:
                diff_x = event.x - self.touch_start_x
                diff_y = event.y - self.touch_start_y
                
                if abs(diff_x) > 0.07:
                    dx = 1 if diff_x > 0 else -1
                    self.touch_start_x = event.x
                    self.is_tap = False
                    
                if diff_y > 0.07:
                    self.animation_limit = 100
                    self.is_tap = False
                    
            elif event.type == pygame.FINGERUP:
                if self.is_tap:
                    rotate_piece = True
                self.animation_limit = 2000

        # Handle requested horizontal movement
        if dx != 0:
            old_blocks = deepcopy(self.current_piece.blocks)
            self.current_piece.move(dx, 0)
            if not self.check_borders(self.current_piece.blocks):
                self.current_piece.blocks = old_blocks
                
        # Handle requested rotation
        if rotate_piece:
            old_blocks = deepcopy(self.current_piece.blocks)
            self.current_piece.rotate()
            if not self.check_borders(self.current_piece.blocks):
                self.current_piece.blocks = old_blocks
                
        return True

    def update(self):
        if self.game_over_flag:
            return

        # Advance down by tick speed
        self.animation_count += self.animation_speed
        if self.animation_count > self.animation_limit:
            self.animation_count = 0
            old_blocks = deepcopy(self.current_piece.blocks)
            self.current_piece.move(0, 1)
            
            # If hit bottom/grid structure
            if not self.check_borders(self.current_piece.blocks):
                for block in old_blocks:
                    self.field[block.y][block.x] = self.current_piece.color
                
                # Cycle onto next piece
                self.current_piece = self.next_piece
                self.next_piece = Tetromino()
                self.animation_limit = 2000
                
                # Check game over conditions
                for x in range(WIDTH):
                    if self.field[0][x]:
                        self.game_over_flag = True
                        self.set_record()
                        return

        # Check completed lines
        target_line = HEIGHT - 1
        self.lines_cleared_this_frame = 0
        for row in range(HEIGHT - 1, -1, -1):
            count = 0
            for x in range(WIDTH):
                if self.field[row][x]:
                    count += 1
                self.field[target_line][x] = self.field[row][x]
            if count < WIDTH:
                target_line -= 1
            else:
                self.animation_speed += 3
                self.lines_cleared_this_frame += 1
                
        self.score += SCORES_TABLE[self.lines_cleared_this_frame]

    def reset_game(self):
        self.field = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.animation_count, self.animation_speed, self.animation_limit = 0, 60, 2000
        self.score = 0
        self.game_over_flag = False
        self.current_piece = Tetromino()
        self.next_piece = Tetromino()

    def draw(self, game_screen, virtual_screen, font, main_font, title_tetris, title_score, title_record):
        # Draw background grids
        for i_rect in self.grid:
            pygame.draw.rect(game_screen, (40, 40, 40), i_rect, 1)
            
        # Draw current active figure blocks
        for block in self.current_piece.blocks:
            self.figure_rect.x = block.x * TILE
            self.figure_rect.y = block.y * TILE
            pygame.draw.rect(game_screen, self.current_piece.color, self.figure_rect)
            
        # Draw settled field blocks
        for y, row in enumerate(self.field):
            for x, col in enumerate(row):
                if col:
                    self.figure_rect.x, self.figure_rect.y = x * TILE, y * TILE
                    pygame.draw.rect(game_screen, col, self.figure_rect)
                    
        # Draw upcoming figure preview panel
        for block in self.next_piece.blocks:
            self.figure_rect.x = block.x * TILE + 380
            self.figure_rect.y = block.y * TILE + 185
            pygame.draw.rect(virtual_screen, self.next_piece.color, self.figure_rect)
            
        # Draw metadata fonts/titles
        virtual_screen.blit(title_tetris, (485, 40))
        virtual_screen.blit(title_score, (535, 780))
        virtual_screen.blit(font.render(str(self.score), True, pygame.Color('white')), (550, 840))
        virtual_screen.blit(title_record, (525, 650))
        virtual_screen.blit(font.render(self.record, True, pygame.Color('gold')), (550, 710))


class App:
    """Core running application setup wrapper."""
    def __init__(self):
        pygame.init()

        # Grab actual display screen size limits (especially critical on forced layouts/mobile)
        info = pygame.display.Info()
        self.window_width = info.current_w if info.current_w else RESOLUTION[0]
        self.window_height = info.current_h if info.current_h else RESOLUTION[1]

        # Initialize physical screen window display size completely
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        self.virtual_screen = pygame.Surface(RESOLUTION)
        self.game_screen = pygame.Surface(GAME_RESOLUTION)
        self.clock = pygame.time.Clock()

        # Pre-calculate aspect-ratio scaling dimensions
        self.calculate_scale_and_margins()

        # Load game media assets with safe fallbacks
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
        # Calculate aspect scaling based on boundaries
        scale_width = self.window_width / RESOLUTION[0]
        scale_height = self.window_height / RESOLUTION[1]
        self.scale = min(scale_width, scale_height)

        # Final size of virtual screen inside the window
        self.scaled_width = int(RESOLUTION[0] * self.scale)
        self.scaled_height = int(RESOLUTION[1] * self.scale)

        # Center layout offsets (Pillarbox / Letterbox math margins)
        self.margin_x = (self.window_width - self.scaled_width) // 2
        self.margin_y = (self.window_height - self.scaled_height) // 2

    def run(self):
        running = True
        while running:
            # Process Event Pipeline
            running = self.game.process_input()
            
            # Line clearance custom delays
            for _ in range(self.game.lines_cleared_this_frame):
                pygame.time.wait(200)

            # Update Application State Engine
            if not self.game.game_over_flag:
                self.game.update()
            else:
                # Run Game-Over layout effect loop internally
                for i_rect in self.game.grid:
                    pygame.draw.rect(self.game_screen, (randrange(30, 256), randrange(30, 256), randrange(30, 256)), i_rect)
                    self.virtual_screen.blit(self.game_screen, (20, 20))
                    
                    # Distort-free projection scaling engine inside animations
                    scaled_surface = pygame.transform.scale(self.virtual_screen, (self.scaled_width, self.scaled_height))
                    self.screen.fill((0, 0, 0)) # Clear window back buffer
                    self.screen.blit(scaled_surface, (self.margin_x, self.margin_y))
                    
                    pygame.display.flip()
                    self.clock.tick(200)
                self.game.reset_game()

            # Render frame scene pipeline
            self.virtual_screen.blit(self.bg, (0, 0))
            self.virtual_screen.blit(self.game_screen, (20, 20))
            self.game_screen.blit(self.game_bg, (0, 0))

            self.game.draw(
                self.game_screen, self.virtual_screen, self.font, self.main_font,
                self.title_tetris, self.title_score, self.title_record
            )

            # RENDER WITH DYNAMIC RESCALE PROJECTION Matrix
            self.screen.fill((0, 0, 0))  # Fill structural margins with clean black bars
            scaled_surface = pygame.transform.scale(self.virtual_screen, (self.scaled_width, self.scaled_height))
            self.screen.blit(scaled_surface, (self.margin_x, self.margin_y))
            
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = App()
    app.run()
