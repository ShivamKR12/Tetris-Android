import os
from copy import deepcopy
import pygame
from settings import WIDTH, HEIGHT, TILE, SCORES_TABLE
from tetromino import Tetromino

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
        record_file = os.path.join(os.path.expanduser("~"), ".tetris_record")
        try:
            if os.path.exists(record_file):
                with open(record_file, 'r', encoding='utf-8') as f:
                    return f.readline().strip() or '0'
            elif os.path.exists('record'):
                with open('record', 'r', encoding='utf-8') as f:
                    return f.readline().strip() or '0'
            return '0'
        except Exception:
            return '0'

    def set_record(self):
        rec = max(int(self.record), self.score)
        record_file = os.path.join(os.path.expanduser("~"), ".tetris_record")
        try:
            with open(record_file, 'w', encoding='utf-8') as f:
                f.write(str(rec))
        except Exception:
            try:
                with open('record', 'w', encoding='utf-8') as f:
                    f.write(str(rec))
            except Exception:
                pass
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
