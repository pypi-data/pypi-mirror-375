# lsy-qweather-sdk

和风天气开发服务 Python SDK

[![PyPI version](https://badge.fury.io/py/lsy-qweather-sdk.svg)](https://badge.fury.io/py/lsy-qweather-sdk)
[![Python Version](https://img.shields.io/pypi/pyversions/lsy-qweather-sdk.svg)](https://pypi.org/project/lsy-qweather-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 简介

`lsy-qweather-sdk` 是和风天气开发服务的非官方Python SDK，为开发者提供简单易用的天气数据接口。支持实时天气、天气预报、逐小时预报和天气预警等功能。

### ✨ 主要特性

- 🌤️ **实时天气**: 获取当前天气状况
- 📅 **天气预报**: 获取3-30天天气预报
- ⏰ **逐小时预报**: 获取未来168小时逐小时天气
- 🚨 **天气预警**: 获取官方天气灾害预警信息
- 🛠️ **异常处理**: 完善的错误处理机制
- 🌐 **多语言支持**: 支持多种语言和单位制
- 🏗️ **易于使用**: 简洁的API设计

### 📊 支持的天气数据

| 数据类型 | API方法 | 描述 |
|---------|---------|------|
| 实时天气 | `get_weather_now()` | 当前实时天气状况 |
| 天气预报 | `get_weather_daily()` | 3-30天天气预报 |
| 逐小时预报 | `get_weather_hourly()` | 未来168小时天气 |
| 天气预警 | `get_weather_warning()` | 官方灾害预警信息 |

## 🚀 快速开始

### 安装

```bash
pip install lsy-qweather-sdk
```

### 基本使用

```python
from py_qweather import WeatherAPI

# 创建API实例
api = WeatherAPI("your_api_key_here")

# 获取北京实时天气
result = api.get_weather_now(116.41, 39.92)
print(f"当前温度: {result.now.temp}°C")
print(f"天气状况: {result.now.text}")
print(f"体感温度: {result.now.feelsLike}°C")

# 获取3天天气预报
daily_result = api.get_weather_daily(116.41, 39.92, days=3)
for day in daily_result.daily:
    print(f"{day.fxDate}: {day.textDay}, {day.tempMin}°C ~ {day.tempMax}°C")

# 获取天气预警
warning_result = api.get_weather_warning(116.41, 39.92)
if warning_result.warning:
    for warning in warning_result.warning:
        print(f"⚠️ {warning.typeName}: {warning.severity}")
else:
    print("当前无天气预警")
```

## 📚 详细文档

### API密钥获取

1. 访问 [和风天气开发平台](https://dev.qweather.com/)
2. 注册账户并创建应用
3. 获取API密钥（API Key）

### WeatherAPI 类

#### 初始化

```python
WeatherAPI(api_key: str, host: str = None)
```

- `api_key`: 和风天气API密钥
- `host`: 自定义API主机（可选）

```python
# 使用默认主机
api = WeatherAPI("your_api_key")

# 使用自定义主机
api = WeatherAPI("your_api_key", "custom.api.host")
```

### 实时天气

#### get_weather_now

获取实时天气数据。

```python
get_weather_now(lng: float, lat: float, lang: str = "zh", unit: str = "m") -> WeatherResult
```

**参数:**
- `lng`: 经度坐标
- `lat`: 纬度坐标  
- `lang`: 语言参数，默认"zh"
- `unit`: 单位制，默认"m"（公制）

**返回值:** `WeatherResult` 对象

**示例:**
```python
# 获取上海实时天气
result = api.get_weather_now(121.47, 31.23)

print(f"温度: {result.now.temp}°C")
print(f"天气: {result.now.text}")
print(f"湿度: {result.now.humidity}%")
print(f"风向: {result.now.windDir}")
print(f"风速: {result.now.windSpeed} km/h")
print(f"气压: {result.now.pressure} hPa")
print(f"能见度: {result.now.vis} km")
```

### 天气预报

#### get_weather_daily

获取天气预报数据。

```python
get_weather_daily(lng: float, lat: float, days: int = 3, lang: str = "zh", unit: str = "m") -> WeatherDailyResult
```

**参数:**
- `lng`: 经度坐标
- `lat`: 纬度坐标
- `days`: 预报天数（3, 7, 10, 15, 30）
- `lang`: 语言参数，默认"zh"  
- `unit`: 单位制，默认"m"

**返回值:** `WeatherDailyResult` 对象

**示例:**
```python
# 获取广州7天天气预报
result = api.get_weather_daily(113.23, 23.16, days=7)

for day in result.daily:
    print(f"日期: {day.fxDate}")
    print(f"白天: {day.textDay}, {day.tempMax}°C")
    print(f"夜晚: {day.textNight}, {day.tempMin}°C")
    print(f"湿度: {day.humidity}%")
    print(f"降水概率: {day.pop}%")
    print("-" * 30)
```

### 逐小时预报

#### get_weather_hourly

获取逐小时天气预报。

```python
get_weather_hourly(lng: float, lat: float, hours: int = 24, lang: str = "zh", unit: str = "m") -> WeatherHourlyResult
```

**参数:**
- `lng`: 经度坐标
- `lat`: 纬度坐标
- `hours`: 预报小时数（24, 72, 168）
- `lang`: 语言参数，默认"zh"
- `unit`: 单位制，默认"m"

**返回值:** `WeatherHourlyResult` 对象

**示例:**
```python
# 获取深圳未来24小时天气
result = api.get_weather_hourly(114.07, 22.62, hours=24)

for hour in result.hourly[:6]:  # 显示前6小时
    print(f"时间: {hour.fxTime}")
    print(f"温度: {hour.temp}°C")
    print(f"天气: {hour.text}")
    print(f"降水概率: {hour.pop}%")
    print("-" * 20)
```

### 天气预警

#### get_weather_warning

获取天气灾害预警信息。

```python
get_weather_warning(lng: float, lat: float, lang: str = "zh") -> WeatherWarningResult
```

**参数:**
- `lng`: 经度坐标
- `lat`: 纬度坐标
- `lang`: 语言参数，默认"zh"

**返回值:** `WeatherWarningResult` 对象

**示例:**
```python
# 获取成都天气预警
result = api.get_weather_warning(104.07, 30.67)

if result.warning:
    for warning in result.warning:
        print(f"预警类型: {warning.typeName}")
        print(f"严重等级: {warning.severity}")
        print(f"预警状态: {warning.status}")
        print(f"发布时间: {warning.pubTime}")
        print(f"预警内容: {warning.text}")
        print("-" * 40)
else:
    print("当前无天气预警信息")
```

## 🎯 数据模型

### WeatherNow - 实时天气

| 字段 | 类型 | 描述 |
|------|------|------|
| obsTime | str | 观测时间 |
| temp | str | 温度（°C） |
| feelsLike | str | 体感温度 |
| icon | str | 天气状况图标 |
| text | str | 天气状况描述 |
| wind360 | str | 风向360角度 |
| windDir | str | 风向 |
| windScale | str | 风力等级 |
| windSpeed | str | 风速（km/h） |
| humidity | str | 相对湿度（%） |
| precip | str | 当前小时累计降水量 |
| pressure | str | 大气压强 |
| vis | str | 能见度（km） |
| cloud | str | 云量（%） |
| dew | str | 露点温度 |

### WeatherDaily - 天气预报

| 字段 | 类型 | 描述 |
|------|------|------|
| fxDate | str | 预报日期 |
| sunrise | str | 日出时间 |
| sunset | str | 日落时间 |
| moonrise | str | 月升时间 |
| moonset | str | 月落时间 |
| moonPhase | str | 月相名称 |
| moonPhaseIcon | str | 月相图标 |
| tempMax | str | 最高温度 |
| tempMin | str | 最低温度 |
| iconDay | str | 白天天气图标 |
| textDay | str | 白天天气描述 |
| iconNight | str | 夜晚天气图标 |
| textNight | str | 夜晚天气描述 |
| wind360Day | str | 白天风向360角度 |
| windDirDay | str | 白天风向 |
| windScaleDay | str | 白天风力等级 |
| windSpeedDay | str | 白天风速 |
| wind360Night | str | 夜晚风向360角度 |
| windDirNight | str | 夜晚风向 |
| windScaleNight | str | 夜晚风力等级 |
| windSpeedNight | str | 夜晚风速 |
| humidity | str | 相对湿度 |
| precip | str | 预计降水量 |
| pressure | str | 大气压强 |
| vis | str | 能见度 |
| cloud | str | 云量 |
| uvIndex | str | 紫外线强度指数 |

### WeatherHourly - 逐小时预报

| 字段 | 类型 | 描述 |
|------|------|------|
| fxTime | str | 预报时间 |
| temp | str | 温度 |
| icon | str | 天气状况图标 |
| text | str | 天气状况 |
| wind360 | str | 风向360角度 |
| windDir | str | 风向 |
| windScale | str | 风力等级 |
| windSpeed | str | 风速 |
| humidity | str | 相对湿度 |
| pop | str | 逐小时预报降水概率 |
| precip | str | 逐小时预报降水量 |
| pressure | str | 大气压强 |
| cloud | str | 云量 |
| dew | str | 露点温度 |

### WeatherWarning - 天气预警

| 字段 | 类型 | 描述 |
|------|------|------|
| id | str | 预警唯一标识 |
| sender | str | 预警发布单位 |
| pubTime | str | 预警发布时间 |
| title | str | 预警信息标题 |
| startTime | str | 预警开始时间 |
| endTime | str | 预警结束时间 |
| status | str | 预警信息状态 |
| severity | str | 预警严重等级 |
| severityColor | str | 预警等级颜色 |
| type | str | 预警类型ID |
| typeName | str | 预警类型名称 |
| urgency | str | 预警信息紧迫程度 |
| certainty | str | 预警信息确定性 |
| text | str | 预警详细文字描述 |
| related | str | 关联预警ID |

## ⚙️ 高级功能

### 多语言支持

支持多种语言的天气数据：

```python
# 中文（默认）
result_zh = api.get_weather_now(116.41, 39.92, lang="zh")

# 英文
result_en = api.get_weather_now(116.41, 39.92, lang="en")

# 日文
result_ja = api.get_weather_now(116.41, 39.92, lang="ja")
```

### 单位制选择

支持不同的单位制：

```python
# 公制单位（默认）
result_metric = api.get_weather_now(116.41, 39.92, unit="m")

# 英制单位
result_imperial = api.get_weather_now(116.41, 39.92, unit="i")
```

### 自定义API主机

支持使用自定义API主机：

```python
# 商业版用户可使用专用主机
api = WeatherAPI("your_api_key", "api.qweather.com")

# 开发版用户使用免费主机（默认）
api = WeatherAPI("your_api_key")  # 自动使用 devapi.qweather.com
```

### JSON序列化

所有数据模型都支持JSON序列化：

```python
result = api.get_weather_now(116.41, 39.92)

# 转换为JSON字符串
json_str = result.to_json()
print(json_str)

# 转换为字典
data_dict = result.to_dict()
print(data_dict)
```

## ❌ 异常处理

SDK提供了完善的异常处理机制：

```python
from py_qweather import (
    WeatherAPI, 
    WeatherError, 
    WeatherNetworkError,
    WeatherAPIError, 
    WeatherParseError
)

try:
    api = WeatherAPI("your_api_key")
    result = api.get_weather_now(116.41, 39.92)
    
except WeatherNetworkError as e:
    print(f"网络错误: {e}")
    
except WeatherAPIError as e:
    print(f"API错误: {e}")
    print(f"错误代码: {e.error_code}")
    
except WeatherParseError as e:
    print(f"数据解析错误: {e}")
    
except WeatherError as e:
    print(f"通用天气错误: {e}")
```

### 异常类型

| 异常类 | 描述 |
|--------|------|
| WeatherError | 基础异常类 |
| WeatherNetworkError | 网络连接异常 |
| WeatherAPIError | API调用异常 |
| WeatherParseError | 数据解析异常 |

## 📝 完整示例

### 天气监控应用

```python
from py_qweather import WeatherAPI, WeatherError
import time

def weather_monitor():
    api = WeatherAPI("your_api_key_here")
    
    # 监控的城市坐标（北京）
    lng, lat = 116.41, 39.92
    
    try:
        # 获取实时天气
        current = api.get_weather_now(lng, lat)
        print("=== 实时天气 ===")
        print(f"温度: {current.now.temp}°C")
        print(f"天气: {current.now.text}")
        print(f"体感: {current.now.feelsLike}°C")
        print(f"湿度: {current.now.humidity}%")
        print()
        
        # 获取今日预报
        daily = api.get_weather_daily(lng, lat, days=1)
        today = daily.daily[0]
        print("=== 今日预报 ===")
        print(f"日期: {today.fxDate}")
        print(f"温度范围: {today.tempMin}°C ~ {today.tempMax}°C")
        print(f"白天: {today.textDay}")
        print(f"夜晚: {today.textNight}")
        print(f"降水概率: {today.pop if hasattr(today, 'pop') else 'N/A'}%")
        print()
        
        # 检查天气预警
        warnings = api.get_weather_warning(lng, lat)
        print("=== 天气预警 ===")
        if warnings.warning:
            for warning in warnings.warning:
                print(f"🚨 {warning.typeName}")
                print(f"   等级: {warning.severity}")
                print(f"   状态: {warning.status}")
                print(f"   内容: {warning.text}")
        else:
            print("✅ 当前无天气预警")
        
    except WeatherError as e:
        print(f"获取天气数据失败: {e}")

if __name__ == "__main__":
    weather_monitor()
```

### 多城市天气对比

```python
def compare_cities_weather():
    api = WeatherAPI("your_api_key_here")
    
    cities = {
        "北京": (116.41, 39.92),
        "上海": (121.47, 31.23),
        "广州": (113.23, 23.16),
        "深圳": (114.07, 22.62)
    }
    
    print("=== 多城市天气对比 ===")
    for city_name, (lng, lat) in cities.items():
        try:
            result = api.get_weather_now(lng, lat)
            print(f"{city_name}: {result.now.temp}°C, {result.now.text}")
        except WeatherError as e:
            print(f"{city_name}: 获取失败 - {e}")

if __name__ == "__main__":
    compare_cities_weather()
```

## 📊 API状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 204 | 请求成功，但你查询的地区暂时没有你需要的数据 |
| 400 | 请求错误，可能包含错误的请求参数或缺少必需的请求参数 |
| 401 | 认证失败，可能使用了错误的KEY、数字签名错误、KEY的类型错误 |
| 402 | 超过访问次数或余额不足以支持继续访问服务 |
| 403 | 无访问权限，可能是绑定的PackageName、BundleID、域名IP地址不一致 |
| 404 | 查询的数据或地区不存在 |
| 429 | 超过限定的QPM（每分钟访问次数） |
| 500 | 服务器错误 |

## 🔗 相关链接

- [和风天气开发平台](https://dev.qweather.com/)
- [和风天气API文档](https://dev.qweather.com/docs/api/)
- [项目源码](https://github.com/9kl/py-qweather)
- [问题反馈](https://github.com/9kl/py-qweather/issues)

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)

## 🤝 贡献

欢迎贡献代码！请查看 [Contributing Guidelines](CONTRIBUTING.md) 了解详情。

## 📞 支持

如果您在使用过程中遇到问题，可以通过以下方式获取帮助：

1. 查看 [常见问题](https://github.com/9kl/py-qweather/wiki/FAQ)
2. [提交Issue](https://github.com/9kl/py-qweather/issues)
3. 发送邮件至：chinafengheping@outlook.com

---

Made with ❤️ by lsy-qweather-sdk contributors
