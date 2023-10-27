"""
Intermediate #7	16x16	256	40	15.6%

------> x, cols
|
|
v
y, rows

"""

import random
import pygame


class Tile:
    def __init__(self, pos: tuple, number: int, is_bomb: bool):
        self.r, self.c = pos
        self.adjacent_bombs = number
        self.is_bomb = is_bomb
        
        self.is_flagged = False
        self.is_revealed = False


class Board:
    def __init__(self, bombs: int, tiles: tuple):
        self.bombs = bombs 
        self.rows, self.cols = tiles  # e.g. (16, 16)

        self.grid = []      # list<list<Tile>>>
        self.bomb_pos = []  # list<tuple<int, int>>
       
        self.has_bomb_visible = False
        self.marked_bombs_count = 0

        self.construct_grid()

    def make_bomb_positions(self):
        while len(self.bomb_pos) < self.bombs:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            if (r, c) not in self.bomb_pos:
                self.bomb_pos += [(r, c)]

    def get_tile(self, r: int, c: int):
        return self.grid[r][c]
    
    def get_adjacent_pos(self, r: int, c: int):
        adjacent_pos = []

        for row in range(r - 1, r + 2):
            for col in range(c - 1, c + 2):
                if 0 <= row < self.rows and 0 <= col < self.cols:
                    adjacent_pos += [(row, col)]

        adjacent_pos.remove((r, c))

        return adjacent_pos
        
    def count_adjacent_bombs(self, r: int, c: int):
        counter = 0

        for pos in self.get_adjacent_pos(r, c):
            if pos in self.bomb_pos:
                counter += 1
        return counter

    def construct_grid(self):
        self.make_bomb_positions()
        
        for r in range(self.rows):
            grid_row = []
            for c in range(self.cols):
                n = 0
                is_bomb = True
                if (r, c) not in self.bomb_pos:
                    n = self.count_adjacent_bombs(r, c)
                    is_bomb = False

                t = Tile((r, c), n, is_bomb)
                grid_row += [t]
            self.grid += [grid_row]
        print("Grid constructed.")
    
    def clear_blanks(self, r: int, c: int):
        for r, c in self.get_adjacent_pos(r, c):
            t = self.get_tile(r, c)
            if not t.is_bomb and not t.is_revealed:
                t.is_revealed = True
                if not t.adjacent_bombs:
                    self.clear_blanks(t.r, t.c)

    def toggle_flag(self, tile: Tile):
        tile.is_flagged = not tile.is_flagged

        if tile.is_flagged:
            self.marked_bombs_count += 1
        else:
            self.marked_bombs_count -= 1

        
class Painter:
    def __init__(self, board: Board, screen: pygame.Surface):
        self.board = board
        self.screen = screen
        self.width, self.height = self.screen.get_size()
        self.tile_size = 37
        self.start_height = int(self.height - self.tile_size * self.board.rows)
        self.draw_board()

    def get_clicked_tile(self, c: int, r: int):
        r = (r - self.start_height) // self.tile_size
        c = c // self.tile_size

        if not (0 <= r < self.board.rows) or not (0 <= c < self.board.cols):
            print("out of range: ", (r, c))
            exit()

        return self.board.get_tile(r, c)
    
    def is_grid_clicked(self, y):
        return self.start_height < y


    def draw_board(self):
        """ main drawing loop """
        LIGHT_SLATE_GREY = (119,136,153)
        RED = (220, 20, 60)
        BLACK = (0, 0, 0)
        font = pygame.font.SysFont('calibri', 14)  
        self.screen.fill(0)
        RESTART_TEXT = "click 'r' to restart"
        bombs_marked_text = f"bombs marked: {self.board.marked_bombs_count}/{self.board.bombs}"
        
        text = font.render(bombs_marked_text, True, LIGHT_SLATE_GREY)
        text_rect = text.get_rect()
        text_rect.center = (100, self.start_height - 10)
        self.screen.blit(text, text_rect)

        if self.board.has_bomb_visible:
            text = font.render(RESTART_TEXT, True, LIGHT_SLATE_GREY)
            text_rect = text.get_rect()
            text_rect.center = (100, self.start_height - 40)
            self.screen.blit(text, text_rect)
        pygame.display.flip()
        # draw grid
        for row in self.board.grid:
            
            for col in range(self.board.cols):
                text = font.render("", True, LIGHT_SLATE_GREY)
                color = LIGHT_SLATE_GREY
                tile: Tile = row[col]

                if tile.is_bomb and tile.is_revealed:
                    color = RED

                tile_x = tile.c * self.tile_size
                tile_y = self.start_height + tile.r*self.tile_size

                # draw tile background
                t = pygame.Rect(tile_x, tile_y, self.tile_size, self.tile_size), 
                w = (int) (not tile.is_revealed)  # 0 --> fill, 1 --> border
                pygame.draw.rect(self.screen, color, t, width=w)
                
                # mark number on revealed + non bomb tile
                if not tile.is_bomb and tile.is_revealed and tile.adjacent_bombs:
                    text = font.render(str(tile.adjacent_bombs), True, BLACK)

                # mark 'B' as bomb flags
                if not tile.is_revealed and tile.is_flagged:
                    text = font.render("B", True, LIGHT_SLATE_GREY)
                
                # put marking on tile
                text_rect = text.get_rect()
                text_rect.center = (tile_x + self.tile_size // 2, tile_y + self.tile_size // 2)
                self.screen.blit(text, text_rect)
                    
        
        pygame.display.flip()

def main():
    pygame.init()
    width, height = 592, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Minesweeper")
    running = True
    bombs = 40
    tiles = (16, 16)
    b = Board(bombs, tiles)
    p = Painter(b, screen)

    while running:
    
        for e in pygame.event.get():
            x, y = pygame.mouse.get_pos()
            LEFT_CLICK = (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and p.is_grid_clicked(y))
            RIGHT_CLICK = (e.type == pygame.MOUSEBUTTONDOWN and e.button == 3 and p.is_grid_clicked(y))
            RESTART = (e.type == pygame.KEYDOWN and e.key == pygame.K_r and b.has_bomb_visible)
            

            if e.type == pygame.QUIT:
                running = False

            elif RESTART:
                main()
            
            elif LEFT_CLICK:
                clicked = p.get_clicked_tile(x, y)

                if not clicked.is_revealed:
                    clicked.is_revealed = True
                    
                if not clicked.adjacent_bombs and not clicked.is_bomb:
                    b.clear_blanks(clicked.r, clicked.c)

                if clicked.is_bomb:
                    b.has_bomb_visible = True

            elif RIGHT_CLICK:
                clicked = p.get_clicked_tile(x, y)

                if not clicked.is_revealed:
                    b.toggle_flag(clicked)
                    
        p.draw_board()
    
    pygame.quit()

if __name__ == "__main__":
    main()