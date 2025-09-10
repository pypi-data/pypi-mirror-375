import asyncio
import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from textmode import TextmodeConsole, ROM_MAP

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single in-memory session for simplicity
_console: Optional[TextmodeConsole] = None
_game_task: Optional[asyncio.Task] = None


class StepRequest(BaseModel):
    key: str


def _reset_session():
    global _console, _game_task
    if _game_task and not _game_task.done():
        _game_task.cancel()
    _console = TextmodeConsole(cols=16, rows=16)
    _game_task = None


@app.post("/start")
async def start():
    global _console, _game_task
    _reset_session()
    # start demo game
    game = ROM_MAP.get("menu")()

    async def _run():
        try:
            await game.run(_console)  # type: ignore[arg-type]
        except asyncio.CancelledError:
            pass
        except Exception:
            # don't crash server on game error; mark over
            _console.gameOver()  # type: ignore[union-attr]
        finally:
            _console.gameOver()

    _game_task = asyncio.create_task(_run())
    # Return initial render
    # Allow a tiny loop turn in case game draws immediately
    await asyncio.sleep(0)
    return _console.render_payload()  # type: ignore[union-attr]


@app.post("/step")
async def step(req: StepRequest):
    global _console, _game_task
    if _console is None:
        raise HTTPException(status_code=400, detail="No active session. Call /start first.")
    key = (req.key or '').lower().strip()
    if key not in { 'up', 'down', 'left', 'right', 'enter' }:
        raise HTTPException(status_code=400, detail="Invalid key. Use up/down/left/right/enter")

    _console.enqueue_key(key)
    # Give the running game a chance to handle this key and re-render
    # A couple of yields are generally enough for simple UIs
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    return _console.render_payload()


# --- Static files (client) ---
WWW_DIR = Path(__file__).resolve().parent / "www"
if WWW_DIR.exists():
    # Serve client assets under "/" (e.g., /client.html)
    app.mount("/", StaticFiles(directory=str(WWW_DIR), html=True), name="static")