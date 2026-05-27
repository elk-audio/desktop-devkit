from guru.mappings import PluginParameterMapping, BypassMapping


MAPPINGS = [[
    # Example: Map a pot to a plugin parameter
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
]]
