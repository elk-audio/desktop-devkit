from guru.presets import Preset


preset_01 = Preset(
    "Short",
    initial_state=[
        {
            "processor": "Reverb",
            "parameters": {"dry": 0.0, "wet": 0.2, "room_size": 0.1, "width": 0.25, "damp": 0.9},
        },
    ],
)

preset_02 = Preset(
    "Medium",
    initial_state=[
        {
            "processor": "Reverb",
            "parameters": {
                "dry": 0.0,
                "wet": 0.5,
                "room_size": 0.5,
                "width": 0.6,
                "damp": 0.5,
            },
        }
    ],
)

preset_03 = Preset(
    "Long",
    initial_state=[
        {
            "processor": "Reverb",
            "parameters": {
                "dry": 0.0,
                "wet": 1.0,
                "room_size": 0.89,
                "width": 1.0,
                "damp": 0.3,
            },
        },
    ],
)
