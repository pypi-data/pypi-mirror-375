from textmode.engine import (
    TextmodeConsole, 
    ALLOWED_KEYS
)

ROM_MAP = {}
def register_rom(name: str):
    """Decorator to register a ROM class under a given name.

    Usage:
        from textmode.roms import register_rom

        @register_rom("my_rom")
        class MyRom:
            async def run(self, console): ...
    """
    def _decorator(cls):
        ROM_MAP[str(name)] = cls
        return cls
    return _decorator

# import ROMs to register them
import textmode.roms as _

__all__ = ['TextmodeConsole', 'ALLOWED_KEYS', 'register_rom', 'ROM_MAP']