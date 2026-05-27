import asyncio
import logging

from guru.app import GlueApp
from guru.display_manager import DisplayManager
from guru import observer
from param_mappings import MAPPINGS

async def main():
    app = GlueApp(mappings=MAPPINGS, log_level=logging.INFO)
    await app.initialize()

    dm = DisplayManager(app=app)

    await observer.emit("DrawText", "Example 02")
    return await app.run()


if __name__ == "__main__":
    asyncio.run(main())
