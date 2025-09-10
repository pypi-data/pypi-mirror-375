import asyncio
from dataclasses import dataclass
from typing import List, Optional, Callable, Dict, Any

# ComputerCraft-like color bit mapping
a_COLOR_TO_HEX = {
    1:   '#F0F0F0', # white
    2:   '#F2B233', # orange
    4:   '#E57FD8', # magenta
    8:   '#99B2F2', # lightBlue
    16:  '#DEDE6C', # yellow
    32:  '#7FCC19', # lime
    64:  '#F2B2CC', # pink
    128: '#4C4C4C', # gray
    256: '#999999', # lightGray
    512: '#4C99B2', # cyan
    1024:'#B266E5', # purple
    2048:'#3366CC', # blue
    4096:'#7F664C', # brown
    8192:'#57A64E', # green
    16384:'#CC4C4C', # red
    32768:'#111111', # black,
}

NAME_TO_BIT = {
    'white': 1,
    'orange': 2,
    'magenta': 4,
    'lightBlue': 8,
    'yellow': 16,
    'lime': 32,
    'pink': 64,
    'gray': 128,
    'lightGray': 256,
    'cyan': 512,
    'purple': 1024,
    'blue': 2048,
    'brown': 4096,
    'green': 8192,
    'red': 16384,
    'black': 32768,
}

ALLOWED_KEYS = { 'up', 'down', 'left', 'right', 'enter' }


def resolve_color(c: Optional[Any]) -> Optional[str]:
    if c is None:
        return None
    if isinstance(c, int):
        # choose lowest set bit
        for bit in sorted(a_COLOR_TO_HEX.keys()):
            if (c & bit) == bit:
                return a_COLOR_TO_HEX[bit]
        return None
    if isinstance(c, str):
        if c.startswith('#'):
            return c
        bit = NAME_TO_BIT.get(c)
        if bit:
            return a_COLOR_TO_HEX[bit]
    return None


@dataclass
class Cell:
    ch: str = ' '
    fg: str = '#F0F0F0'
    bg: str = '#111111'
    style: str = 'normal'  # 'normal' | 'italic' | 'blink'


class TextmodeConsole:
    def __init__(self, cols: int = 16, rows: int = 16, render_dialogues: bool = True, render_choices: bool = True):
        self.cols = max(1, int(cols))
        self.rows = max(1, int(rows))
        self.grid: List[Cell] = [Cell() for _ in range(self.cols * self.rows)]
        # Current drawing attributes
        self.current_fg = resolve_color('white')
        self.current_bg = resolve_color('black')
        self.current_style = 'normal'
        # Input queue for key events
        self._key_q: asyncio.Queue[str] = asyncio.Queue()
        self._over: bool = False
        # Score tracking
        self._score: int = 0
        # Dialogue behavior & queue
        self._skip_dialogue: bool = (not render_dialogues)
        self._dialogues: List[str] = []
        # Choices behavior & state
        self._render_choices: bool = bool(render_choices)
        self._choices_opts: Optional[List[str]] = None
        self._choice_selection_q: asyncio.Queue[str] = asyncio.Queue()

    # --------------- Screen & Drawing -----------------
    def setScreen(self, cols: int, rows: int) -> None:
        self.cols = max(1, int(cols))
        self.rows = max(1, int(rows))
        self.grid = [Cell() for _ in range(self.cols * self.rows)]
        # After resizing, clear to current background color
        self.clear()

    def _xy2id(self, x: int, y: int) -> int:
        if x < 0 or y < 0 or x >= self.cols or y >= self.rows:
            return -1
        return y * self.cols + x

    def clear(self) -> None:
        for i in range(self.cols * self.rows):
            c = self.grid[i]
            c.ch = ' '
            # apply current drawing attributes to each cleared cell
            c.fg = self.current_fg
            c.bg = self.current_bg
            c.style = self.current_style

    def clearLine(self, y: int) -> None:
        cy = int(y)
        if cy < 0 or cy >= self.rows:
            return
        for x in range(self.cols):
            idx = self._xy2id(x, cy)
            if idx != -1:
                c = self.grid[idx]
                c.ch = ' '
                c.fg = self.current_fg
                c.bg = self.current_bg
                c.style = self.current_style

    def snapshot(self) -> Dict[str, Any]:
        # Snapshot full grid state and current attrs
        chars = ''.join(c.ch if c.ch else ' ' for c in self.grid)
        fgs = [c.fg for c in self.grid]
        bgs = [c.bg for c in self.grid]
        styles = [c.style for c in self.grid]
        return {
            'cols': self.cols,
            'rows': self.rows,
            'chars': chars,
            'fgs': fgs,
            'bgs': bgs,
            'styles': styles,
            'over': self._over,
            'score': self._score,
        }

    def restore(self, snap: Dict[str, Any]) -> None:
        cols = int(snap.get('cols', self.cols))
        rows = int(snap.get('rows', self.rows))
        chars: str = snap.get('chars', '')
        fgs: List[str] = snap.get('fgs', [])
        bgs: List[str] = snap.get('bgs', [])
        styles: List[str] = snap.get('styles', [])
        if cols != self.cols or rows != self.rows:
            self.setScreen(cols, rows)
        total = self.cols * self.rows
        for i in range(total):
            c = self.grid[i]
            c.ch = chars[i] if i < len(chars) else ' '
            c.fg = fgs[i] if i < len(fgs) else c.fg
            c.bg = bgs[i] if i < len(bgs) else c.bg
            c.style = styles[i] if i < len(styles) else c.style

    def writeAt(self, s: str, x: int = 0, y: int = 0) -> None:
        start_x = int(x)
        cx = start_x
        cy = int(y)
        for ch in list(str(s or '')):
            if ch == '\n':
                cy += 1
                cx = start_x
                if cy >= self.rows:
                    break
                continue
            idx = self._xy2id(cx, cy)
            if idx != -1:
                cell = self.grid[idx]
                cell.ch = ch
                cell.fg = self.current_fg
                cell.bg = self.current_bg
                cell.style = self.current_style
            cx += 1

    def write(self, s: str) -> None:
        self.writeAt(s, 0, 0)

    # --------------- Colors & Styles -----------------
    def setTextColor(self, color: Any) -> None:
        hexv = resolve_color(color)
        if hexv:
            self.current_fg = hexv

    def setBackgroundColor(self, color: Any) -> None:
        hexv = resolve_color(color)
        if hexv:
            self.current_bg = hexv

    def setTextStyle(self, style: str) -> None:
        s = str(style).lower().strip()
        if s == 'italics':
            self.current_style = 'italic'
        elif s == 'blink':
            self.current_style = 'blink'
        else:
            self.current_style = 'normal'

    # --------------- UI Utilities -----------------
    def frame(self, x: int = 0, y: Optional[int] = None, width: Optional[int] = None,
              topLeft: str = '', bottomRight: str = '', height: Optional[int] = None) -> None:
        if y is None:
            y = self.rows - 4
        if width is None:
            width = min(self.cols, 10)
        width = max(3, min(int(width), self.cols - x))
        inner = width - 2
        # If height is None, draw classic 4-line frame (2 inner rows)
        if height is None:
            top = '┌' + '─' * inner + '┐'
            mid = '│' + ' ' * inner + '│'
            bot = '└' + '─' * inner + '┘'
            self.writeAt('\n'.join([top, mid, mid, bot]), x, y)
            if topLeft:
                self.writeAt(str(topLeft)[:inner], x + 1, y)
            if bottomRight:
                s = str(bottomRight)
                start = x + width - 2 - (len(s) - 1)
                self.writeAt(s, max(x + 1, start), y + 3)
            return
        # Variable-height frame: draw top, `height` inner rows, bottom
        inner_h = max(1, min(int(height), self.rows - y - 2))
        top = '┌' + '─' * inner + '┐'
        mid = '│' + ' ' * inner + '│'
        bot = '└' + '─' * inner + '┘'
        self.writeAt(top, x, y)
        for r in range(inner_h):
            self.writeAt(mid, x, y + 1 + r)
        self.writeAt(bot, x, y + 1 + inner_h)
        if topLeft:
            self.writeAt(str(topLeft)[:inner], x + 1, y)
        if bottomRight:
            s = str(bottomRight)
            start = x + width - 2 - (len(s) - 1)
            self.writeAt(s, max(x + 1, start), y + 1 + inner_h)

    def _wrap_text(self, text: str, width: int = 8) -> List[str]:
        words = str(text or '').split()
        lines: List[str] = []
        line = ''
        for w in words:
            if len(w) > width:
                if line:
                    lines.append(line)
                    line = ''
                for i in range(0, len(w), width):
                    lines.append(w[i:i+width])
                continue
            if not line:
                line = w
            elif len(line) + 1 + len(w) <= width:
                line += ' ' + w
            else:
                lines.append(line)
                line = w
        if line:
            lines.append(line)
        return lines

    # --------------- Dialogue helpers -----------------
    def pop_dialogues(self) -> List[str]:
        """Return and clear any queued dialogue lines since last call."""
        out = list(self._dialogues)
        self._dialogues.clear()
        return out

    def _queue_dialogue(self, text: str) -> None:
        t = str(text or '')
        if t:
            self._dialogues.append(t)

    def peek_choices(self) -> Optional[List[str]]:
        """Return a copy of the active choices list if a choices menu is active; otherwise None."""
        return list(self._choices_opts) if self._choices_opts is not None else None

    def enqueue_choice(self, label: str) -> bool:
        """In headless mode, enqueue a choice selection by exact label.

        Returns True if accepted (matches an active option), False otherwise.
        Has no effect when no choices are active.
        """
        if self._choices_opts is None:
            return False
        lbl = str(label)
        if lbl in self._choices_opts:
            try:
                self._choice_selection_q.put_nowait(lbl)
                return True
            except asyncio.QueueFull:
                return False
        return False

    async def dialogue(self, text: str, x: int = 0, y: Optional[int] = None,
                       width: Optional[int] = None, height: int = 2) -> None:
        # Always queue the raw dialogue text for external consumers
        self._queue_dialogue(text)
        if self._skip_dialogue:
            # Skip rendering and waiting; act as a no-op on the screen
            return
        if y is None:
            y = self.rows - 4
        if width is None:
            width = max(1, self.cols - x - 2)
        snap = self.snapshot()
        try:
            lines = self._wrap_text(text, width)
            idx = 0
            while idx < len(lines):
                page = lines[idx: idx + height]
                # draw textbox
                more = (idx + height) < len(lines)
                self.frame(x, y, width + 2, bottomRight=('▼' if more else ''), height=height)
                for i, ln in enumerate(page):
                    ln2 = ln.ljust(width)[:width]
                    self.writeAt(ln2, x + 1, y + 1 + i)
                # Make the bottom-right indicator blink and bright
                if more:
                    prev_fg, prev_style = self.current_fg, self.current_style
                    try:
                        self.setTextColor('white')
                        self.setTextStyle('blink')
                        self.writeAt('▼', x + width, y + height + 1)
                    finally:
                        self.current_fg, self.current_style = prev_fg, prev_style
                # wait for enter
                await self.waitKey(lambda k: k == 'enter')
                idx += height
        finally:
            self.restore(snap)

    async def waitKey(self, predicate: Callable[[str], bool]) -> str:
        while True:
            k = await self._key_q.get()
            if predicate(k):
                return k

    async def choices(self, options: List[str], y: int = 0, width: int = None,
                      x: Optional[int] = None, keep: bool = False) -> Optional[str]:
        opts = [str(o) for o in (options or [])]
        if not opts:
            return None
        if not width:
            width = min(max(6, max(len(o) for o in opts)), self.cols - 2)
        snap = self.snapshot()
        i = 0
        innerWidth = max(1, min(int(width), self.cols - 2))
        frameX = max(0, self.cols - (innerWidth + 2)) if x is None else max(0, min(int(x), self.cols - (innerWidth + 2)))
        frameY = max(0, min(int(y), self.rows - (len(opts) + 2)))
        self._choices_opts = list(opts)
        try:
            def render() -> None:
                if not self._render_choices:
                    return
                # clear area
                for r in range(len(opts) + 2):
                    self.writeAt(' ' * (innerWidth + 2), frameX, frameY + r)
                # draw frame
                self.frame(frameX, frameY, innerWidth + 2, height=len(opts))
                # draw options
                for idx, raw in enumerate(opts):
                    label = raw.ljust(max(0, innerWidth - 1))[:max(0, innerWidth - 1)]
                    rowY = frameY + 1 + idx
                    if idx == i:
                        # blinking selector arrow
                        prev_fg, prev_style = self.current_fg, self.current_style
                        try:
                            self.setTextColor('white')
                            self.setTextStyle('blink')
                            self.writeAt('►', frameX + 1, rowY)
                        finally:
                            self.current_fg, self.current_style = prev_fg, prev_style
                    else:
                        if self._render_choices:
                            self.writeAt(' ', frameX + 1, rowY)
                    # render the label with normal style
                    if self._render_choices:
                        self.setTextStyle('normal')
                        self.writeAt(label.ljust(innerWidth - 1)[:innerWidth - 1], frameX + 2, rowY)

            if not self._render_choices:
                # Headless mode: wait for an explicit selection via enqueue_choice()
                selected = await self._choice_selection_q.get()
                # Ensure selected is one of opts; if not, coerce to first
                if selected not in opts:
                    selected = opts[0]
                return selected

            # Rendered mode (classic): navigate with keys and Enter
            render()
            while True:
                k = await self.waitKey(lambda _k: _k in ALLOWED_KEYS)
                if k == 'enter':
                    break
                if k == 'down':
                    i = (i + 1) % len(opts)
                    render()
                    continue
                if k == 'up':
                    i = (i - 1 + len(opts)) % len(opts)
                    render()
                    continue
            selected = opts[i]
            if not keep and self._render_choices:
                self.restore(snap)
            return selected
        finally:
            self._choices_opts = None

    # --------------- Game state helpers -----------------
    def enqueue_key(self, key: str) -> None:
        k = str(key).lower().strip()
        if k in ALLOWED_KEYS:
            # put_nowait is fine; consumer always awaits
            try:
                self._key_q.put_nowait(k)
            except asyncio.QueueFull:
                pass

    def addScore(self, points: int) -> None:
        """Increase (or decrease) the player's score by `points`."""
        try:
            p = int(points)
        except Exception:
            p = 0
        self._score += p

    def getScore(self) -> int:
        """Return the current player's score."""
        return int(self._score)

    def gameOver(self) -> None:
        self._over = True
        prev_fg = self.current_fg
        prev_bg = self.current_bg
        prev_style = self.current_style
        try:
            self.setTextColor('red')
            self.setBackgroundColor('black')
            self.setTextStyle('normal')
            self.writeAt(f'Score: {self._score}', 0, self.rows - 2)
            self.writeAt('You are DEAD', 0, self.rows - 1)
        finally:
            # keep colors as-is afterwards (mirror browser semantics that attributes persist),
            # but we already set them above to red/black; restore previous if desired
            self.current_fg = prev_fg
            self.current_bg = prev_bg
            self.current_style = prev_style

    # convenience API surface compatibility
    # Expose names matching the browser helpers
    def setTextColour(self, color: Any) -> None:
        self.setTextColor(color)

    def setBackgroundColour(self, color: Any) -> None:
        self.setBackgroundColor(color)

    # Serialization for client
    def render_payload(self) -> Dict[str, Any]:
        snap = self.snapshot()
        return snap
