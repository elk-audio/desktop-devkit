from guru.mappings import PluginParameterMapping, Control
from guru import observer
from functools import partial 


MAPPINGS = [[
    # Example: Map a pot to a plugin parameter
    PluginParameterMapping(
        track_name="TRACK",
        plugin_name="gain",
        parameter_name="gain",
        controller_name="POT1",
        preprocessor=lambda x: x,  # Optional: transform 0-1 to 0-100
    ),
    Control(controller_name="SW1", cb=partial(observer.emit, "ToggleLedRequest", 53))
]]

