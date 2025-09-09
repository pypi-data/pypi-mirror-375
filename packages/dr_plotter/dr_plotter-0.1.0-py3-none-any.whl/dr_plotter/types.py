from typing import Any, Union

import pandas as pd

type VisualChannel = str
type ColName = str
type StyleAttrName = str
type Phase = str
type ComponentSchema = dict[str, set[str]]
type ComponentStyles = dict[str, dict[str, Any]]
type GroupInfo = tuple[Any, pd.DataFrame]
type GroupContext = dict[str, Any]
type ColorPalette = list[str]
type SubplotCoord = tuple[int, int]
type ChannelName = str
type ExpectedChannels = dict[SubplotCoord, list[ChannelName]]
type VerificationParams = dict[str, Any]
type VerificationResult = dict[str, Any]
type RGBA = tuple[float, float, float, float]
type RGB = tuple[float, float, float]
type ColorTuple = Union[RGBA, RGB]
type NumericValue = Union[float, int]
type ComparisonValue = Union[NumericValue, ColorTuple, str]
type Position = tuple[float, float]
type CollectionProperties = dict[str, Any]
type StyleCacheKey = tuple[VisualChannel, Any]
