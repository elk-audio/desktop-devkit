# Mock Events GUI

A Python Qt6 GUI application with an integrated gRPC server for generating and streaming mock hardware events. The application dynamically generates UI controls (sliders, buttons, spinboxes) based on a JSON configuration file and exposes them via a gRPC service.

This program is there to help development of User applications for ELK's STM32-based platform. On that platform, hardware controller updates are accessible to a user application via **gRPC events** it can subscribe to. The present GUI intends 
to mock both the hardware controllers and the process that emits gRPC events so that the application can be tested on a dev machine.

## Features

- **Dynamic UI Generation**: Controls are automatically created from a JSON config file
- **gRPC Server**: Runs concurrently with the Qt GUI to serve events over the network
- **Multiple Event Types**:
  - `AnalogEvent`: Continuous float values (e.g., volume, frequency)
  - `RangeEvent`: Discrete integer values (e.g., channel selection)
  - `ToggleEvent`: Boolean values (e.g., play/pause, mute)
  - `RelativeEvent`: Relative changes (e.g., encoders, scroll wheels)
- **LED Indicators**: Visual feedback for remote LED state updates
- **Event Streaming**: Server-side streaming RPC for real-time event subscription
- **State Management**: Query all control states via `RefreshAllStates` RPC

## Requirements

- Python 3.13+
- PySide6 (Qt6 for Python)
- grpcio & grpcio-tools

All dependencies are managed via `uv` (see `pyproject.toml`).

## Installation

The project uses `uv` for dependency management:

```bash
# Install dependencies
uv sync
```

## Configuration

Edit `config.json` to customize the controls and server settings:

```json
{
  "server": {
    "port": 50051,
    "host": "0.0.0.0"
  },
  "controls": [
    {
      "type": "slider",
      "label": "Volume",
      "controller_id": 1,
      "event_type": "analog",
      "min": 0.0,
      "max": 1.0,
      "default": 0.5,
      "step": 0.01
    },
    {
      "type": "button",
      "label": "Play/Pause",
      "controller_id": 10,
      "event_type": "toggle"
    },
    {
      "type": "spinbox",
      "label": "Track Position",
      "controller_id": 20,
      "event_type": "relative",
      "min": -100,
      "max": 100,
      "default": 0,
      "step": 1
    }
  ],
  "leds": [
    {
      "id": 1,
      "label": "Power LED"
    }
  ]
}
```

### Control Types

- **slider**: For analog or range values
  - Use `event_type: "analog"` for float values
  - Use `event_type: "range"` for integer values
- **button**: For toggle/boolean values
  - Use `event_type: "toggle"`
- **spinbox**: For relative/incremental changes
  - Use `event_type: "relative"`

## Usage

### Running the GUI Application

```bash
uv run python main.py
```

This will:

1. Load configuration from `config.json`
2. Start the gRPC server on the configured port (default: 50051)
3. Open the Qt GUI with dynamically generated controls
4. Begin serving gRPC requests

### Testing with the Test Client

In a separate terminal, run the test client:

```bash
uv run python test_client.py
```

The test client will:

1. Connect to the gRPC server
2. Query all control states via `RefreshAllStates`
3. Update LED states via `UpdateLed`
4. Subscribe to events via `SubscribeToEvents` (listens for 10 seconds)

Interact with the GUI while the test client is running to see events being streamed.

## gRPC Service API

### PinProxyService

#### SubscribeToEvents (Server Streaming)

Subscribe to a stream of events from the GUI controls.

```protobuf
rpc SubscribeToEvents(SubscribeRequest) returns (stream Event);
```

Optional filtering by controller IDs:

```python
request = pin_events_pb2.SubscribeRequest(
    controller_ids=[1, 2, 10]  # Only receive events from these controllers
)
```

#### RefreshAllStates (Unary)

Get the current state of all controls.

```protobuf
rpc RefreshAllStates(RefreshAllStatesRequest) returns (RefreshAllStatesResponse);
```

Returns:

- List of pot (analog) states
- List of switch (toggle) states

#### UpdateLed (Unary)

Update the state of an LED indicator.

```protobuf
rpc UpdateLed(UpdateLedRequest) returns (GenericVoidValue);
```

Example:

```python
request = pin_events_pb2.UpdateLedRequest(
    led_id=1,
    active=True
)
stub.UpdateLed(request)
```

## Regenerating Protobuf Code

If you modify `pin_events.proto`, use the automated script to regenerate the Python code:

```bash
uv run python regenerate_proto.py
```

This script will:
1. Compile the `.proto` file using `grpc_tools.protoc`
2. Automatically fix the import statement in `pin_events_pb2_grpc.py`

## Development

### Adding New Controls

1. Edit `config.json` and add a new control entry
2. Restart the application
3. The UI will automatically include the new control

### Adding New Event Types

1. Update `pin_events.proto` with new message types
2. Regenerate protobuf code
3. Add handling in `servicer.py` (emit methods)
4. Add handling in `main_window.py` (UI callbacks)

## License

MIT
