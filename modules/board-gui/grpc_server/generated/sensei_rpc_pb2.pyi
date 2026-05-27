from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GenericVoidValue(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AnalogEvent(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: float
    def __init__(self, value: _Optional[float] = ...) -> None: ...

class ToggleEvent(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: bool
    def __init__(self, value: bool = ...) -> None: ...

class RelativeEvent(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class RangeEvent(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class Event(_message.Message):
    __slots__ = ("controller_id", "timestamp", "analog_ev", "toggle_ev", "relative_ev", "range_ev")
    CONTROLLER_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ANALOG_EV_FIELD_NUMBER: _ClassVar[int]
    TOGGLE_EV_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_EV_FIELD_NUMBER: _ClassVar[int]
    RANGE_EV_FIELD_NUMBER: _ClassVar[int]
    controller_id: int
    timestamp: int
    analog_ev: AnalogEvent
    toggle_ev: ToggleEvent
    relative_ev: RelativeEvent
    range_ev: RangeEvent
    def __init__(self, controller_id: _Optional[int] = ..., timestamp: _Optional[int] = ..., analog_ev: _Optional[_Union[AnalogEvent, _Mapping]] = ..., toggle_ev: _Optional[_Union[ToggleEvent, _Mapping]] = ..., relative_ev: _Optional[_Union[RelativeEvent, _Mapping]] = ..., range_ev: _Optional[_Union[RangeEvent, _Mapping]] = ...) -> None: ...

class SubscribeRequest(_message.Message):
    __slots__ = ("controller_ids",)
    CONTROLLER_IDS_FIELD_NUMBER: _ClassVar[int]
    controller_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, controller_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class UpdateLedRequest(_message.Message):
    __slots__ = ("controller_id", "active")
    CONTROLLER_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    controller_id: int
    active: bool
    def __init__(self, controller_id: _Optional[int] = ..., active: bool = ...) -> None: ...

class WriteToDisplayRequest(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: str
    def __init__(self, data: _Optional[str] = ...) -> None: ...

class GetControllerMapResponse(_message.Message):
    __slots__ = ("pots", "switches", "encoders", "rotaries", "leds")
    POTS_FIELD_NUMBER: _ClassVar[int]
    SWITCHES_FIELD_NUMBER: _ClassVar[int]
    ENCODERS_FIELD_NUMBER: _ClassVar[int]
    ROTARIES_FIELD_NUMBER: _ClassVar[int]
    LEDS_FIELD_NUMBER: _ClassVar[int]
    pots: _containers.RepeatedCompositeFieldContainer[PotState]
    switches: _containers.RepeatedCompositeFieldContainer[SwitchState]
    encoders: _containers.RepeatedCompositeFieldContainer[EncoderState]
    rotaries: _containers.RepeatedCompositeFieldContainer[RotaryState]
    leds: _containers.RepeatedCompositeFieldContainer[LedState]
    def __init__(self, pots: _Optional[_Iterable[_Union[PotState, _Mapping]]] = ..., switches: _Optional[_Iterable[_Union[SwitchState, _Mapping]]] = ..., encoders: _Optional[_Iterable[_Union[EncoderState, _Mapping]]] = ..., rotaries: _Optional[_Iterable[_Union[RotaryState, _Mapping]]] = ..., leds: _Optional[_Iterable[_Union[LedState, _Mapping]]] = ...) -> None: ...

class PotState(_message.Message):
    __slots__ = ("name", "id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    id: int
    def __init__(self, name: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...

class SwitchState(_message.Message):
    __slots__ = ("name", "id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    id: int
    def __init__(self, name: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...

class EncoderState(_message.Message):
    __slots__ = ("name", "id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    id: int
    def __init__(self, name: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...

class RotaryState(_message.Message):
    __slots__ = ("name", "id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    id: int
    def __init__(self, name: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...

class LedState(_message.Message):
    __slots__ = ("name", "id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    id: int
    def __init__(self, name: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...
