#!/usr/bin/env python3
"""
Tetris for the terminal | Terminetris | Python curses edition
Controls: ← → move | ↑ rotate | ↓ soft drop | SPACE hard drop | P pause | Q quit
"""

import curses
import random
import time

# Tetromino definitions (shapes × rotations) 

TETROMINOES = {
    'I': [
        [(0,1),(1,1),(2,1),(3,1)],
        [(1,0),(1,1),(1,2),(1,3)],
    ],
    'O': [
        [(0,0),(1,0),(0,1),(1,1)],
    ],
    'T': [
        [(0,1),(1,0),(1,1),(1,2)],
        [(0,1),(1,1),(2,1),(1,0)],
        [(1,0),(1,1),(1,2),(2,1)],
        [(0,1),(1,1),(2,1),(1,2)],
    ],
    'S': [
        [(0,1),(0,2),(1,0),(1,1)],
        [(0,0),(1,0),(1,1),(2,1)],
    ],
    'Z': [
        [(0,0),(0,1),(1,1),(1,2)],
        [(0,1),(1,0),(1,1),(2,0)],
    ],
    'J': [
        [(0,0),(1,0),(1,1),(1,2)],
        [(0,1),(1,1),(2,1),(2,0)],
        [(1,0),(1,1),(1,2),(2,2)],
        [(0,0),(0,1),(1,0),(2,0)],
    ],
    'L': [
        [(0,2),(1,0),(1,1),(1,2)],
        [(0,0),(0,1),(1,1),(2,1)],
        [(1,0),(1,1),(1,2),(2,0)],
        [(0,1),(1,1),(2,1),(2,2)],
    ],
}

COLORS = {
    'I': 1, 'O': 2, 'T': 3, 'S': 4, 'Z': 5, 'J': 6, 'L': 7,
}

BOARD_W, BOARD_H = 10, 20
BLOCK = '██'
EMPTY = '  '

LEVEL_SPEEDS = [0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.25, 0.2, 0.15, 0.1]
POINTS = [0, 100, 300, 500, 800]  # 0-4 lines cleared


class Tetris:
    def __init__(self):
        self.board = [[0] * BOARD_W for _ in range(BOARD_H)]
        self.score = 0
        self.lines = 0
        self.level = 0
        self.paused = False
        self.game_over = False
        self.bag = []
        self.current = None
        self.next_piece = None
        self.cx = self.cy = 0       # (to remember) it determines current piece position (row, col)
        self.crot = 0               # (to remember) it determines current rotation index
        self._spawn()

    # Piece bag 
  
    def _refill_bag(self):
        self.bag = list(TETROMINOES.keys())
        random.shuffle(self.bag)

    def _next_from_bag(self):
        if not self.bag:
            self._refill_bag()
        return self.bag.pop()

    # Spawn
  
    def _spawn(self):
        if self.next_piece is None:
            self.next_piece = self._next_from_bag()
        self.current = self.next_piece
        self.next_piece = self._next_from_bag()
        self.crot = 0
        shape = TETROMINOES[self.current][self.crot]
        self.cy = 0
        self.cx = BOARD_W // 2 - 2
        if self._collides(self.cy, self.cx, shape):
            self.game_over = True

    # Collision
    
    def _collides(self, row, col, shape):
        for r, c in shape:
            nr, nc = row + r, col + c
            if nr < 0 or nr >= BOARD_H or nc < 0 or nc >= BOARD_W:
                return True
            if self.board[nr][nc]:
                return True
        return False

    # Movement 
    
    def move(self, dr, dc):
        shape = TETROMINOES[self.current][self.crot]
        if not self._collides(self.cy + dr, self.cx + dc, shape):
            self.cy += dr
            self.cx += dc
            return True
        return False

    def rotate(self):
        rots = TETROMINOES[self.current]
        new_rot = (self.crot + 1) % len(rots)
        shape = rots[new_rot]
        # hm, try normal, then wall-kick ±1
        for kick in [0, -1, 1, -2, 2]:
            if not self._collides(self.cy, self.cx + kick, shape):
                self.crot = new_rot
                self.cx += kick
                return

    def hard_drop(self):
        shape = TETROMINOES[self.current][self.crot]
        while not self._collides(self.cy + 1, self.cx, shape):
            self.cy += 1
        self._lock()

    # Lock & clear
    
    def _lock(self):
        shape = TETROMINOES[self.current][self.crot]
        color = COLORS[self.current]
        for r, c in shape:
            self.board[self.cy + r][self.cx + c] = color
        cleared = self._clear_lines()
        self.score += POINTS[cleared] * (self.level + 1)
        self.lines += cleared
        self.level = min(self.lines // 10, len(LEVEL_SPEEDS) - 1)
        self._spawn()

    def _clear_lines(self):
        full = [r for r in range(BOARD_H) if all(self.board[r])]
        for r in full:
            del self.board[r]
            self.board.insert(0, [0] * BOARD_W)
        return len(full)

    def tick(self):
        """Gravity drop called by the game loop."""
        shape = TETROMINOES[self.current][self.crot]
        if self._collides(self.cy + 1, self.cx, shape):
            self._lock()
        else:
            self.cy += 1

    # Ghost piece
    
    def ghost_row(self):
        shape = TETROMINOES[self.current][self.crot]
        gy = self.cy
        while not self._collides(gy + 1, self.cx, shape):
            gy += 1
        return gy


# Renderer

def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN,    -1)  # I
    curses.init_pair(2, curses.COLOR_YELLOW,  -1)  # O
    curses.init_pair(3, curses.COLOR_MAGENTA, -1)  # T
    curses.init_pair(4, curses.COLOR_GREEN,   -1)  # S
    curses.init_pair(5, curses.COLOR_RED,     -1)  # Z
    curses.init_pair(6, curses.COLOR_BLUE,    -1)  # J
    curses.init_pair(7, curses.COLOR_WHITE,   -1)  # L
    curses.init_pair(8, curses.COLOR_BLACK,   curses.COLOR_WHITE)  # ghost


def safe_addstr(win, y, x, text, attr=0):
    try:
        win.addstr(y, x, text, attr)
    except curses.error:
        pass


def draw_board(win, game, origin_r, origin_c):
    ghost_r = game.ghost_row()
    ghost_shape = TETROMINOES[game.current][game.crot]
    ghost_cells = {(ghost_r + r, game.cx + c) for r, c in ghost_shape}
    cur_cells   = {(game.cy  + r, game.cx + c) for r, c in ghost_shape}
    cur_color   = COLORS[game.current]

    for row in range(BOARD_H):
        for col in range(BOARD_W):
            sy = origin_r + row
            sx = origin_c + col * 2
            if (row, col) in cur_cells:
                safe_addstr(win, sy, sx, BLOCK, curses.color_pair(cur_color) | curses.A_BOLD)
            elif (row, col) in ghost_cells:
                safe_addstr(win, sy, sx, '░░', curses.color_pair(8))
            elif game.board[row][col]:
                safe_addstr(win, sy, sx, BLOCK, curses.color_pair(game.board[row][col]))
            else:
                safe_addstr(win, sy, sx, EMPTY)


def draw_border(win, origin_r, origin_c):
    # top
    safe_addstr(win, origin_r - 1, origin_c - 1, '┌' + '──' * BOARD_W + '┐')
    # sides
    for r in range(BOARD_H):
        safe_addstr(win, origin_r + r, origin_c - 1, '│')
        safe_addstr(win, origin_r + r, origin_c + BOARD_W * 2, '│')
    # bottom
    safe_addstr(win, origin_r + BOARD_H, origin_c - 1, '└' + '──' * BOARD_W + '┘')


def draw_sidebar(win, game, origin_r, sidebar_c):
    def label(text, r):
        safe_addstr(win, origin_r + r, sidebar_c, text)

    label('TETRIS', 0)
    label('──────────', 1)
    label(f'Score', 3)
    label(f'{game.score:>10}', 4)
    label(f'Lines', 6)
    label(f'{game.lines:>10}', 7)
    label(f'Level', 9)
    label(f'{game.level + 1:>10}', 10)
    label('──────────', 12)
    label('  NEXT', 13)

    # The next piece preview
    
    if game.next_piece:
        shape = TETROMINOES[game.next_piece][0]
        color = COLORS[game.next_piece]
        preview = [[False]*4 for _ in range(4)]
        for r, c in shape:
            if r < 4 and c < 4:
                preview[r][c] = True
        for r in range(4):
            for c in range(4):
                sy = origin_r + 15 + r
                sx = sidebar_c + c * 2
                if preview[r][c]:
                    safe_addstr(win, sy, sx, BLOCK, curses.color_pair(color) | curses.A_BOLD)
                else:
                    safe_addstr(win, sy, sx, EMPTY)

    label('──────────', 20)
    label('← → move', 22)
    label('↑  rotate', 23)
    label('↓  drop', 24)
    label('SPC hard', 25)
    label('P   pause', 26)
    label('Q   quit', 27)


def draw_overlay(win, text, height, width):
    lines = text.strip().split('\n')
    start_r = height // 2 - len(lines) // 2
    for i, line in enumerate(lines):
        safe_addstr(win, start_r + i, width // 2 - len(line) // 2, line, curses.A_BOLD)


# Main game loop
def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    init_colors()

    height, width = stdscr.getmaxyx()
    # board origin centered
    origin_r = (height - BOARD_H) // 2
    origin_c = (width - BOARD_W * 2) // 2 - 2  # leave room for border
    sidebar_c = origin_c + BOARD_W * 2 + 4

    game = Tetris()
    last_tick = time.time()

    while True:
        now = time.time()
        speed = LEVEL_SPEEDS[game.level]

        # Input
        
        key = stdscr.getch()
        if key == ord('q') or key == ord('Q'):
            break
        if key == ord('p') or key == ord('P'):
            game.paused = not game.paused
        if not game.paused and not game.game_over:
            if key == curses.KEY_LEFT:
                game.move(0, -1)
            elif key == curses.KEY_RIGHT:
                game.move(0, 1)
            elif key == curses.KEY_DOWN:
                game.move(1, 0)
            elif key == curses.KEY_UP:
                game.rotate()
            elif key == ord(' '):
                game.hard_drop()

        # Gravity tick
        
        if not game.paused and not game.game_over:
            if now - last_tick >= speed:
                game.tick()
                last_tick = now

        # Draw
        
        stdscr.erase()
        draw_border(stdscr, origin_r, origin_c)
        draw_board(stdscr, game, origin_r, origin_c)
        draw_sidebar(stdscr, game, origin_r, sidebar_c)

        if game.paused:
            draw_overlay(stdscr, '\n  ⏸  PAUSED  \n  P to resume \n', height, width)
        if game.game_over:
            draw_overlay(stdscr, f'\n  GAME OVER  \n  Score: {game.score}  \n  Q to quit  \n', height, width)

        stdscr.refresh()
        time.sleep(0.033)  # ~30 fps


if __name__ == '__main__':
    curses.wrapper(main)
