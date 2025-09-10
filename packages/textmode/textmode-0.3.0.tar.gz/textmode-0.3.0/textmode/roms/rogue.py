import random
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict

from textmode import TextmodeConsole, register_rom


# Glyphs and colors
GLYPH_WALL = '█'
GLYPH_FLOOR = '∙'
GLYPH_PLAYER = '@'
GLYPH_STAIRS = '⟎'
GLYPH_CHEST = '⧇'
GLYPH_KEY = '⚷'
GLYPH_SWORD = '†'
GLYPH_TAROT = '♢'

# Themes define palette, tiles, monsters
THEMES = [
    {
        'name': 'stone',
        'fg': 'lightGray',
        'bg': 'black',
        'wall': GLYPH_WALL,
        'floor': GLYPH_FLOOR,
        'primary': {'glyph': '☠', 'name': 'skull'},
        'secondary': {'glyph': '⋒', 'name': 'knight'},
        'msg': 'you enter the stone halls'
    },
    {
        'name': 'swamp',
        'fg': 'green',
        'bg': 'black',
        'wall': '▓',
        'floor': '·',
        'primary': {'glyph': '⌤', 'name': 'frog'},
        'secondary': {'glyph': '⚱', 'name': 'ooze'},
        'msg': 'a damp swamp stench fills the air'
    },
    {
        'name': 'hell',
        'fg': 'red',
        'bg': 'black',
        'wall': '■',
        'floor': '·',
        'primary': {'glyph': '⚇', 'name': 'imp'},
        'secondary': {'glyph': '⟁', 'name': 'flame'},
        'msg': 'sulfur and ash choke the dim passages'
    },
]

# Pools
SWORDS = [
    {'name': 'shortsword', 'glyph': GLYPH_SWORD, 'desc': 'quick poke', 'atk': (1, 2), 'knock': 1, 'speed': 'fast', 'radius': 'close', 'dur': (3, 5)},
    {'name': 'longsword', 'glyph': GLYPH_SWORD, 'desc': 'steady swing', 'atk': (2, 3), 'knock': 1, 'speed': 'slow', 'radius': 'far', 'dur': (4, 6)},
    {'name': 'scythe', 'glyph': '☥', 'desc': 'grim sweep', 'atk': (2, 4), 'knock': 2, 'speed': 'slow', 'radius': 'far', 'dur': (3, 5)},
]

TAROTS = [
    {'name': 'the star', 'glyph': GLYPH_TAROT, 'color': 'cyan', 'stat': 'attack', 'desc': '+1 attack'},
    {'name': 'the tower', 'glyph': GLYPH_TAROT, 'color': 'purple', 'stat': 'knockback', 'desc': '+1 knockback'},
    {'name': 'the chariot', 'glyph': GLYPH_TAROT, 'color': 'yellow', 'stat': 'speed', 'desc': 'faster strikes'},
    {'name': 'strength', 'glyph': GLYPH_TAROT, 'color': 'orange', 'stat': 'radius', 'desc': 'wider arc'},
]


@dataclass
class Item:
    kind: str  # 'sword' | 'tarot' | 'key'
    name: str
    glyph: str
    color: Optional[str] = None
    data: Dict = field(default_factory=dict)


@dataclass
class Monster:
    x: int
    y: int
    glyph: str
    name: str
    hp: int
    atk: int
    tough: bool = False


@register_rom("rogue")
class Rogue:
    async def run(self, console: TextmodeConsole) -> None:
        cols, rows = 32, 18
        hud_h = 2
        map_h = rows - hud_h
        console.setScreen(cols, rows)

        floor = 1
        rng = random.Random()
        await console.dialogue('welcome to ROGUE. arrows to move. walk into things to use. enter to continue')
        player = {'x': 0, 'y': 0, 'hp': 10, 'base_atk': 1, 'seen': set(), 'fov': 7}
        inv_sword: Optional[Item] = None
        inv_tarot: Optional[Item] = None

        defeated = 0
        stairs: Optional[Tuple[int, int]] = None

        while True:
            theme = THEMES[(floor - 1) % len(THEMES)]
            # Generate map and place entities
            grid, rooms = self._gen_map(cols, map_h, rng, theme)
            player['x'], player['y'] = rooms[0][0] + 1, rooms[0][1] + 1
            monsters: List[Monster] = []
            items: Dict[Tuple[int, int], Item] = {}
            stairs = None
            defeated = 0

            # Place monsters
            n_mobs = max(3, floor + 2)
            for _ in range(n_mobs):
                rx, ry, rw, rh = rng.choice(rooms)
                x = rng.randrange(rx + 1, rx + rw - 1)
                y = rng.randrange(ry + 1, ry + rh - 1)
                if (x, y) == (player['x'], player['y']):
                    continue
                mdef = theme['primary'] if rng.random() < 0.7 else theme['secondary']
                m = Monster(x, y, mdef['glyph'], mdef['name'], hp=2 + floor // 2, atk=1 + floor // 3)
                monsters.append(m)

            # Possible tough enemy + chest + key
            tough_spawned = False
            if rng.random() < 0.002:  # 0.2%
                # choose a monster to upgrade or add a new one
                if monsters:
                    m = rng.choice(monsters)
                else:
                    rx, ry, rw, rh = rng.choice(rooms)
                    m = Monster(rx + rw // 2, ry + rh // 2, theme['primary']['glyph'], theme['primary']['name'], hp=4 + floor, atk=2 + floor // 2)
                    monsters.append(m)
                m.tough = True
                m.hp += 3
                m.atk += 1
                # Chest somewhere in far room
                crx, cry, crw, crh = rng.choice(rooms)
                cx = rng.randrange(crx + 1, crx + crw - 1)
                cy = rng.randrange(cry + 1, cry + crh - 1)
                items[(cx, cy)] = Item('chest', 'locked chest', GLYPH_CHEST)
                # Key follows tough enemy
                key_pos = self._adjacent_free(grid, m.x, m.y, rng)
                if key_pos:
                    items[key_pos] = Item('key', 'yellow key', GLYPH_KEY, color='yellow', data={'follow': (m.x, m.y)})
                tough_spawned = True

            # Place a random weapon and tarot on the floor
            self._drop_random_sword(items, grid, rooms, rng)
            self._drop_random_tarot(items, grid, rooms, rng)

            await console.dialogue(f"{theme['msg']}")

            # main floor loop
            while True:
                # Draw
                self._render(console, grid, theme, player, monsters, items, stairs, floor, inv_sword, inv_tarot, cols, map_h, hud_h)

                # Win/advance condition: defeated >= 3 spawns stairs if not placed
                if stairs is None and defeated >= 3:
                    stairs = self._spawn_stairs(grid, rooms, rng, player, monsters, items)

                # Get input
                k = await console.waitKey(lambda kk: kk in {'up', 'down', 'left', 'right', 'enter'})
                if k == 'enter':
                    await console.dialogue('enter: confirm in menus. otherwise does nothing.')
                    continue

                dx = 0
                dy = 0
                if k == 'up': dy = -1
                elif k == 'down': dy = 1
                elif k == 'left': dx = -1
                elif k == 'right': dx = 1

                nx, ny = player['x'] + dx, player['y'] + dy
                if not self._is_blocking(grid, nx, ny):
                    # Interact first with entity occupying next tile
                    occupied_m = self._monster_at(monsters, nx, ny)
                    if occupied_m:
                        # Combat trigger with initiative: slow=0, fast=1, chariot(+1)
                        init = 0
                        if inv_sword and inv_sword.data.get('speed') == 'fast':
                            init += 1
                        if inv_tarot and inv_tarot.data.get('stat') == 'speed':  # chariot
                            init += 1
                        log = []
                        # Player pre-attacks
                        pre_attacks = 2 if init >= 2 else (1 if init >= 1 else 0)
                        while pre_attacks > 0 and occupied_m in monsters:
                            if self._player_attack(player, occupied_m, inv_sword, inv_tarot, log):
                                defeated += 1
                                monsters.remove(occupied_m)
                                for pos, it in list(items.items()):
                                    if it.kind == 'key' and 'follow' in it.data:
                                        it.data.pop('follow', None)
                                log.append('you slay the foe')
                                break
                            pre_attacks -= 1
                        # Monster retaliates if still alive
                        if occupied_m in monsters:
                            self._monster_attack(occupied_m, player, log)
                            if player['hp'] <= 0:
                                console.gameOver()
                                await console.dialogue('your journey ends here')
                                return
                            # If no pre-attacks happened (init==0), player gets their normal swing now
                            if init == 0 and occupied_m in monsters:
                                if self._player_attack(player, occupied_m, inv_sword, inv_tarot, log):
                                    defeated += 1
                                    monsters.remove(occupied_m)
                                    for pos, it in list(items.items()):
                                        if it.kind == 'key' and 'follow' in it.data:
                                            it.data.pop('follow', None)
                                    log.append('you slay the foe')
                        # present combat log
                        if log:
                            await console.dialogue('\n'.join(log))
                        # consume durability if sword
                        if inv_sword:
                            inv_sword.data['dur'] -= 1
                            if inv_sword.data['dur'] <= 0:
                                await console.dialogue('your weapon breaks')
                                inv_sword = None
                    else:
                        # Move
                        player['x'], player['y'] = nx, ny
                        # Pickups or tile actions
                        it = items.get((nx, ny))
                        if it:
                            if it.kind == 'key':
                                await console.dialogue('you pocket the yellow key')
                                items.pop((nx, ny), None)
                                # mark key in inventory state
                                player['has_key'] = True
                            elif it.kind == 'sword':
                                # loop until a non-inspect decision is made
                                while True:
                                    opts = [f"take {it.name}", "leave", 'inspect']
                                    if inv_sword:
                                        opts.append('swap')
                                    choice = await console.choices(opts)
                                    if choice == 'inspect':
                                        await console.dialogue(self._item_desc(it))
                                        continue
                                    if choice == f"take {it.name}":
                                        inv_sword = it
                                        items.pop((nx, ny), None)
                                        await console.dialogue(f"took {it.name}")
                                    elif choice == 'swap' and inv_sword:
                                        items[(nx, ny)] = inv_sword
                                        inv_sword = it
                                        await console.dialogue('swapped weapons')
                                    break
                            elif it.kind == 'tarot':
                                while True:
                                    opts = [f"take {it.name}", "leave", 'inspect']
                                    if inv_tarot:
                                        opts.append('swap')
                                    choice = await console.choices(opts)
                                    if choice == 'inspect':
                                        await console.dialogue(self._item_desc(it))
                                        continue
                                    if choice == f"take {it.name}":
                                        inv_tarot = it
                                        items.pop((nx, ny), None)
                                        await console.dialogue(f"you hold {it.name}")
                                    elif choice == 'swap' and inv_tarot:
                                        items[(nx, ny)] = inv_tarot
                                        inv_tarot = it
                                        await console.dialogue('swapped tarot')
                                    break
                            elif it.kind == 'chest':
                                # require key
                                if player.get('has_key'):
                                    # Offer swap/drop dialogue
                                    await console.dialogue('the chest unlocks')
                                    player['has_key'] = False
                                    # Roll item inside: sword or tarot
                                    content_is_sword = rng.random() < 0.5
                                    if content_is_sword:
                                        content = self._roll_sword(rng)
                                        content_item = Item('sword', content['name'], content['glyph'], data=content)
                                    else:
                                        content = self._roll_tarot(rng)
                                        content_item = Item('tarot', content['name'], content['glyph'], color=content['color'], data=content)
                                    # Show dialogue
                                    while True:
                                        opts = [f"take {content_item.name}", "leave", 'inspect']
                                        if (content_is_sword and inv_sword) or ((not content_is_sword) and inv_tarot):
                                            opts.append('swap')
                                        pick = await console.choices(opts)
                                        if pick == 'inspect':
                                            await console.dialogue(self._item_desc(content_item))
                                            continue
                                        break
                                    if pick == f"take {content_item.name}":
                                        if content_is_sword:
                                            inv_sword = content_item
                                        else:
                                            inv_tarot = content_item
                                        items.pop((nx, ny), None)
                                    elif pick == 'swap':
                                        if content_is_sword and inv_sword:
                                            items[(nx, ny)] = inv_sword
                                            inv_sword = content_item
                                        elif (not content_is_sword) and inv_tarot:
                                            items[(nx, ny)] = inv_tarot
                                            inv_tarot = content_item
                                else:
                                    await console.dialogue('locked. a yellow key follows a tough foe')
                        elif stairs and (nx, ny) == stairs:
                            floor += 1
                            await console.dialogue('you descend the stairs')
                            break  # rebuild next floor

                    # Monsters step only if player successfully moved or fought something (not into solid)
                    self._step_monsters(grid, monsters, player, items, rng)

                # If attempted to move into solid, ignore simulation (monsters do not step)

                # Death
                if player['hp'] <= 0:
                    console.gameOver()
                    await console.dialogue('you are dead')
                    return

    # ---------------- Rendering & FOV -----------------
    def _render(self, console: TextmodeConsole, grid: List[List[str]], theme: Dict, player, monsters: List[Monster], items: Dict[Tuple[int,int], Item], stairs: Optional[Tuple[int,int]], floor: int, inv_sword: Optional[Item], inv_tarot: Optional[Item], cols: int, map_h: int, hud_h: int) -> None:
        console.setBackgroundColor(theme['bg'])
        console.setTextColor(theme['fg'])
        console.setTextStyle('normal')
        console.clear()

        cols_ = cols
        rows_ = map_h

        # FOV
        seen = self._compute_fov(grid, player['x'], player['y'], player['fov'])
        # persist seen for fog of war
        # We keep it simple and just draw unseen as blank

        for y in range(rows_):
            for x in range(cols_):
                ch = ' '
                if (x, y) in seen:
                    t = grid[y][x]
                    ch = theme['floor'] if t == 'floor' else (theme['wall'])
                elif grid[y][x] == 'wall':
                    ch = ' '
                # write tile
                console.writeAt(ch, x, y)

        # Draw stairs/items/monsters/player only if in seen
        if stairs and (stairs in seen):
            console.writeAt(GLYPH_STAIRS, stairs[0], stairs[1])

        for (ix, iy), it in items.items():
            if (ix, iy) in seen:
                if it.color:
                    console.setTextColor(it.color)
                console.writeAt(it.glyph, ix, iy)
                console.setTextColor(theme['fg'])

        for m in monsters:
            if (m.x, m.y) in seen:
                if m.tough:
                    console.setTextColor('yellow')
                console.writeAt(m.glyph, m.x, m.y)
                if m.tough:
                    console.setTextColor(theme['fg'])

        console.setTextColor('white')
        console.writeAt(GLYPH_PLAYER, player['x'], player['y'])
        console.setTextColor(theme['fg'])

        # HUD (bottom rows)
        y = rows_
        console.clearLine(y)
        console.clearLine(y+1)
        # Minimal icon HUD: floor, hp, weapon, tarot, key
        hud_parts = []
        hud_parts.append(f"Ŀ{floor}")
        hud_parts.append(f"♥{player['hp']}")
        if inv_sword:
            hud_parts.append(f"{inv_sword.glyph}{inv_sword.data.get('dur','-')}")
        if inv_tarot:
            hud_parts.append(f"{inv_tarot.glyph}")
        if player.get('has_key'):
            hud_parts.append(GLYPH_KEY)
        console.writeAt(' '.join(hud_parts)[:cols_], 0, y)

    def _compute_fov(self, grid: List[List[str]], px: int, py: int, radius: int) -> set:
        visible = set()
        visible.add((px, py))
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x = px + dx
                y = py + dy
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    if dx*dx + dy*dy <= radius*radius:
                        if self._los(grid, px, py, x, y):
                            visible.add((x, y))
        return visible

    def _los(self, grid: List[List[str]], x0: int, y0: int, x1: int, y1: int) -> bool:
        # Bresenham line; walls block sight
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            if (x, y) != (x0, y0) and grid[y][x] == 'wall':
                return False
            if (x, y) == (x1, y1):
                return True
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    # ---------------- Generation -----------------
    def _gen_map(self, cols: int, rows: int, rng: random.Random, theme: Dict) -> Tuple[List[List[str]], List[Tuple[int,int,int,int]]]:
        grid = [['wall' for _ in range(cols)] for _ in range(rows)]
        rooms: List[Tuple[int, int, int, int]] = []
        n_rooms = 6
        for _ in range(n_rooms):
            w = rng.randrange(5, 9)
            h = rng.randrange(4, 7)
            x = rng.randrange(1, max(2, cols - w - 1))
            y = rng.randrange(1, max(2, rows - h - 1))
            ok = True
            for rx, ry, rw, rh in rooms:
                if (x < rx + rw + 1 and x + w + 1 > rx and y < ry + rh + 1 and y + h + 1 > ry):
                    ok = False
                    break
            if not ok:
                continue
            rooms.append((x, y, w, h))
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    grid[yy][xx] = 'floor'
        # Connect rooms with corridors
        rooms_sorted = sorted(rooms, key=lambda r: (r[0], r[1]))
        for i in range(1, len(rooms_sorted)):
            x1, y1, w1, h1 = rooms_sorted[i-1]
            x2, y2, w2, h2 = rooms_sorted[i]
            cx1, cy1 = x1 + w1 // 2, y1 + h1 // 2
            cx2, cy2 = x2 + w2 // 2, y2 + h2 // 2
            if random.random() < 0.5:
                self._carve_h(grid, cx1, cx2, cy1)
                self._carve_v(grid, cy1, cy2, cx2)
            else:
                self._carve_v(grid, cy1, cy2, cx1)
                self._carve_h(grid, cx1, cx2, cy2)
        return grid, rooms

    def _carve_h(self, grid, x1, x2, y):
        if x1 > x2:
            x1, x2 = x2, x1
        for x in range(x1, x2 + 1):
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = 'floor'

    def _carve_v(self, grid, y1, y2, x):
        if y1 > y2:
            y1, y2 = y2, y1
        for y in range(y1, y2 + 1):
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = 'floor'

    # ---------------- Helpers -----------------
    def _is_blocking(self, grid, x, y) -> bool:
        if x < 0 or y < 0 or y >= len(grid) or x >= len(grid[0]):
            return True
        return grid[y][x] == 'wall'

    def _monster_at(self, monsters: List[Monster], x: int, y: int) -> Optional[Monster]:
        for m in monsters:
            if m.x == x and m.y == y:
                return m
        return None

    def _player_attack(self, player, m: Monster, sword: Optional[Item], tarot: Optional[Item], log: List[str]) -> bool:
        # damage calc
        bonus = 0
        if tarot and tarot.data.get('stat') == 'attack':
            bonus += 1
        base = player['base_atk'] + bonus
        if sword:
            low, high = sword.data.get('atk', (1, 2))
            dmg = random.randint(low, high) + base
        else:
            dmg = base
        m.hp -= dmg
        log.append(f"you hit {m.name} for {dmg}")
        return m.hp <= 0

    def _monster_attack(self, m: Monster, player, log: List[str]) -> None:
        dmg = m.atk
        player['hp'] -= dmg
        log.append(f"{m.name} hits you for {dmg}")

    def _spawn_stairs(self, grid, rooms, rng: random.Random, player, monsters, items) -> Tuple[int, int]:
        tries = 100
        while tries > 0:
            rx, ry, rw, rh = rng.choice(rooms)
            x = rng.randrange(rx + 1, rx + rw - 1)
            y = rng.randrange(ry + 1, ry + rh - 1)
            if (x, y) != (player['x'], player['y']) and not self._monster_at(monsters, x, y) and (x, y) not in items:
                return (x, y)
            tries -= 1
        return (player['x'], player['y'])

    def _adjacent_free(self, grid, x, y, rng: random.Random) -> Optional[Tuple[int, int]]:
        choices = [(1,0),(-1,0),(0,1),(0,-1)]
        rng.shuffle(choices)
        for dx, dy in choices:
            nx, ny = x + dx, y + dy
            if not self._is_blocking(grid, nx, ny):
                return (nx, ny)
        return None

    def _step_monsters(self, grid, monsters: List[Monster], player, items: Dict[Tuple[int,int], Item], rng: random.Random) -> None:
        # Move keys that follow tough monsters
        for pos, it in list(items.items()):
            if it.kind == 'key' and 'follow' in it.data:
                # find current tough monster location
                target = None
                for m in monsters:
                    if m.tough:
                        target = (m.x, m.y)
                        break
                if target:
                    tx, ty = target
                    # move adjacent towards target
                    best = None
                    best_d = 1e9
                    for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                        nx, ny = tx + dx, ty + dy
                        if self._is_blocking(grid, nx, ny):
                            continue
                        if (nx, ny) in items and items[(nx, ny)] is not it:
                            continue
                        d = abs(nx - tx) + abs(ny - ty)
                        if d < best_d:
                            best_d = d
                            best = (nx, ny)
                    if best:
                        items.pop(pos, None)
                        items[best] = it

        px, py = player['x'], player['y']
        for m in monsters:
            # If adjacent, may attack (engage)
            if abs(m.x - px) + abs(m.y - py) == 1:
                self._monster_attack(m, player, [])
                continue
            # If in LOS and close, chase
            if self._los(grid, m.x, m.y, px, py) and (abs(m.x - px) + abs(m.y - py) <= 8):
                dx = 1 if px > m.x else (-1 if px < m.x else 0)
                dy = 1 if py > m.y else (-1 if py < m.y else 0)
                options = []
                if not self._is_blocking(grid, m.x + dx, m.y):
                    options.append((m.x + dx, m.y))
                if not self._is_blocking(grid, m.x, m.y + dy):
                    options.append((m.x, m.y + dy))
                if options:
                    nx, ny = rng.choice(options)
                    m.x, m.y = nx, ny
            else:
                # random walk
                for _ in range(4):
                    dx, dy = rng.choice([(1,0),(-1,0),(0,1),(0,-1)])
                    nx, ny = m.x + dx, m.y + dy
                    if not self._is_blocking(grid, nx, ny):
                        m.x, m.y = nx, ny
                        break

    def _drop_random_sword(self, items, grid, rooms, rng: random.Random):
        s = self._roll_sword(rng)
        self._drop_item(items, grid, rooms, Item('sword', s['name'], s['glyph'], data=s), rng)

    def _roll_sword(self, rng: random.Random) -> Dict:
        base = rng.choice(SWORDS)
        # randomize speed (fast/slow), radius (close/far), durability, atk
        speed = rng.choice(['fast', 'slow']) if 'speed' not in base else base['speed']
        radius = rng.choice(['close', 'far']) if 'radius' not in base else base['radius']
        dur = rng.randint(*base.get('dur', (2, 5)))
        atk = (base['atk'][0], base['atk'][1])
        knock = base.get('knock', 1)
        return {'name': base['name'], 'glyph': base['glyph'], 'desc': base['desc'], 'speed': speed, 'radius': radius, 'dur': dur, 'atk': atk, 'knock': knock}

    def _drop_random_tarot(self, items, grid, rooms, rng: random.Random):
        t = self._roll_tarot(rng)
        self._drop_item(items, grid, rooms, Item('tarot', t['name'], GLYPH_TAROT, color=t['color'], data=t), rng)

    def _roll_tarot(self, rng: random.Random) -> Dict:
        base = rng.choice(TAROTS)
        return dict(base)

    def _drop_item(self, items: Dict[Tuple[int,int], Item], grid, rooms, item: Item, rng: random.Random):
        tries = 200
        while tries > 0:
            rx, ry, rw, rh = rng.choice(rooms)
            x = rng.randrange(rx + 1, rx + rw - 1)
            y = rng.randrange(ry + 1, ry + rh - 1)
            if grid[y][x] == 'floor' and (x, y) not in items:
                items[(x, y)] = item
                return
            tries -= 1

    # ---------------- Inspection -----------------
    def _item_desc(self, it: Item) -> str:
        if it.kind == 'sword':
            d = it.data
            atk = d.get('atk', (1, 2))
            return (f"{it.glyph} {it.name}\n"
                    f"{d.get('desc','')}\n"
                    f"speed: {d.get('speed','?')}  radius: {d.get('radius','?')}\n"
                    f"durability: {d.get('dur','?')}  knockback: {d.get('knock',0)}\n"
                    f"attack: {atk[0]}–{atk[1]}")
        if it.kind == 'tarot':
            d = it.data
            return (f"{it.glyph} {it.name}\n"
                    f"{d.get('desc','')}\n"
                    f"stat: {d.get('stat','?')}  color: {it.color or d.get('color','?')}")
        if it.kind == 'key':
            return f"{it.glyph} {it.name}\nopens a locked chest"
        if it.kind == 'chest':
            return f"{it.glyph} locked chest\nneeds a yellow key"
        return f"{it.glyph} {it.name}"
