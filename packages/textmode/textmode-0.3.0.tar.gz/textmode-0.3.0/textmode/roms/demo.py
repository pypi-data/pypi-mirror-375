import asyncio
from typing import Any
from textmode import TextmodeConsole, register_rom

@register_rom("demo")
class DemoGame:
    async def run(self, console: TextmodeConsole) -> None:
        # Initial size similar to existing demo
        console.setScreen(16, 16)
        # Show choices and branch like the JS demo
        demo = await console.choices(['demo1', 'demo2'])
        if demo == 'demo1':
            await console.dialogue('hello traveler welcome to the dungeon')
            console.writeAt(
                """\
┌♥♡♡─┐┌──┐
│∙∙∙⟏││†3│
│∙☠∙∙││⛨1│
│∙∙@∙││⚱⚱│
│∙∙∙∙││⚷⚷│
└────┘└──┘"""
            )
        else:
            console.setTextColor('red')
            console.setBackgroundColor('black')
            console.setTextStyle('italics')
            console.writeAt('Hello', 0, 0)

            console.setTextStyle('normal')
            console.setTextColor('white')
            console.setBackgroundColor('gray')
            console.writeAt('\nWorld', 0, 0)

        # After rendering, wait for Enter
        await console.waitKey(lambda k: k == 'enter')