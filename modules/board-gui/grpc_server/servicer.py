"""gRPC servicer implementation for PinProxyService."""

import threading
import time
from typing import Dict, List, Optional, Set, Callable
from queue import Queue

import grpc
from grpc_server.generated import sensei_rpc_pb2, sensei_rpc_pb2_grpc


class PinProxyServicer(sensei_rpc_pb2_grpc.SenseiControllerServicer):
    """Implementation of PinProxyService gRPC service."""

    def __init__(self):
        self._subscribers: List[Queue] = []
        self._subscribers_lock = threading.Lock()

        # State tracking
        self._pot_states: Dict[int, sensei_rpc_pb2.PotState] = {}
        self._switch_states: Dict[int, sensei_rpc_pb2.SwitchState] = {}
        self._encoder_states: Dict[int, sensei_rpc_pb2.EncoderState] = {}
        self._rotary_states: Dict[int, sensei_rpc_pb2.RotaryState] = {}
        self._led_states: Dict[int, sensei_rpc_pb2.LedState] = {}
        self._state_lock = threading.Lock()

        # LED update callback
        self._led_update_callback: Optional[Callable[[int, bool], None]] = None

        # Display update callback
        self._display_update_callback: Optional[Callable[[str], None]] = None

    def SubscribeToEvents(
        self, request: sensei_rpc_pb2.SubscribeRequest, context: grpc.ServicerContext
    ):
        """Server streaming RPC for event subscription."""
        event_queue = Queue()

        # Register subscriber
        with self._subscribers_lock:
            self._subscribers.append(event_queue)

        # Get controller filter (if any)
        controller_filter: Optional[Set[int]] = None
        if request.controller_ids:
            controller_filter = set(request.controller_ids)

        try:
            while context.is_active():
                try:
                    # Wait for events with timeout to check context
                    event = event_queue.get(timeout=0.1)

                    # Apply filter if specified
                    if controller_filter:
                        controller_id = self._get_event_controller_id(event)
                        if controller_id and controller_id not in controller_filter:
                            continue

                    yield event

                except Exception:
                    # Timeout - check if context is still active
                    continue
        finally:
            # Unregister subscriber
            with self._subscribers_lock:
                if event_queue in self._subscribers:
                    self._subscribers.remove(event_queue)

    def RefreshAllStates(
        self,
        request: sensei_rpc_pb2.GenericVoidValue,
        context: grpc.ServicerContext,
    ) -> sensei_rpc_pb2.GenericVoidValue:
        """Return current state of all controls."""
        return sensei_rpc_pb2.GenericVoidValue()

    def GetControllerMap(
        self, request: sensei_rpc_pb2.GenericVoidValue, context: grpc.ServicerContext
    ) -> sensei_rpc_pb2.GetControllerMapResponse:
        with self._state_lock:
            response = sensei_rpc_pb2.GetControllerMapResponse()
            response.pots.extend(self._pot_states.values())
            response.switches.extend(self._switch_states.values())
            response.encoders.extend(self._encoder_states.values())
            response.rotaries.extend(self._rotary_states.values())

            # Add LED states
            for led_id in self._led_states:
                response.leds.append(sensei_rpc_pb2.LedState(id=led_id, name="a led"))

            return response

    def UpdateLed(
        self, request: sensei_rpc_pb2.UpdateLedRequest, context: grpc.ServicerContext
    ) -> sensei_rpc_pb2.GenericVoidValue:
        """Update LED state."""
        with self._state_lock:
            self._led_states[request.controller_id] = request.active

        # Notify any listeners
        print(f"LED {request.controller_id} set to {'ON' if request.active else 'OFF'}")

        # Trigger callback if registered
        if self._led_update_callback:
            self._led_update_callback(request.controller_id, request.active)

        return sensei_rpc_pb2.GenericVoidValue()

    def WriteToDisplay(
        self,
        request: sensei_rpc_pb2.WriteToDisplayRequest,
        context: grpc.ServicerContext,
    ) -> sensei_rpc_pb2.GenericVoidValue:
        """Update display with message."""
        # Trigger callback if registered
        if self._display_update_callback:
            self._display_update_callback(request.data)

        return sensei_rpc_pb2.GenericVoidValue()

    # Helper methods for emitting events

    def emit_analog_event(self, controller_id: int, value: float):
        """Emit an analog event to all subscribers."""
        event = sensei_rpc_pb2.Event(
            controller_id=controller_id,
            timestamp=self._get_timestamp(),
            analog_ev=sensei_rpc_pb2.AnalogEvent(
                value=value,
            ),
        )
        self._broadcast_event(event)

    def emit_toggle_event(self, controller_id: int, value: bool):
        """Emit a toggle event to all subscribers."""
        event = sensei_rpc_pb2.Event(
            controller_id=controller_id,
            timestamp=self._get_timestamp(),
            toggle_ev=sensei_rpc_pb2.ToggleEvent(value=value),
        )
        self._broadcast_event(event)

    def emit_relative_event(self, controller_id: int, value: int):
        """Emit a relative event to all subscribers."""
        event = sensei_rpc_pb2.Event(
            controller_id=controller_id,
            timestamp=self._get_timestamp(),
            relative_ev=sensei_rpc_pb2.RelativeEvent(
                value=value,
            ),
        )
        self._broadcast_event(event)

    def emit_range_event(self, controller_id: int, value: int):
        """Emit a range event to all subscribers."""
        event = sensei_rpc_pb2.Event(
            controller_id=controller_id,
            timestamp=self._get_timestamp(),
            range_ev=sensei_rpc_pb2.RangeEvent(
                value=value,
            ),
        )
        self._broadcast_event(event)

    def register_pot_state(
        self, controller_id: int, name: str, device: str, initial_value: float
    ):
        """Register a pot (analog control) state."""
        with self._state_lock:
            self._pot_states[controller_id] = sensei_rpc_pb2.PotState(
                id=controller_id,
                name=name,
            )

    def register_switch_state(
        self, controller_id: int, name: str, device: str, initial_value: bool
    ):
        """Register a switch (toggle control) state."""
        with self._state_lock:
            self._switch_states[controller_id] = sensei_rpc_pb2.SwitchState(
                id=controller_id, name=name
            )

    def register_encoder_state(self, controller_id: int, name: str, device: str):
        """Register an encoder (relative control) state."""
        with self._state_lock:
            self._encoder_states[controller_id] = sensei_rpc_pb2.EncoderState(
                id=controller_id, name=name
            )

    def register_rotary_state(
        self, controller_id: int, name: str, device: str, initial_position: int
    ):
        """Register a rotary switch (range control) state."""
        with self._state_lock:
            self._rotary_states[controller_id] = sensei_rpc_pb2.RotaryState(
                id=controller_id, name=name
            )

    def get_led_state(self, led_id: int) -> bool:
        """Get current LED state."""
        with self._state_lock:
            return self._led_states.get(led_id, False)

    def set_led_update_callback(self, callback: Callable[[int, bool], None]):
        """Register a callback to be called when LED state changes."""
        self._led_update_callback = callback

    def set_display_update_callback(self, callback: Callable[[str], None]):
        """Register a callback to be called when display is updated."""
        self._display_update_callback = callback

    # Private helper methods

    def _broadcast_event(self, event: sensei_rpc_pb2.Event):
        """Broadcast event to all subscribers."""
        with self._subscribers_lock:
            for queue in self._subscribers:
                try:
                    queue.put_nowait(event)
                except Exception:
                    # Queue full, skip this subscriber
                    pass

    @staticmethod
    def _get_timestamp() -> int:
        """Get current timestamp in microseconds."""
        return int(time.time() * 1_000_000)

    @staticmethod
    def _get_event_controller_id(event: sensei_rpc_pb2.Event) -> Optional[int]:
        """Extract controller ID from event."""
        return event.controller_id
