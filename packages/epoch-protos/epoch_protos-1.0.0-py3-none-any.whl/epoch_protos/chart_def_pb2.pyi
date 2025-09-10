import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AxisDef(_message.Message):
    __slots__ = ("type", "label", "categories")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    type: _common_pb2.AxisType
    label: str
    categories: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, type: _Optional[_Union[_common_pb2.AxisType, str]] = ..., label: _Optional[str] = ..., categories: _Optional[_Iterable[str]] = ...) -> None: ...

class ChartDef(_message.Message):
    __slots__ = ("id", "title", "type", "category", "y_axis", "x_axis")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    Y_AXIS_FIELD_NUMBER: _ClassVar[int]
    X_AXIS_FIELD_NUMBER: _ClassVar[int]
    id: str
    title: str
    type: _common_pb2.EpochFolioDashboardWidget
    category: str
    y_axis: AxisDef
    x_axis: AxisDef
    def __init__(self, id: _Optional[str] = ..., title: _Optional[str] = ..., type: _Optional[_Union[_common_pb2.EpochFolioDashboardWidget, str]] = ..., category: _Optional[str] = ..., y_axis: _Optional[_Union[AxisDef, _Mapping]] = ..., x_axis: _Optional[_Union[AxisDef, _Mapping]] = ...) -> None: ...

class StraightLineDef(_message.Message):
    __slots__ = ("title", "value", "vertical")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    VERTICAL_FIELD_NUMBER: _ClassVar[int]
    title: str
    value: _common_pb2.Scalar
    vertical: bool
    def __init__(self, title: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.Scalar, _Mapping]] = ..., vertical: bool = ...) -> None: ...

class Band(_message.Message):
    __slots__ = ("to",)
    FROM_FIELD_NUMBER: _ClassVar[int]
    TO_FIELD_NUMBER: _ClassVar[int]
    to: _common_pb2.Scalar
    def __init__(self, to: _Optional[_Union[_common_pb2.Scalar, _Mapping]] = ..., **kwargs) -> None: ...

class Point(_message.Message):
    __slots__ = ("x", "y")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: _common_pb2.Scalar
    y: _common_pb2.Scalar
    def __init__(self, x: _Optional[_Union[_common_pb2.Scalar, _Mapping]] = ..., y: _Optional[_Union[_common_pb2.Scalar, _Mapping]] = ...) -> None: ...

class Line(_message.Message):
    __slots__ = ("data", "name", "dash_style", "line_width")
    DATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DASH_STYLE_FIELD_NUMBER: _ClassVar[int]
    LINE_WIDTH_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[Point]
    name: str
    dash_style: str
    line_width: int
    def __init__(self, data: _Optional[_Iterable[_Union[Point, _Mapping]]] = ..., name: _Optional[str] = ..., dash_style: _Optional[str] = ..., line_width: _Optional[int] = ...) -> None: ...

class LinesDef(_message.Message):
    __slots__ = ("chart_def", "lines", "straight_lines", "y_plot_bands", "x_plot_bands", "overlay", "stacked")
    CHART_DEF_FIELD_NUMBER: _ClassVar[int]
    LINES_FIELD_NUMBER: _ClassVar[int]
    STRAIGHT_LINES_FIELD_NUMBER: _ClassVar[int]
    Y_PLOT_BANDS_FIELD_NUMBER: _ClassVar[int]
    X_PLOT_BANDS_FIELD_NUMBER: _ClassVar[int]
    OVERLAY_FIELD_NUMBER: _ClassVar[int]
    STACKED_FIELD_NUMBER: _ClassVar[int]
    chart_def: ChartDef
    lines: _containers.RepeatedCompositeFieldContainer[Line]
    straight_lines: _containers.RepeatedCompositeFieldContainer[StraightLineDef]
    y_plot_bands: _containers.RepeatedCompositeFieldContainer[Band]
    x_plot_bands: _containers.RepeatedCompositeFieldContainer[Band]
    overlay: Line
    stacked: bool
    def __init__(self, chart_def: _Optional[_Union[ChartDef, _Mapping]] = ..., lines: _Optional[_Iterable[_Union[Line, _Mapping]]] = ..., straight_lines: _Optional[_Iterable[_Union[StraightLineDef, _Mapping]]] = ..., y_plot_bands: _Optional[_Iterable[_Union[Band, _Mapping]]] = ..., x_plot_bands: _Optional[_Iterable[_Union[Band, _Mapping]]] = ..., overlay: _Optional[_Union[Line, _Mapping]] = ..., stacked: bool = ...) -> None: ...

class HeatMapPoint(_message.Message):
    __slots__ = ("x", "y", "value")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    x: _common_pb2.Scalar
    y: _common_pb2.Scalar
    value: _common_pb2.Scalar
    def __init__(self, x: _Optional[_Union[_common_pb2.Scalar, _Mapping]] = ..., y: _Optional[_Union[_common_pb2.Scalar, _Mapping]] = ..., value: _Optional[_Union[_common_pb2.Scalar, _Mapping]] = ...) -> None: ...

class HeatMapDef(_message.Message):
    __slots__ = ("chart_def", "points")
    CHART_DEF_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    chart_def: ChartDef
    points: _containers.RepeatedCompositeFieldContainer[HeatMapPoint]
    def __init__(self, chart_def: _Optional[_Union[ChartDef, _Mapping]] = ..., points: _Optional[_Iterable[_Union[HeatMapPoint, _Mapping]]] = ...) -> None: ...

class BarDef(_message.Message):
    __slots__ = ("chart_def", "data", "straight_lines", "bar_width")
    CHART_DEF_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    STRAIGHT_LINES_FIELD_NUMBER: _ClassVar[int]
    BAR_WIDTH_FIELD_NUMBER: _ClassVar[int]
    chart_def: ChartDef
    data: _common_pb2.Array
    straight_lines: _containers.RepeatedCompositeFieldContainer[StraightLineDef]
    bar_width: int
    def __init__(self, chart_def: _Optional[_Union[ChartDef, _Mapping]] = ..., data: _Optional[_Union[_common_pb2.Array, _Mapping]] = ..., straight_lines: _Optional[_Iterable[_Union[StraightLineDef, _Mapping]]] = ..., bar_width: _Optional[int] = ...) -> None: ...

class HistogramDef(_message.Message):
    __slots__ = ("chart_def", "data", "straight_lines", "bins_count")
    CHART_DEF_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    STRAIGHT_LINES_FIELD_NUMBER: _ClassVar[int]
    BINS_COUNT_FIELD_NUMBER: _ClassVar[int]
    chart_def: ChartDef
    data: _common_pb2.Array
    straight_lines: _containers.RepeatedCompositeFieldContainer[StraightLineDef]
    bins_count: int
    def __init__(self, chart_def: _Optional[_Union[ChartDef, _Mapping]] = ..., data: _Optional[_Union[_common_pb2.Array, _Mapping]] = ..., straight_lines: _Optional[_Iterable[_Union[StraightLineDef, _Mapping]]] = ..., bins_count: _Optional[int] = ...) -> None: ...

class BoxPlotDataPoint(_message.Message):
    __slots__ = ("low", "q1", "median", "q3", "high")
    LOW_FIELD_NUMBER: _ClassVar[int]
    Q1_FIELD_NUMBER: _ClassVar[int]
    MEDIAN_FIELD_NUMBER: _ClassVar[int]
    Q3_FIELD_NUMBER: _ClassVar[int]
    HIGH_FIELD_NUMBER: _ClassVar[int]
    low: float
    q1: float
    median: float
    q3: float
    high: float
    def __init__(self, low: _Optional[float] = ..., q1: _Optional[float] = ..., median: _Optional[float] = ..., q3: _Optional[float] = ..., high: _Optional[float] = ...) -> None: ...

class BoxPlotOutlier(_message.Message):
    __slots__ = ("category_index", "value")
    CATEGORY_INDEX_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    category_index: int
    value: float
    def __init__(self, category_index: _Optional[int] = ..., value: _Optional[float] = ...) -> None: ...

class BoxPlotDataPointDef(_message.Message):
    __slots__ = ("outliers", "points")
    OUTLIERS_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    outliers: _containers.RepeatedCompositeFieldContainer[BoxPlotOutlier]
    points: _containers.RepeatedCompositeFieldContainer[BoxPlotDataPoint]
    def __init__(self, outliers: _Optional[_Iterable[_Union[BoxPlotOutlier, _Mapping]]] = ..., points: _Optional[_Iterable[_Union[BoxPlotDataPoint, _Mapping]]] = ...) -> None: ...

class BoxPlotDef(_message.Message):
    __slots__ = ("chart_def", "data")
    CHART_DEF_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    chart_def: ChartDef
    data: BoxPlotDataPointDef
    def __init__(self, chart_def: _Optional[_Union[ChartDef, _Mapping]] = ..., data: _Optional[_Union[BoxPlotDataPointDef, _Mapping]] = ...) -> None: ...

class XRangePoint(_message.Message):
    __slots__ = ("x", "x2", "y", "is_long")
    X_FIELD_NUMBER: _ClassVar[int]
    X2_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    IS_LONG_FIELD_NUMBER: _ClassVar[int]
    x: _common_pb2.Scalar
    x2: _common_pb2.Scalar
    y: int
    is_long: bool
    def __init__(self, x: _Optional[_Union[_common_pb2.Scalar, _Mapping]] = ..., x2: _Optional[_Union[_common_pb2.Scalar, _Mapping]] = ..., y: _Optional[int] = ..., is_long: bool = ...) -> None: ...

class XRangeDef(_message.Message):
    __slots__ = ("chart_def", "categories", "points")
    CHART_DEF_FIELD_NUMBER: _ClassVar[int]
    CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    chart_def: ChartDef
    categories: _containers.RepeatedScalarFieldContainer[str]
    points: _containers.RepeatedCompositeFieldContainer[XRangePoint]
    def __init__(self, chart_def: _Optional[_Union[ChartDef, _Mapping]] = ..., categories: _Optional[_Iterable[str]] = ..., points: _Optional[_Iterable[_Union[XRangePoint, _Mapping]]] = ...) -> None: ...

class PieData(_message.Message):
    __slots__ = ("name", "y")
    NAME_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    name: str
    y: _common_pb2.Scalar
    def __init__(self, name: _Optional[str] = ..., y: _Optional[_Union[_common_pb2.Scalar, _Mapping]] = ...) -> None: ...

class PieDataDef(_message.Message):
    __slots__ = ("name", "points", "size", "inner_size")
    NAME_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    INNER_SIZE_FIELD_NUMBER: _ClassVar[int]
    name: str
    points: _containers.RepeatedCompositeFieldContainer[PieData]
    size: str
    inner_size: str
    def __init__(self, name: _Optional[str] = ..., points: _Optional[_Iterable[_Union[PieData, _Mapping]]] = ..., size: _Optional[str] = ..., inner_size: _Optional[str] = ...) -> None: ...

class PieDef(_message.Message):
    __slots__ = ("chart_def", "data")
    CHART_DEF_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    chart_def: ChartDef
    data: _containers.RepeatedCompositeFieldContainer[PieDataDef]
    def __init__(self, chart_def: _Optional[_Union[ChartDef, _Mapping]] = ..., data: _Optional[_Iterable[_Union[PieDataDef, _Mapping]]] = ...) -> None: ...

class Chart(_message.Message):
    __slots__ = ("lines_def", "heat_map_def", "bar_def", "histogram_def", "box_plot_def", "x_range_def", "pie_def")
    LINES_DEF_FIELD_NUMBER: _ClassVar[int]
    HEAT_MAP_DEF_FIELD_NUMBER: _ClassVar[int]
    BAR_DEF_FIELD_NUMBER: _ClassVar[int]
    HISTOGRAM_DEF_FIELD_NUMBER: _ClassVar[int]
    BOX_PLOT_DEF_FIELD_NUMBER: _ClassVar[int]
    X_RANGE_DEF_FIELD_NUMBER: _ClassVar[int]
    PIE_DEF_FIELD_NUMBER: _ClassVar[int]
    lines_def: LinesDef
    heat_map_def: HeatMapDef
    bar_def: BarDef
    histogram_def: HistogramDef
    box_plot_def: BoxPlotDef
    x_range_def: XRangeDef
    pie_def: PieDef
    def __init__(self, lines_def: _Optional[_Union[LinesDef, _Mapping]] = ..., heat_map_def: _Optional[_Union[HeatMapDef, _Mapping]] = ..., bar_def: _Optional[_Union[BarDef, _Mapping]] = ..., histogram_def: _Optional[_Union[HistogramDef, _Mapping]] = ..., box_plot_def: _Optional[_Union[BoxPlotDef, _Mapping]] = ..., x_range_def: _Optional[_Union[XRangeDef, _Mapping]] = ..., pie_def: _Optional[_Union[PieDef, _Mapping]] = ...) -> None: ...
