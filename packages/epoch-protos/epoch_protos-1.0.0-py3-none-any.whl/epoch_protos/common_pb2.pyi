from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EpochFolioDashboardWidget(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WidgetUnspecified: _ClassVar[EpochFolioDashboardWidget]
    WidgetCard: _ClassVar[EpochFolioDashboardWidget]
    WidgetLines: _ClassVar[EpochFolioDashboardWidget]
    WidgetBar: _ClassVar[EpochFolioDashboardWidget]
    WidgetDataTable: _ClassVar[EpochFolioDashboardWidget]
    WidgetXRange: _ClassVar[EpochFolioDashboardWidget]
    WidgetHistogram: _ClassVar[EpochFolioDashboardWidget]
    WidgetPie: _ClassVar[EpochFolioDashboardWidget]
    WidgetHeatMap: _ClassVar[EpochFolioDashboardWidget]
    WidgetBoxPlot: _ClassVar[EpochFolioDashboardWidget]
    WidgetArea: _ClassVar[EpochFolioDashboardWidget]
    WidgetColumn: _ClassVar[EpochFolioDashboardWidget]

class EpochFolioType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TypeUnspecified: _ClassVar[EpochFolioType]
    TypeString: _ClassVar[EpochFolioType]
    TypeInteger: _ClassVar[EpochFolioType]
    TypeDecimal: _ClassVar[EpochFolioType]
    TypePercent: _ClassVar[EpochFolioType]
    TypeBoolean: _ClassVar[EpochFolioType]
    TypeDateTime: _ClassVar[EpochFolioType]
    TypeDate: _ClassVar[EpochFolioType]
    TypeDayDuration: _ClassVar[EpochFolioType]
    TypeMonetary: _ClassVar[EpochFolioType]
    TypeDuration: _ClassVar[EpochFolioType]

class AxisType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AxisUnspecified: _ClassVar[AxisType]
    AxisLinear: _ClassVar[AxisType]
    AxisLogarithmic: _ClassVar[AxisType]
    AxisDateTime: _ClassVar[AxisType]
    AxisCategory: _ClassVar[AxisType]
WidgetUnspecified: EpochFolioDashboardWidget
WidgetCard: EpochFolioDashboardWidget
WidgetLines: EpochFolioDashboardWidget
WidgetBar: EpochFolioDashboardWidget
WidgetDataTable: EpochFolioDashboardWidget
WidgetXRange: EpochFolioDashboardWidget
WidgetHistogram: EpochFolioDashboardWidget
WidgetPie: EpochFolioDashboardWidget
WidgetHeatMap: EpochFolioDashboardWidget
WidgetBoxPlot: EpochFolioDashboardWidget
WidgetArea: EpochFolioDashboardWidget
WidgetColumn: EpochFolioDashboardWidget
TypeUnspecified: EpochFolioType
TypeString: EpochFolioType
TypeInteger: EpochFolioType
TypeDecimal: EpochFolioType
TypePercent: EpochFolioType
TypeBoolean: EpochFolioType
TypeDateTime: EpochFolioType
TypeDate: EpochFolioType
TypeDayDuration: EpochFolioType
TypeMonetary: EpochFolioType
TypeDuration: EpochFolioType
AxisUnspecified: AxisType
AxisLinear: AxisType
AxisLogarithmic: AxisType
AxisDateTime: AxisType
AxisCategory: AxisType

class Scalar(_message.Message):
    __slots__ = ("double_value", "int64_value", "uint64_value", "string_value", "bool_value", "timestamp_nanos", "null_value")
    DOUBLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    INT64_VALUE_FIELD_NUMBER: _ClassVar[int]
    UINT64_VALUE_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_NANOS_FIELD_NUMBER: _ClassVar[int]
    NULL_VALUE_FIELD_NUMBER: _ClassVar[int]
    double_value: float
    int64_value: int
    uint64_value: int
    string_value: str
    bool_value: bool
    timestamp_nanos: int
    null_value: _struct_pb2.NullValue
    def __init__(self, double_value: _Optional[float] = ..., int64_value: _Optional[int] = ..., uint64_value: _Optional[int] = ..., string_value: _Optional[str] = ..., bool_value: bool = ..., timestamp_nanos: _Optional[int] = ..., null_value: _Optional[_Union[_struct_pb2.NullValue, str]] = ...) -> None: ...

class Array(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedCompositeFieldContainer[Scalar]
    def __init__(self, values: _Optional[_Iterable[_Union[Scalar, _Mapping]]] = ...) -> None: ...
