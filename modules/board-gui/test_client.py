"""Test client for the Mock Events GUI gRPC server."""

import grpc
import sys
import time

from grpc_server.generated import sensei_rpc_pb2, sensei_rpc_pb2_grpc


def test_subscribe_to_events(stub):
    """Test the SubscribeToEvents RPC."""
    print("\n=== Testing SubscribeToEvents ===")

    request = sensei_rpc_pb2.SubscribeRequest()

    try:
        print("Subscribing to events (will listen for 10 seconds)...")
        event_stream = stub.SubscribeToEvents(request)

        start_time = time.time()
        event_count = 0

        for event in event_stream:
            elapsed = time.time() - start_time
            if elapsed > 10:
                break

            event_count += 1

            # Determine event type and print details
            if event.HasField('analog_ev'):
                ev = event.analog_ev
                print(f"[{event_count}] AnalogEvent: controller_id={event.controller_id}, value={ev.value:.3f}, timestamp={event.timestamp}")
            elif event.HasField('toggle_ev'):
                ev = event.toggle_ev
                print(f"[{event_count}] ToggleEvent: controller_id={event.controller_id}, value={ev.value}, timestamp={event.timestamp}")
            elif event.HasField('relative_ev'):
                ev = event.relative_ev
                print(f"[{event_count}] RelativeEvent: controller_id={event.controller_id}, value={ev.value}, timestamp={event.timestamp}")
            elif event.HasField('range_ev'):
                ev = event.range_ev
                print(f"[{event_count}] RangeEvent: controller_id={event.controller_id}, value={ev.value}, timestamp={event.timestamp}")

        print(f"\nReceived {event_count} events")

    except grpc.RpcError as e:
        print(f"RPC failed: {e.code()}: {e.details()}")
    except KeyboardInterrupt:
        print("\nSubscription cancelled by user")


def test_get_controller_map(stub):
    """Test the GetControllerMap RPC."""
    print("\n=== Testing GetControllerMap ===")

    request = sensei_rpc_pb2.GenericVoidValue()

    try:
        response = stub.GetControllerMap(request)

        print(f"\nPot States ({len(response.pots)} pots):")
        for pot in response.pots:
            print(f"  - {pot.name} (id={pot.id})")

        print(f"\nSwitch States ({len(response.switches)} switches):")
        for switch in response.switches:
            print(f"  - {switch.name} (id={switch.id})")

        print(f"\nEncoder States ({len(response.encoders)} encoders):")
        for encoder in response.encoders:
            print(f"  - {encoder.name} (id={encoder.id})")

        print(f"\nRotary States ({len(response.rotaries)} rotaries):")
        for rotary in response.rotaries:
            print(f"  - {rotary.name} (id={rotary.id})")

        print(f"\nLED States ({len(response.leds)} LEDs):")
        for led in response.leds:
            print(f"  - {led.name} (id={led.id})")

    except grpc.RpcError as e:
        print(f"RPC failed: {e.code()}: {e.details()}")


def test_update_led(stub, controller_id: int, active: bool):
    """Test the UpdateLed RPC."""
    print(f"\n=== Testing UpdateLed (controller_id={controller_id}, active={active}) ===")

    request = sensei_rpc_pb2.UpdateLedRequest(
        controller_id=controller_id,
        active=active
    )

    try:
        response = stub.UpdateLed(request)
        print(f"LED {controller_id} updated successfully")

    except grpc.RpcError as e:
        print(f"RPC failed: {e.code()}: {e.details()}")


def main():
    """Main test client."""
    server_address = "localhost:50051"

    print(f"Connecting to gRPC server at {server_address}...")

    try:
        # Create channel and stub
        channel = grpc.insecure_channel(server_address)
        stub = sensei_rpc_pb2_grpc.SenseiControllerStub(channel)

        # Wait for channel to be ready
        grpc.channel_ready_future(channel).result(timeout=5)
        print("Connected successfully!\n")

        # Run tests
        print("=" * 60)
        print("Mock Events GUI - gRPC Client Test")
        print("=" * 60)

        # Test GetControllerMap
        test_get_controller_map(stub)

        # Test UpdateLed - turn on red LEDs
        test_update_led(stub, controller_id=50, active=True)
        test_update_led(stub, controller_id=51, active=True)
        test_update_led(stub, controller_id=52, active=False)
        test_update_led(stub, controller_id=53, active=True)

        # Test SubscribeToEvents
        print("\n" + "=" * 60)
        print("Now interact with the GUI to generate events!")
        print("Move sliders, click buttons, change spinboxes...")
        print("=" * 60)
        test_subscribe_to_events(stub)

        channel.close()

    except grpc.FutureTimeoutError:
        print(f"Error: Could not connect to server at {server_address}")
        print("Make sure the GUI application is running.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
