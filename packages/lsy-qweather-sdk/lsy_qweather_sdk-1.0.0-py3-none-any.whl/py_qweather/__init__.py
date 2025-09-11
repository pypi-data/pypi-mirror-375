"""
和风天气API Python SDK

提供完整的和风天气API接口封装，包括：
- 实时天气数据获取
- 每日天气预报获取
- 逐小时天气预报获取
- 天气灾害预警获取
- 自定义异常处理
- 多种主机支持
- 完整的错误处理
"""

from .api import (
    WeatherAPI,
    WeatherNow,
    WeatherDaily,
    WeatherHourly,
    WeatherWarning,
    WeatherRefer,
    WeatherResult,
    WeatherDailyResult,
    WeatherHourlyResult,
    WeatherWarningResult,
)
from .exceptions import WeatherError, WeatherNetworkError, WeatherAPIError, WeatherParseError

__version__ = "1.0.0"
__author__ = "py-qweather"

__all__ = [
    # API类
    "WeatherAPI",
    # 数据实体类
    "WeatherNow",
    "WeatherDaily",
    "WeatherHourly",
    "WeatherWarning",
    "WeatherRefer",
    "WeatherResult",
    "WeatherDailyResult",
    "WeatherHourlyResult",
    "WeatherWarningResult",
    # 异常类
    "WeatherError",
    "WeatherNetworkError",
    "WeatherAPIError",
    "WeatherParseError",
]
