import asyncio
import logging

logger = logging.getLogger("MAIN")

from guru.app import GlueApp
from guru.display_manager import DisplayManager
from guru import observer
from param_mappings import MAPPINGS

STEPS = [1, 2, 3, 4, 5, 6, 7, 0]
N_LEDS = 4

PATTERNS = [
    [0.4166666666666667, 0.6666666666666666, 0.4166666666666667, 0.6666666666666666, 0.3125, 0.5625, 0.3125, 0.5625],
    [0.3541666666666667, 0.6041666666666666, 0.3541666666666667, 0.6041666666666666, 0.3541666666666667, 0.6041666666666666, 0.3541666666666667, 0.6041666666666666],
    [0.4583333333333333, 0.7083333333333334, 0.4583333333333333, 0.7083333333333334, 0.3125, 0.5625, 0.3125, 0.5625],
    [0.3541666666666667, 0.6041666666666666, 0.3541666666666667, 0.6041666666666666, 0.3541666666666667, 0.6041666666666666, 0.3541666666666667, 0.6041666666666666],
]


class AppState:
    def __init__(self, app):
        self.sc = app.sushi_client.controller
        self.sequencer_id = self.sc.audio_graph.get_processor_id('sequencer')
        self.step_pitches = [self.sc.parameters.get_parameter_id(self.sequencer_id, f'pitch_{n}') for n in STEPS]
        self.step_inds = [self.sc.parameters.get_parameter_id(self.sequencer_id, f'step_ind_{n}') for n in STEPS]

        self.cur_pattern = 0

    async def param_update(self, notif):
        if (     (notif.parameter.processor_id == self.sequencer_id)
            and  (notif.parameter.parameter_id in self.step_inds)
            and  (notif.normalized_value == 1) ):
                led_idx = self.step_inds.index(notif.parameter.parameter_id) % N_LEDS
                prev_led_idx = (led_idx - 1) % N_LEDS
                await observer.emit("ToggleLedRequest", 13 + prev_led_idx, False)
                await observer.emit("ToggleLedRequest", 13 + led_idx, True)

                if  (notif.parameter.parameter_id == self.step_inds[-1]):
                    self.cur_pattern = (self.cur_pattern + 1) % len(PATTERNS)
                    for n, pitch in zip(STEPS, PATTERNS[self.cur_pattern]):
                        self.sc.parameters.set_parameter_value(self.sequencer_id, self.step_pitches[n], pitch)


async def main():
    app = GlueApp(mappings=MAPPINGS, log_level=logging.INFO)
    await app.initialize()

    app.sushi_client.subscribe_to_parameter_updates()
    state = AppState(app)

    dm = DisplayManager(app=app)
    observer.subscribe("SushiParameterUpdate", cb=state.param_update)

    await observer.emit("DrawText", "Example 04")
    return await app.run()


if __name__ == "__main__":
    asyncio.run(main())
