from guru.mappings import PluginParameterMapping, BypassMapping


MAPPINGS = [[
    PluginParameterMapping(
        track_name="TRACK",
        plugin_name="SD2",
        parameter_name="DRIVE",
        controller_name="POT1",
        preprocessor=lambda x: x,  # Optional: transform 0-1 to 0-100
    ),
    PluginParameterMapping(
        track_name="TRACK",
        plugin_name="SD2",
        parameter_name="TONE",
        controller_name="POT2",
        preprocessor=lambda x: x,  # Optional: transform 0-1 to 0-100
    ),
    PluginParameterMapping(
        track_name="TRACK",
        plugin_name="SD2",
        parameter_name="LEVEL",
        controller_name="POT3",
        preprocessor=lambda x: x,  # Optional: transform 0-1 to 0-100
    ),
    BypassMapping(plugin_name="SD2", controller_name="SW1"),
    PluginParameterMapping(
        track_name="TRACK",
        plugin_name="Send_rev",
        parameter_name="gain",
        controller_name="POT6",
        preprocessor=lambda x: x,  # Optional: transform 0-1 to 0-100
    ),
    PluginParameterMapping(
        track_name="AUX",
        plugin_name="Reverb",
        parameter_name="room_size",
        controller_name="POT7",
        preprocessor=lambda x: x,  # Optional: transform 0-1 to 0-100
    ),
]]
