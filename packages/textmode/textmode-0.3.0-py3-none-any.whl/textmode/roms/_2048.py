from __future__ import annotations

import random
from typing import List, Tuple

from textmode import TextmodeConsole, register_rom


Board = List[List[int]]


# Simple color palette for tiles
def tile_colors(val: int) -> Tuple[str, str]:
    """Return (fg, bg) for a given tile value."""
    # foreground, background
    if val == 0:
        return ('#999999', '#111111')  # dim fg on black bg for empty
    mapping = {
        2:   ('#111111', '#EEE4DA'),
        4:   ('#111111', '#EDE0C8'),
        8:   ('#FFFFFF', '#F2B179'),
        16:  ('#FFFFFF', '#F59563'),
        32:  ('#FFFFFF', '#F67C5F'),
        64:  ('#FFFFFF', '#F65E3B'),
        128: ('#FFFFFF', '#EDCF72'),
        256: ('#FFFFFF', '#EDCC61'),
        512: ('#FFFFFF', '#EDC850'),
        1024:('#FFFFFF', '#EDC53F'),
        2048:('#FFFFFF', '#EDC22E'),
    }
    return mapping.get(val, ('#FFFFFF', '#3C3A32'))


def tile_char(val: int) -> str:
    """Pick a single-character glyph to represent the tile, fitting 1x1 inner cell.

    - Single-digit values (2,4,8) render as the actual digit.
    - For larger values, use distinct glyphs to avoid everything becoming a star.
    """
    if val == 0:
        return ' '
    if val < 10:
        return str(val)
    # Richer symbol map for multi-digit values
    glyphs = {
        16: '∙',
        32: '∘',
        64: '•',
        128: '▓',
        256: '█',
        512: '☼',
        1024: '⸙',
        2048: '★',
        4096: '☼',
        8192: '✕',
    }
    # Fallback tiers if values grow beyond mapping
    if val in glyphs:
        return glyphs[val]
    # Choose a tiered fallback based on magnitude
    if val < 100:
        return '●'
    if val < 1000:
        return '◆'
    if val < 10000:
        return '★'
    return '✦'


def empty_cells(board: Board) -> List[Tuple[int, int]]:
    cells: List[Tuple[int, int]] = []
    for r in range(4):
        for c in range(4):
            if board[r][c] == 0:
                cells.append((r, c))
    return cells


def add_random_tile(board: Board) -> bool:
    cells = empty_cells(board)
    if not cells:
        return False
    r, c = random.choice(cells)
    board[r][c] = 4 if random.random() < 0.1 else 2
    return True


def _compress(row: List[int]) -> List[int]:
    xs = [v for v in row if v != 0]
    xs += [0] * (4 - len(xs))
    return xs


def _merge(row: List[int]) -> Tuple[List[int], int]:
    score_gain = 0
    r = list(row)
    for i in range(3):
        if r[i] != 0 and r[i] == r[i + 1]:
            r[i] *= 2
            score_gain += r[i]
            r[i + 1] = 0
    return r, score_gain


def move_left(board: Board) -> Tuple[Board, bool, int]:
    moved = False
    gained = 0
    out: Board = []
    for row in board:
        comp = _compress(row)
        merged, g = _merge(comp)
        comp2 = _compress(merged)
        out.append(comp2)
        if comp2 != row:
            moved = True
        gained += g
    return out, moved, gained


def move_right(board: Board) -> Tuple[Board, bool, int]:
    out: Board = []
    moved = False
    gained = 0
    for row in board:
        rev = list(reversed(row))
        comp = _compress(rev)
        merged, g = _merge(comp)
        comp2 = _compress(merged)
        new_row = list(reversed(comp2))
        out.append(new_row)
        if new_row != row:
            moved = True
        gained += g
    return out, moved, gained


def transpose(board: Board) -> Board:
    return [list(row) for row in zip(*board)]  # type: ignore[misc]


def move_up(board: Board) -> Tuple[Board, bool, int]:
    t = transpose(board)
    moved_board, moved, gained = move_left(t)
    return transpose(moved_board), moved, gained


def move_down(board: Board) -> Tuple[Board, bool, int]:
    t = transpose(board)
    moved_board, moved, gained = move_right(t)
    return transpose(moved_board), moved, gained


def any_moves_available(board: Board) -> bool:
    if empty_cells(board):
        return True
    # Check merges horizontally
    for r in range(4):
        for c in range(3):
            if board[r][c] == board[r][c + 1]:
                return True
    # Check merges vertically
    for c in range(4):
        for r in range(3):
            if board[r][c] == board[r + 1][c]:
                return True
    return False


def draw_board(console: TextmodeConsole, board: Board, top_y: int = 1, left_x: int = 2) -> None:
    # Render each tile as a 3x3 framed cell (outer dimensions), with 1-char spacing between tiles
    tile_w = 3  # outer width (includes borders)
    tile_h = 3  # outer height (includes borders) -> inner height = 1
    gap = 1
    # Draw background panel around the board
    total_w = 4 * tile_w + 3 * gap
    total_h = 4 * tile_h + 3 * gap
    # Optional: faint frame around the whole board
    prev_fg, prev_bg, prev_style = console.current_fg, console.current_bg, console.current_style
    try:
        console.setTextColor('#CCCCCC')
        console.setBackgroundColor('#111111')
        console.frame(x=left_x - 2, y=top_y - 2, width=total_w + 5, height=total_h + 3)
    finally:
        console.current_fg, console.current_bg, console.current_style = prev_fg, prev_bg, prev_style

    for r in range(4):
        for c in range(4):
            v = board[r][c]
            fg, bg = tile_colors(v)
            # position for the top-left corner of the tile's frame
            x = left_x + c * (tile_w + gap)
            y = top_y + r * (tile_h + gap)
            # Draw tile frame with the tile background color
            prev_fg, prev_bg, prev_style = console.current_fg, console.current_bg, console.current_style
            try:
                console.setBackgroundColor(bg)
                console.setTextColor('#E0E0E0')  # border color
                console.frame(x=x, y=y, width=tile_w, height=1)  # inner height 1 -> outer 3 rows
                # Write centered glyph into the inner cell (x+1, y+1)
                ch = tile_char(v)
                console.setTextColor(fg)
                console.writeAt(ch, x + 1, y + 1)
            finally:
                console.current_fg, console.current_bg, console.current_style = prev_fg, prev_bg, prev_style


@register_rom("2048")
class Game2048:
    async def run(self, console: TextmodeConsole) -> None:
        console.setScreen(19, 19)
        console.setBackgroundColor('black')
        console.setTextColor('white')

        # Initialize
        board: Board = [[0 for _ in range(4)] for _ in range(4)]
        add_random_tile(board)
        add_random_tile(board)
        score = 0

        # Introduce controls and legend via dialogue (not drawn persistently)
        legend_vals = [16, 32, 64, 128, 256, 512, 1024, 2048]
        legend = ", ".join(f"{v}={tile_char(v)}" for v in legend_vals)
        await console.dialogue(
            "Use arrow keys to move. Press Enter to restart after game over. "
            f"Tile legend: {legend}."
        )

        def render() -> None:
            console.clear()
            draw_board(console, board, top_y=2, left_x=2)

        render()

        # Game loop
        while True:
            key = await console.waitKey(lambda k: k in {'up', 'down', 'left', 'right', 'enter'})

            if key == 'enter':
                # Restart game
                board = [[0 for _ in range(4)] for _ in range(4)]
                add_random_tile(board)
                add_random_tile(board)
                # Reset score via negative add of current score, then set to 0
                console.addScore(-console.getScore())
                score = 0
                render()
                continue

            moved = False
            gained = 0
            if key == 'left':
                board, moved, gained = move_left(board)
            elif key == 'right':
                board, moved, gained = move_right(board)
            elif key == 'up':
                board, moved, gained = move_up(board)
            elif key == 'down':
                board, moved, gained = move_down(board)

            if moved:
                add_random_tile(board)
                if gained:
                    score += gained
                    console.addScore(gained)
                render()

            if not any_moves_available(board):
                # Draw final frame and mark game over
                render()
                console.gameOver()
                # Wait for Enter to restart
                await console.waitKey(lambda k: k == 'enter')
                # Restart
                board = [[0 for _ in range(4)] for _ in range(4)]
                add_random_tile(board)
                add_random_tile(board)
                console.addScore(-console.getScore())
                score = 0
                render()
