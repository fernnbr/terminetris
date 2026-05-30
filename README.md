# Terminetris | Terminal Edition
*My Tetris for Terminals. A fully-featured Tetris game for the terminal, written in Python. It feels so nostalgic!* 
Oh and it uses the built-in `curses` library. ;) (and no external dependencies required.) 

*Well...I really LOVE tetris. That's why I created this tetris for terminal, to play when I am... bored or without internet.* 

---

## ||| Requirements

| Requirement | Details |
|---|---|
| Python | 3.6 or higher |
| OS | macOS, Linux, or any Unix-like system with a terminal |
| Library | `curses` (included in Python's standard library) |
| Terminal size | At least **24 rows × 60 columns** recommended |

> **Psiu, Windows users:** `curses` is not natively available on Windows.
> </br> Please, use WSL (Windows Subsystem for Linux) or install `windows-curses` via pip.

---

## ||| Installation & Running

No installation needed. Just download `tetris.py` and run:

```zsh
python3 terminetris.py
```

To make it executable directly:

```zsh
chmod +x terminetris.py
./terminetris.py
```

---

## ||| Controls

| Key | Action |
|---|---|
| `←` Arrow | Move piece left |
| `→` Arrow | Move piece right |
| `↑` Arrow | Rotate piece clockwise |
| `↓` Arrow | Soft drop (accelerate fall) |
| `Space` | Hard drop (instant fall) |
| `P` | Pause / Resume |
| `Q` | Quit game |

---

## ||| Gameplay

### ||| Objective

Clear as many horizontal lines as possible by filling them completely with blocks. 
</br> Lines disappear when full, and the board shifts down. 
</br> The game ends when a new piece cannot spawn at the top of the board. 
</br> Simple, like tetris. 

### ||| Scoring

Points are awarded based on how many lines are cleared at once, multiplied by the current level:

| Lines Cleared | Base Points |
|---|---|
| 1 (Single) | 100 |
| 2 (Double) | 300 |
| 3 (Triple) | 500 |
| 4 (Tetris) | 800 |

**Formula:** `Points = Base Points × (Level + 1)`

### ||| Levels

- The level increases every **10 lines** cleared.
- Higher levels increase the gravity speed (pieces fall faster).
- Maximum level: **10**.

</br>

| Level | Drop interval |
|---|---|
| 1 | 0.8s |
| 2 | 0.7s |
| 3 | 0.6s |
| 4 | 0.5s |
| 5 | 0.4s |
| 6 | 0.3s |
| 7 | 0.25s |
| 8 | 0.2s |
| 9 | 0.15s |
| 10 | 0.1s |

---

## ||| Features

### ||| All 7 Terminetris

</br>

| Piece | Shape | Color |
|---|---|---|
| I | Four in a row | Cyan |
| O | 2×2 square | Yellow |
| T | T-shape | Magenta |
| S | S-skew | Green |
| Z | Z-skew | Red |
| J | J-shape | Blue |
| L | L-shape | White |

### ||| 7-Bag Randomizer

Pieces are drawn from a shuffled bag containing one of each terminetris. 
</br> When the bag is exhausted, a new shuffled bag is created. 

### ||| Ghost Piece

A faint `░░` shadow is projected below the active piece showing exactly where it will land. 
</br> This helps with precise placement, especially at higher speeds. hehehe

### ||| Wall Kicks

When rotating near a wall or other blocks, the game attempts to shift the piece left or right (up to 2 cells) to make the rotation valid. </br> This prevents frustrating failed rotations at the edges of the board. (I reckon) 

### ||| Next Piece Preview

YAYYYY. The sidebar shows the upcoming piece so you can plan your moves in advance.

---

## ||| Code Structure

```
tetris.py
│
├── TETROMINOES         – Dict of all 7 pieces with rotation states
├── COLORS              – Mapping of piece names to curses color pairs
├── LEVEL_SPEEDS        – Drop interval (seconds) per level
├── POINTS              – Score table for line clears
│
├── class Tetris        – Game state and logic
│   ├── __init__        – Initializes board, score, and spawns first piece
│   ├── _refill_bag     – Shuffles a new 7-bag
│   ├── _next_from_bag  – Draws next piece from the bag
│   ├── _spawn          – Places a new piece at the top of the board
│   ├── _collides       – Checks if a shape overlaps walls or locked blocks
│   ├── move            – Moves the current piece by (dr, dc)
│   ├── rotate          – Rotates the piece with wall-kick attempts
│   ├── hard_drop       – Instantly drops the piece to the lowest valid row
│   ├── _lock           – Locks the piece, clears lines, updates score
│   ├── _clear_lines    – Removes full rows and shifts board down
│   ├── tick            – Applies gravity (called each frame interval)
│   └── ghost_row       – Calculates the lowest valid row for the ghost
│
├── init_colors         – Sets up curses color pairs
├── safe_addstr         – Wrapper to suppress curses out-of-bounds errors
├── draw_board          – Renders the play field, active piece, and ghost
├── draw_border         – Draws the Unicode box border around the board
├── draw_sidebar        – Renders score, level, lines, next piece, and help
├── draw_overlay        – Renders centered text (PAUSED / GAME OVER)
│
└── main                – Game loop: input → physics → render
```

---

## ||| Board Layout

```
┌────────────────────┐  TETRIS
│                    │  ──────────
│                    │  Score
│     [active]       │         0
│                    │  Lines
│     [ghost]        │         0
│                    │  Level
│  [locked blocks]   │         1
│                    │  ──────────
│                    │    NEXT
└────────────────────┘  [preview]
```

- **Board:** 10 columns × 20 rows
- **Each block:** rendered as `██` (2 characters wide) for a more square appearance
- **Frame rate:** ~30 fps (`0.033s` sleep per loop)

---

## ||| Customization

You can tweak constants at the top of the file:

| Constant | Default | Description |
|---|---|---|
| `BOARD_W` | `10` | Board width in columns |
| `BOARD_H` | `20` | Board height in rows |
| `BLOCK` | `'██'` | Character used for filled cells |
| `LEVEL_SPEEDS` | `[0.8 … 0.1]` | Drop speed (s) per level |
| `POINTS` | `[0,100,300,500,800]` | Score per lines cleared |

---

## ||| Troubleshooting

**Board is cut off or misaligned**
→ Please, try to resize your terminal to at least 60 columns × 26 rows and restart the game.

**Colors not showing**
→ Please, make sure your terminal supports 256 colors. Set `TERM=xterm-256color` in your shell if needed.

**`ModuleNotFoundError: No module named '_curses'`**
→ Oh! On Windows, install `windows-curses`:
```
pip install windows-curses
```

**Key inputs feel laggy**
→ This is expected in `nodelay` mode the input polling and physics run on the same loop.
</br> The game targets 30 fps which is smooth under normal conditions.

---

## License

Yeah buddies it's free to use, modify, and distribute. No attribution required.
But please, let me know if your game is as fun as this. I would love to learn with you and your code. 

