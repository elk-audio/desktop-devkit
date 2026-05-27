# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mock Events GUI is a Python Qt6 application with an integrated gRPC server for mocking hardware controller events from ELK's STM32-based platform. The application dynamically generates UI controls from a JSON configuration file and exposes them via gRPC, allowing user applications to be tested on a dev machine without physical hardware.

## Key Commands

### Running the Application
```bash
uv run python main.py
```
Starts the Qt GUI and gRPC server. The server runs on port 50051 by default (configurable in `config.json`).

### Testing with Client
```bash
uv run python test_client.py
```
Runs the test client which connects to the gRPC server, queries states, updates LEDs, and subscribes to events for 10 seconds.

### Dependency Management
```bash
uv sync                    # Install/sync dependencies
```
Uses `uv` for dependency management (see `pyproject.toml`).

### Regenerating Protobuf Code
```bash
uv run python regenerate_proto.py
```
Regenerates Python files from `pin_events.proto` and automatically fixes the import statement in the generated gRPC file.

## Architecture

### Threading Model

The application uses a **dual-threaded architecture**:

1. **Qt GUI Thread**: Runs the Qt event loop and handles all UI interactions
2. **gRPC Thread Pool**: Handles incoming gRPC requests via ThreadPoolExecutor

**Critical Threading Considerations:**
- The `PinProxyServicer` is shared between both threads and uses thread-safe patterns
- All state access in the servicer is protected by `threading.Lock`
- LED updates from gRPC callbacks use Qt signals (`led_update_signal`) to safely update the GUI from the gRPC thread
- Never directly manipulate Qt widgets from the gRPC thread

### Component Structure

```
main.py                    # Entry point, starts gRPC server and Qt app
├── gui/
│   ├── config_loader.py   # Loads JSON config, defines dataclasses
│   └── main_window.py     # Qt GUI, creates controls dynamically
├── grpc_server/
│   ├── servicer.py        # gRPC service implementation
│   └── generated/         # Auto-generated protobuf code
│       ├── pin_events_pb2.py
│       └── pin_events_pb2_grpc.py
└── config.json            # Defines controls, LEDs, and server config
```

### Data Flow

1. **GUI → gRPC**: User interacts with control → MainWindow callback → Servicer emit method → Event broadcast to all subscribers
2. **gRPC → GUI**: Client calls UpdateLed → Servicer callback → Qt signal → MainWindow updates LED indicator
3. **State Management**: Servicer maintains pot/switch states for RefreshAllStates RPC

### Event Types and Control Mapping

- **AnalogEvent** (float): Slider with `event_type: "analog"` → normalized 0.0-1.0 values
- **RangeEvent** (int): Slider with `event_type: "range"` → discrete integer values
- **ToggleEvent** (bool): Button with `event_type: "toggle"` → checkable button
- **RelativeEvent** (int): Spinbox with `event_type: "relative"` → emits delta changes

### Configuration System

All UI controls are generated dynamically from `config.json`. To add a new control:
1. Add entry to `controls` array in `config.json`
2. Restart application - UI automatically includes the new control
3. No code changes required

### gRPC Service API

**PinProxyService** provides three RPCs:
- `SubscribeToEvents`: Server-side streaming, optional filtering by controller_ids
- `RefreshAllStates`: Unary, returns current state of all controls
- `UpdateLed`: Unary, updates LED indicator state in the GUI

### Protobuf Regeneration

The `regenerate_proto.py` script performs two steps:
1. Compiles `.proto` file using `grpc_tools.protoc`
2. Fixes import in `pin_events_pb2_grpc.py` from absolute to relative import

Always run this script after modifying `pin_events.proto`.

## Development Patterns

### Adding New Event Types

1. Update `pin_events.proto` with new message types
2. Run `uv run python regenerate_proto.py`
3. Add emit method in `servicer.py` (e.g., `emit_new_event`)
4. Add UI callback in `main_window.py` to call the emit method

### Thread Safety for New Features

When adding features that interact between GUI and gRPC:
- Use `threading.Lock` for shared state in the servicer
- Use Qt signals to update GUI from gRPC thread
- Connect signals to slots in MainWindow constructor

### Control State Registration

Controls must register their state with the servicer to appear in `RefreshAllStates`:
- Analog controls: call `servicer.register_pot_state()`
- Toggle controls: call `servicer.register_switch_state()`
