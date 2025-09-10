from typing import Callable, List, Tuple, Type
from textmode import (
    TextmodeConsole,
    ROM_MAP, 
    register_rom
)

Label = str
Factory = Callable[[], object]

def discover_roms() -> List[Tuple[Label, Factory]]:
    """Discover ROMs from the central ROM_MAP.

    Excludes the Menu itself to avoid recursion in the menu listing.
    """
    items: List[Tuple[Label, Factory]] = []
    for name, cls in ROM_MAP.items():
        if name == 'menu':
            continue
        def make_factory(kls: Type[object]) -> Factory:
            return lambda: kls()
        items.append((name, make_factory(cls)))
    items.sort(key=lambda t: t[0].lower())
    return items


@register_rom("menu")
class MenuGame:
    async def run(self, console: TextmodeConsole) -> None:
        # keep it simple: small screen, black bg, white fg
        console.setScreen(16, 16)
        console.setBackgroundColor('black')
        console.setTextColor('white')
        
        # Discover available ROMs dynamically each time (in case files changed)
        roms_list = discover_roms()

        # Title
        console.writeAt('Textmode ROMs', 0, 0)
        console.writeAt('Choose a game:', 0, 2)

        if not roms_list:
            console.writeAt('No ROMs found.', 0, 4)
            console.writeAt('Press Enter...', 0, 6)
            await console.waitKey(lambda k: k == 'enter')
            return

        options: List[str] = [label for (label, _) in roms_list] + ['Quit']
        choice = await console.choices(options, y=4, width=max(12, max(len(o) for o in options) + 2))
        if choice == 'Quit' or choice is None:
            return

        # Find selected and launch
        for label, factory in roms_list:
            if label == choice:
                game = factory()
                console.clear()
                await game.run(console)  # type: ignore[arg-type]
                break
