"""Quick test for GetControllerMap."""

import grpc
import sys
from grpc_server.generated import sensei_rpc_pb2, sensei_rpc_pb2_grpc


def main():
    """Quick test client."""
    server_address = "localhost:50051"

    print(f"Connecting to {server_address}...")

    try:
        channel = grpc.insecure_channel(server_address)
        stub = sensei_rpc_pb2_grpc.SenseiControllerStub(channel)
        grpc.channel_ready_future(channel).result(timeout=5)
        print("Connected!\n")

        # Test GetControllerMap
        print("=== Testing GetControllerMap ===\n")
        request = sensei_rpc_pb2.GenericVoidValue()
        response = stub.GetControllerMap(request)

        print(f"Pot States: {len(response.pots)} pots")
        for pot in response.pots:
            print(f"  - {pot.name} (id={pot.id})")

        print(f"\nSwitch States: {len(response.switches)} switches")
        for switch in response.switches:
            print(f"  - {switch.name} (id={switch.id})")

        print(f"\nEncoder States: {len(response.encoders)} encoders")
        for encoder in response.encoders:
            print(f"  - {encoder.name} (id={encoder.id})")

        print(f"\nRotary States: {len(response.rotaries)} rotaries")
        for rotary in response.rotaries:
            print(f"  - {rotary.name} (id={rotary.id})")

        print(f"\nLED States: {len(response.leds)} LEDs")
        for led in response.leds:
            print(f"  - {led.name} (id={led.id})")

        # Test UpdateLed
        print("\n=== Testing UpdateLed ===\n")
        for controller_id in [50, 51, 52, 53]:
            stub.UpdateLed(sensei_rpc_pb2.UpdateLedRequest(controller_id=controller_id, active=True))
            print(f"LED {controller_id} turned ON")

        print("\n✓ All tests passed!")
        channel.close()

    except grpc.FutureTimeoutError:
        print(f"Error: Could not connect to server")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
