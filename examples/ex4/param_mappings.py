from guru.mappings import PluginParameterMapping, BypassMapping

MAPPINGS = [[

    PluginParameterMapping(
        track_name="bass",
        plugin_name="bass",
        parameter_name="gain",
        controller_name="POT1",
        preprocessor=lambda x: 0.6 + x * 0.4,  # Optional: transform 0-1 to 0-100
    ),
    PluginParameterMapping(
        track_name="kick",
        plugin_name="kick",
        parameter_name="gain",
        controller_name="POT2",
        preprocessor=lambda x: 0.6 + x * 0.4,  # Optional: transform 0-1 to 0-100
    ),
    PluginParameterMapping(
        track_name="snare",
        plugin_name="snare",
        parameter_name="gain",
        controller_name="POT3",
        preprocessor=lambda x: 0.6 + x * 0.4,  # Optional: transform 0-1 to 0-100
    ),
    PluginParameterMapping(
        track_name="hat",
        plugin_name="hat",
        parameter_name="gain",
        controller_name="POT4",
        preprocessor=lambda x: 0.6 + x * 0.4,  # Optional: transform 0-1 to 0-100
    ),
    PluginParameterMapping(
        track_name="bass",
        plugin_name="synth",
        parameter_name="VCF Freq",
        controller_name="POT5",
        preprocessor=lambda x: 0.5 + x * 0.5,  # Optional: transform 0-1 to 0-100
    ),
    PluginParameterMapping(
        track_name="bass",
        plugin_name="synth",
        parameter_name="VCF Reso",
        controller_name="POT6",
        preprocessor=lambda x: x,  # Optional: transform 0-1 to 0-100
    ),
    PluginParameterMapping(
        track_name="bass",
        plugin_name="chorus",
        parameter_name="amount",
        controller_name="POT7",
        preprocessor=lambda x: x,  # Optional: transform 0-1 to 0-100
    ),
    PluginParameterMapping(
        track_name="aux_drums",
        plugin_name="reverb",
        parameter_name="wet",
        controller_name="POT8",
        preprocessor=lambda x: x,  # Optional: transform 0-1 to 0-100
    ),
    BypassMapping(plugin_name="synth", controller_name="SW1"),

]]
