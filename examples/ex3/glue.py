import asyncio
import logging

from guru.app import GlueApp
from param_mappings import MAPPINGS
from guru.presets import PresetManager
from guru.display_manager import DisplayManager
from guru import observer

async def main():
    app = GlueApp(mappings=MAPPINGS, log_level=logging.INFO)
    await app.initialize()

    dm = DisplayManager(app=app)

    # Adding a PresetManager
    # Thanks to the event-signal system, that's all we need to do!
    pm = PresetManager()
    from sushi_presets import preset_01, preset_02, preset_03

    pm.add_preset(preset_01)
    pm.add_preset(preset_02)
    pm.add_preset(preset_03)
    await pm.initialize_presets()
    await pm.load_preset(0)

    await observer.emit("DrawText", "Example 03")
    return await app.run()


if __name__ == "__main__":
    asyncio.run(main())
