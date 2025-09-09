from typing import List, Tuple, Optional, Dict
from textmode import TextmodeConsole, register_rom

# Simple key-driven Tetris implementation for the Textmode Fantasy Console.
# Notes:
# - No timers are used; gravity advances only when you press a key (Down or Enter for hard drop).
# - Controls: Left/Right to move, Up to rotate, Down to soft drop, Enter to hard drop.
# - Board size: 10x20 playfield rendered within a frame; a small info panel is shown on the right.

Coord = Tuple[int, int]

# Tetromino shapes (I, O, T, S, Z, J, L)
# Each piece is defined as a list of rotation states; each state is a list of (x,y) coords.
PIECES: Dict[str, List[List[Coord]]] = {
    'I': [
        [(0, 1), (1, 1), (2, 1), (3, 1)],  # ---- horizontal
        [(2, 0), (2, 1), (2, 2), (2, 3)],  # | vertical
    ],
    'O': [
        [(1, 0), (2, 0), (1, 1), (2, 1)],  # square (rotation invariant)
    ],
    'T': [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    'S': [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
    ],
    'Z': [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
    ],
    'J': [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    'L': [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

PIECE_ORDER = ['T', 'J', 'Z', 'O', 'S', 'L', 'I']  # deterministic cycle
PIECE_COLOR = {
    'I': 'cyan',
    'O': 'yellow',
    'T': 'purple',
    'S': 'green',
    'Z': 'red',
    'J': 'blue',
    'L': 'orange',
}

BLOCK_CHAR = '█'
EMPTY_CHAR = ' '

PLAY_W = 10
PLAY_H = 20

class Piece:
    def __init__(self, kind: str):
        self.kind = kind
        self.rot = 0
        self.x = 3  # spawn X relative to playfield
        self.y = 0  # spawn Y

    @property
    def shapes(self) -> List[List[Coord]]:
        return PIECES[self.kind]

    def cells(self, ox: int = 0, oy: int = 0, rot: Optional[int] = None) -> List[Coord]:
        r = self.rot if rot is None else rot % len(self.shapes)
        return [(self.x + ox + dx, self.y + oy + dy) for (dx, dy) in self.shapes[r]]

@register_rom("tetris")
class TetrisGame:
    async def run(self, console: TextmodeConsole) -> None:
        # Screen layout: frame at (1,1) with inner size 10x20; info panel to the right.
        console.setScreen(24, 24)
        console.setBackgroundColor('black')
        console.setTextColor('white')
        console.clear()
 
        board: List[List[Optional[str]]] = [[None for _ in range(PLAY_W)] for _ in range(PLAY_H)]
        order_idx = 0

        def new_piece() -> Piece:
            nonlocal order_idx
            kind = PIECE_ORDER[order_idx % len(PIECE_ORDER)]
            order_idx += 1
            p = Piece(kind)
            # Center more nicely for I/O
            if kind == 'I':
                p.x = 3
            elif kind == 'O':
                p.x = 4
            else:
                p.x = 3
            p.y = 0
            return p

        current = new_piece()
        next_piece_kind = PIECE_ORDER[order_idx % len(PIECE_ORDER)]

        def fits(cells: List[Coord]) -> bool:
            for (x, y) in cells:
                if x < 0 or x >= PLAY_W or y < 0 or y >= PLAY_H:
                    return False
                if board[y][x] is not None:
                    return False
            return True

        def lock_piece(p: Piece) -> None:
            for (x, y) in p.cells():
                if 0 <= y < PLAY_H and 0 <= x < PLAY_W:
                    board[y][x] = p.kind

        def clear_lines() -> int:
            cleared = 0
            y = PLAY_H - 1
            while y >= 0:
                if all(board[y][x] is not None for x in range(PLAY_W)):
                    # remove this line and add empty at top
                    del board[y]
                    board.insert(0, [None for _ in range(PLAY_W)])
                    cleared += 1
                else:
                    y -= 1
            return cleared

        def award_lines(cleared: int) -> None:
            # Simple scoring for cleared lines (no level multiplier)
            # 1:100, 2:300, 3:500, 4:800
            if cleared <= 0:
                return
            table = {1: 100, 2: 300, 3: 500, 4: 800}
            console.addScore(table.get(cleared, cleared * 100))

        def spawn_next() -> bool:
            nonlocal current, next_piece_kind, order_idx
            current = Piece(next_piece_kind)
            if current.kind == 'I':
                current.x = 3
            elif current.kind == 'O':
                current.x = 4
            else:
                current.x = 3
            current.y = 0
            order_idx += 1
            next_piece_kind = PIECE_ORDER[order_idx % len(PIECE_ORDER)]
            return fits(current.cells())

        def render() -> None:
            console.setTextStyle('normal')
            # Clear whole screen area to maintain colors
            for r in range(console.rows):
                console.clearLine(r)

            # Frame around playfield
            console.frame(1, 1, width=PLAY_W + 2, height=PLAY_H)

            # Draw settled board
            for y in range(PLAY_H):
                for x in range(PLAY_W):
                    v = board[y][x]
                    ch = BLOCK_CHAR if v is not None else EMPTY_CHAR
                    if v is not None:
                        console.setTextColor(PIECE_COLOR.get(v, 'white'))
                        console.writeAt(ch, 2 + x, 2 + y)
                    else:
                        console.setTextColor('lightGray')
                        console.writeAt(' ', 2 + x, 2 + y)

            # Draw current piece
            console.setTextColor(PIECE_COLOR.get(current.kind, 'white'))
            for (cx, cy) in current.cells():
                if 0 <= cy < PLAY_H and 0 <= cx < PLAY_W:
                    console.writeAt(BLOCK_CHAR, 2 + cx, 2 + cy)

            # Info panel
            console.setTextColor('white')
            console.frame(PLAY_W + 4, 1, width=8, height=6)
            console.writeAt('NEXT', PLAY_W + 5, 2)
            # Draw next piece in a 4x4 area
            preview_cells = PIECES[next_piece_kind][0]
            px_offset = PLAY_W + 5
            py_offset = 4
            console.setTextColor(PIECE_COLOR.get(next_piece_kind, 'white'))
            for (dx, dy) in preview_cells:
                console.writeAt(BLOCK_CHAR, px_offset + dx, py_offset + dy)

            # Score display
            console.setTextColor('white')
            console.writeAt('SCORE', PLAY_W + 5, 15)
            console.writeAt(str(console.getScore()).rjust(5), PLAY_W + 5, 16)

        def try_move(dx: int, dy: int) -> bool:
            cells = current.cells(dx, dy)
            if fits(cells):
                current.x += dx
                current.y += dy
                return True
            return False

        def try_rotate() -> None:
            new_rot = (current.rot + 1) % len(current.shapes)
            cells = current.cells(rot=new_rot)
            # Basic wall kick: try shift left/right if rotation collides
            kick_options = [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0)]
            for kx, ky in kick_options:
                temp = [(x + kx, y + ky) for (x, y) in cells]
                if fits(temp):
                    current.rot = new_rot
                    current.x += kx
                    current.y += ky
                    return
            # If none fit, ignore rotation

        def step_down(lock_if_blocked: bool = True) -> bool:
            if try_move(0, 1):
                return True
            if lock_if_blocked:
                lock_piece(current)
                cleared = clear_lines()
                award_lines(cleared)
                # spawn next
                if not spawn_next():
                    # game over
                    console.gameOver()
                    return False
            return False

        # Show controls upfront in a dialogue
        await console.dialogue('TETRIS CONTROLS: ←/→ move · ↑ rotate · ↓ soft drop · Enter hard drop')

        # Initial render
        render()

        # Game loop (key-driven)
        while True:
            k = await console.waitKey(lambda kk: kk in {'left', 'right', 'up', 'down', 'enter'})
            if k == 'left':
                try_move(-1, 0)
            elif k == 'right':
                try_move(1, 0)
            elif k == 'up':
                try_rotate()
            elif k == 'down':
                # soft drop one line; if blocked, lock
                cont = step_down(lock_if_blocked=True)
                if not cont and any(board[0][x] is not None for x in range(PLAY_W)):
                    break
            elif k == 'enter':
                # hard drop
                while try_move(0, 1):
                    pass
                # lock after drop
                lock_piece(current)
                cleared = clear_lines()
                award_lines(cleared)
                if not spawn_next():
                    console.gameOver()
                    break
            render()
