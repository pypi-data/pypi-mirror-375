import requests
import json
from .exceptions import WeatherError, WeatherNetworkError, WeatherAPIError, WeatherParseError


class WeatherNow:
    def __init__(
        self,
        obsTime,
        temp,
        feelsLike,
        icon,
        text,
        wind360,
        windDir,
        windScale,
        windSpeed,
        humidity,
        precip,
        pressure,
        vis,
        cloud,
        dew,
    ):
        self.obsTime = obsTime  # 数据观测时间
        self.temp = temp  # 温度，默认单位：摄氏度
        self.feelsLike = feelsLike  # 体感温度，默认单位：摄氏度
        self.icon = icon  # 天气状况的图标代码
        self.text = text  # 天气状况的文字描述
        self.wind360 = wind360  # 风向360角度
        self.windDir = windDir  # 风向
        self.windScale = windScale  # 风力等级
        self.windSpeed = windSpeed  # 风速，公里/小时
        self.humidity = humidity  # 相对湿度，百分比数值
        self.precip = precip  # 过去1小时降水量，默认单位：毫米
        self.pressure = pressure  # 大气压强，默认单位：百帕
        self.vis = vis  # 能见度，默认单位：公里
        self.cloud = cloud  # 云量，百分比数值。可能为空
        self.dew = dew  # 露点温度。可能为空

    def to_json(self):
        return json.dumps(self.__dict__, ensure_ascii=False)


class WeatherDaily:
    def __init__(
        self,
        fxDate,
        sunrise,
        sunset,
        moonrise,
        moonset,
        moonPhase,
        moonPhaseIcon,
        tempMax,
        tempMin,
        iconDay,
        textDay,
        iconNight,
        textNight,
        wind360Day,
        windDirDay,
        windScaleDay,
        windSpeedDay,
        wind360Night,
        windDirNight,
        windScaleNight,
        windSpeedNight,
        humidity,
        precip,
        pressure,
        vis,
        cloud,
        uvIndex,
    ):
        self.fxDate = fxDate  # 预报日期
        self.sunrise = sunrise  # 日出时间，在高纬度地区可能为空
        self.sunset = sunset  # 日落时间，在高纬度地区可能为空
        self.moonrise = moonrise  # 当天月升时间，可能为空
        self.moonset = moonset  # 当天月落时间，可能为空
        self.moonPhase = moonPhase  # 月相名称
        self.moonPhaseIcon = moonPhaseIcon  # 月相图标代码
        self.tempMax = tempMax  # 预报当天最高温度
        self.tempMin = tempMin  # 预报当天最低温度
        self.iconDay = iconDay  # 预报白天天气状况的图标代码
        self.textDay = textDay  # 预报白天天气状况文字描述
        self.iconNight = iconNight  # 预报夜间天气状况的图标代码
        self.textNight = textNight  # 预报晚间天气状况文字描述
        self.wind360Day = wind360Day  # 预报白天风向360角度
        self.windDirDay = windDirDay  # 预报白天风向
        self.windScaleDay = windScaleDay  # 预报白天风力等级
        self.windSpeedDay = windSpeedDay  # 预报白天风速，公里/小时
        self.wind360Night = wind360Night  # 预报夜间风向360角度
        self.windDirNight = windDirNight  # 预报夜间当天风向
        self.windScaleNight = windScaleNight  # 预报夜间风力等级
        self.windSpeedNight = windSpeedNight  # 预报夜间风速，公里/小时
        self.humidity = humidity  # 相对湿度，百分比数值
        self.precip = precip  # 预报当天总降水量，默认单位：毫米
        self.pressure = pressure  # 大气压强，默认单位：百帕
        self.vis = vis  # 能见度，默认单位：公里
        self.cloud = cloud  # 云量，百分比数值。可能为空
        self.uvIndex = uvIndex  # 紫外线强度指数

    def to_json(self):
        return json.dumps(self.__dict__, ensure_ascii=False)


class WeatherHourly:
    def __init__(
        self,
        fxTime,
        temp,
        icon,
        text,
        wind360,
        windDir,
        windScale,
        windSpeed,
        humidity,
        pop,
        precip,
        pressure,
        cloud,
        dew,
    ):
        self.fxTime = fxTime  # 预报时间
        self.temp = temp  # 温度，默认单位：摄氏度
        self.icon = icon  # 天气状况的图标代码
        self.text = text  # 天气状况的文字描述
        self.wind360 = wind360  # 风向360角度
        self.windDir = windDir  # 风向
        self.windScale = windScale  # 风力等级
        self.windSpeed = windSpeed  # 风速，公里/小时
        self.humidity = humidity  # 相对湿度，百分比数值
        self.pop = pop  # 逐小时预报降水概率，百分比数值，可能为空
        self.precip = precip  # 当前小时累计降水量，默认单位：毫米
        self.pressure = pressure  # 大气压强，默认单位：百帕
        self.cloud = cloud  # 云量，百分比数值。可能为空
        self.dew = dew  # 露点温度。可能为空

    def to_json(self):
        return json.dumps(self.__dict__, ensure_ascii=False)


class WeatherWarning:
    def __init__(
        self,
        id,
        sender,
        pubTime,
        title,
        startTime,
        endTime,
        status,
        level,
        severity,
        severityColor,
        type,
        typeName,
        urgency,
        certainty,
        text,
        related,
    ):
        self.id = id  # 本条预警的唯一标识
        self.sender = sender  # 预警发布单位，可能为空
        self.pubTime = pubTime  # 预警发布时间
        self.title = title  # 预警信息标题
        self.startTime = startTime  # 预警开始时间，可能为空
        self.endTime = endTime  # 预警结束时间，可能为空
        self.status = status  # 预警信息的发布状态
        self.level = level  # 预警等级（已弃用）
        self.severity = severity  # 预警严重等级
        self.severityColor = severityColor  # 预警严重等级颜色，可能为空
        self.type = type  # 预警类型ID
        self.typeName = typeName  # 预警类型名称
        self.urgency = urgency  # 预警信息的紧迫程度，可能为空
        self.certainty = certainty  # 预警信息的确定性，可能为空
        self.text = text  # 预警详细文字描述
        self.related = related  # 与本条预警相关联的预警ID，可能为空

    def to_json(self):
        return json.dumps(self.__dict__, ensure_ascii=False)


class WeatherRefer:
    def __init__(self, sources, license):
        self.sources = sources  # 原始数据来源，或数据源说明，可能为空
        self.license = license  # 数据许可或版权声明，可能为空

    def to_json(self):
        return json.dumps(self.__dict__, ensure_ascii=False)


class WeatherResult:
    def __init__(self, code, updateTime, fxLink, now: WeatherNow, refer: WeatherRefer):
        self.code = code  # 状态码
        self.updateTime = updateTime  # 当前API的最近更新时间
        self.fxLink = fxLink  # 当前数据的响应式页面
        self.now = now  # 实况天气数据
        self.refer = refer  # 数据来源和许可

    def to_json(self):
        return json.dumps(
            {
                "code": self.code,
                "updateTime": self.updateTime,
                "fxLink": self.fxLink,
                "now": self.now.__dict__,
                "refer": self.refer.__dict__,
            },
            ensure_ascii=False,
        )


class WeatherDailyResult:
    def __init__(self, code, updateTime, fxLink, daily: list, refer: WeatherRefer):
        self.code = code  # 状态码
        self.updateTime = updateTime  # 当前API的最近更新时间
        self.fxLink = fxLink  # 当前数据的响应式页面
        self.daily = daily  # 每日天气预报数据列表
        self.refer = refer  # 数据来源和许可

    def to_json(self):
        return json.dumps(
            {
                "code": self.code,
                "updateTime": self.updateTime,
                "fxLink": self.fxLink,
                "daily": [day.__dict__ for day in self.daily],
                "refer": self.refer.__dict__,
            },
            ensure_ascii=False,
        )


class WeatherHourlyResult:
    def __init__(self, code, updateTime, fxLink, hourly: list, refer: WeatherRefer):
        self.code = code  # 状态码
        self.updateTime = updateTime  # 当前API的最近更新时间
        self.fxLink = fxLink  # 当前数据的响应式页面
        self.hourly = hourly  # 逐小时天气预报数据列表
        self.refer = refer  # 数据来源和许可

    def to_json(self):
        return json.dumps(
            {
                "code": self.code,
                "updateTime": self.updateTime,
                "fxLink": self.fxLink,
                "hourly": [hour.__dict__ for hour in self.hourly],
                "refer": self.refer.__dict__,
            },
            ensure_ascii=False,
        )


class WeatherWarningResult:
    def __init__(self, code, updateTime, fxLink, warning: list, refer: WeatherRefer):
        self.code = code  # 状态码
        self.updateTime = updateTime  # 当前API的最近更新时间
        self.fxLink = fxLink  # 当前数据的响应式页面
        self.warning = warning  # 天气预警数据列表
        self.refer = refer  # 数据来源和许可

    def to_json(self):
        return json.dumps(
            {
                "code": self.code,
                "updateTime": self.updateTime,
                "fxLink": self.fxLink,
                "warning": [w.__dict__ for w in self.warning],
                "refer": self.refer.__dict__,
            },
            ensure_ascii=False,
        )


class WeatherAPI:
    # 和风天气API错误码对应的错误消息
    ERROR_MESSAGES = {
        "400": "请求错误，请检查请求参数",
        "401": "认证失败，请检查API密钥",
        "402": "超过访问次数或余额不足，请充值",
        "403": "无访问权限，请联系客服",
        "404": "查询的数据或地区不存在",
        "429": "超过限定的QPM（每分钟访问次数）",
        "500": "无响应或超时，请稍后重试",
    }

    def __init__(self, api_key: str, api_host: str = "devapi.qweather.com"):
        """
        初始化天气API客户端
        :param api_key: 和风天气API密钥
        :param api_host: API主机地址，默认为devapi.qweather.com
        """
        assert api_key, "API key must be provided"
        assert api_host, "API host must be provided"

        self.api_key = api_key
        self.api_host = api_host
        self.base_url = f"https://{api_host}/v7/weather"
        self.warning_url = f"https://{api_host}/v7/warning"

    def _make_request(self, url: str, params: dict) -> dict:
        """
        发送HTTP请求并处理响应的通用方法
        :param url: 请求URL
        :param params: 请求参数
        :return: 解析后的JSON数据
        :raises: WeatherError系列异常
        """
        try:
            response = requests.get(url, params=params)

            # 检查HTTP状态码，只有200才继续执行
            if response.status_code != 200:
                raise WeatherNetworkError(
                    f"HTTP请求失败，状态码: {response.status_code}",
                    error_code=f"HTTP_{response.status_code}",
                    response_text=response.text[:200],
                )

            # 检查响应内容类型
            content_type = response.headers.get("content-type", "")
            if "application/json" not in content_type:
                raise WeatherParseError(
                    f"API返回非JSON格式数据，Content-Type: {content_type}",
                    error_code="INVALID_CONTENT_TYPE",
                    response_text=response.text[:200],
                )

            data = response.json()

            # 检查API返回的状态码
            api_code = data.get("code")
            if api_code != "200":
                error_msg = self.ERROR_MESSAGES.get(api_code, f"未知错误，状态码: {api_code}")
                raise WeatherAPIError(
                    f"和风天气API返回错误: {error_msg}",
                    error_code=api_code,
                    response_text=json.dumps(data, ensure_ascii=False),
                )

            return data

        except requests.exceptions.RequestException as e:
            # 网络请求异常
            raise WeatherNetworkError(f"请求和风天气API失败: {str(e)}", error_code="NETWORK_ERROR")
        except ValueError as e:
            # JSON解码异常
            raise WeatherParseError(
                f"解析API响应失败: {str(e)}",
                error_code="JSON_DECODE_ERROR",
                response_text=response.text[:200] if "response" in locals() else None,
            )
        except WeatherError:
            # 重新抛出自定义异常
            raise
        except Exception as e:
            # 其他未知异常
            raise WeatherError(f"获取天气数据时发生未知错误: {str(e)}", error_code="UNKNOWN_ERROR")

    def get_weather_now(self, lng: float, lat: float, lang: str = "zh", unit: str = "m") -> WeatherResult:
        """
        获取实时天气数据。
        :param lng: 经度
        :param lat: 纬度
        :param lang: 多语言设置，默认中文
        :param unit: 单位设置，m=公制，i=英制
        :return: WeatherResult 实体
        """
        params = {"location": f"{lng:.2f},{lat:.2f}", "key": self.api_key, "lang": lang, "unit": unit}
        url = f"{self.base_url}/now"

        # 使用通用请求方法获取数据
        data = self._make_request(url, params)

        # 解析响应数据
        now_data = data.get("now", {})
        refer_data = data.get("refer", {})
        now = WeatherNow(
            obsTime=now_data.get("obsTime"),
            temp=now_data.get("temp"),
            feelsLike=now_data.get("feelsLike"),
            icon=now_data.get("icon"),
            text=now_data.get("text"),
            wind360=now_data.get("wind360"),
            windDir=now_data.get("windDir"),
            windScale=now_data.get("windScale"),
            windSpeed=now_data.get("windSpeed"),
            humidity=now_data.get("humidity"),
            precip=now_data.get("precip"),
            pressure=now_data.get("pressure"),
            vis=now_data.get("vis"),
            cloud=now_data.get("cloud"),
            dew=now_data.get("dew"),
        )
        refer = WeatherRefer(sources=refer_data.get("sources"), license=refer_data.get("license"))
        return WeatherResult(
            code=data.get("code"), updateTime=data.get("updateTime"), fxLink=data.get("fxLink"), now=now, refer=refer
        )

    def get_weather_daily(
        self, lng: float, lat: float, days: str = "3d", lang: str = "zh", unit: str = "m"
    ) -> WeatherDailyResult:
        """
        获取每日天气预报数据。
        :param lng: 经度
        :param lat: 纬度
        :param days: 预报天数，支持：3d, 7d, 10d, 15d, 30d
        :param lang: 多语言设置，默认中文
        :param unit: 单位设置，m=公制，i=英制
        :return: WeatherDailyResult 实体
        """
        # 验证天数参数
        valid_days = ["3d", "7d", "10d", "15d", "30d"]
        if days not in valid_days:
            raise ValueError(f"days参数无效，支持的值：{', '.join(valid_days)}")

        params = {"location": f"{lng:.2f},{lat:.2f}", "key": self.api_key, "lang": lang, "unit": unit}
        url = f"{self.base_url}/{days}"

        # 使用通用请求方法获取数据
        data = self._make_request(url, params)

        # 解析每日天气数据
        daily_data_list = data.get("daily", [])
        daily_list = []
        for daily_data in daily_data_list:
            daily = WeatherDaily(
                fxDate=daily_data.get("fxDate"),
                sunrise=daily_data.get("sunrise"),
                sunset=daily_data.get("sunset"),
                moonrise=daily_data.get("moonrise"),
                moonset=daily_data.get("moonset"),
                moonPhase=daily_data.get("moonPhase"),
                moonPhaseIcon=daily_data.get("moonPhaseIcon"),
                tempMax=daily_data.get("tempMax"),
                tempMin=daily_data.get("tempMin"),
                iconDay=daily_data.get("iconDay"),
                textDay=daily_data.get("textDay"),
                iconNight=daily_data.get("iconNight"),
                textNight=daily_data.get("textNight"),
                wind360Day=daily_data.get("wind360Day"),
                windDirDay=daily_data.get("windDirDay"),
                windScaleDay=daily_data.get("windScaleDay"),
                windSpeedDay=daily_data.get("windSpeedDay"),
                wind360Night=daily_data.get("wind360Night"),
                windDirNight=daily_data.get("windDirNight"),
                windScaleNight=daily_data.get("windScaleNight"),
                windSpeedNight=daily_data.get("windSpeedNight"),
                humidity=daily_data.get("humidity"),
                precip=daily_data.get("precip"),
                pressure=daily_data.get("pressure"),
                vis=daily_data.get("vis"),
                cloud=daily_data.get("cloud"),
                uvIndex=daily_data.get("uvIndex"),
            )
            daily_list.append(daily)

        refer_data = data.get("refer", {})
        refer = WeatherRefer(sources=refer_data.get("sources"), license=refer_data.get("license"))

        return WeatherDailyResult(
            code=data.get("code"),
            updateTime=data.get("updateTime"),
            fxLink=data.get("fxLink"),
            daily=daily_list,
            refer=refer,
        )

    def get_weather_hourly(
        self, lng: float, lat: float, hours: str = "24h", lang: str = "zh", unit: str = "m"
    ) -> WeatherHourlyResult:
        """
        获取逐小时天气预报数据。
        :param lng: 经度
        :param lat: 纬度
        :param hours: 预报小时数，支持：24h, 72h, 168h
        :param lang: 多语言设置，默认中文
        :param unit: 单位设置，m=公制，i=英制
        :return: WeatherHourlyResult 实体
        """
        # 验证小时数参数
        valid_hours = ["24h", "72h", "168h"]
        if hours not in valid_hours:
            raise ValueError(f"hours参数无效，支持的值：{', '.join(valid_hours)}")

        params = {"location": f"{lng:.2f},{lat:.2f}", "key": self.api_key, "lang": lang, "unit": unit}
        url = f"{self.base_url}/{hours}"

        # 使用通用请求方法获取数据
        data = self._make_request(url, params)

        # 解析逐小时天气数据
        hourly_data_list = data.get("hourly", [])
        hourly_list = []
        for hourly_data in hourly_data_list:
            hourly = WeatherHourly(
                fxTime=hourly_data.get("fxTime"),
                temp=hourly_data.get("temp"),
                icon=hourly_data.get("icon"),
                text=hourly_data.get("text"),
                wind360=hourly_data.get("wind360"),
                windDir=hourly_data.get("windDir"),
                windScale=hourly_data.get("windScale"),
                windSpeed=hourly_data.get("windSpeed"),
                humidity=hourly_data.get("humidity"),
                pop=hourly_data.get("pop"),
                precip=hourly_data.get("precip"),
                pressure=hourly_data.get("pressure"),
                cloud=hourly_data.get("cloud"),
                dew=hourly_data.get("dew"),
            )
            hourly_list.append(hourly)

        refer_data = data.get("refer", {})
        refer = WeatherRefer(sources=refer_data.get("sources"), license=refer_data.get("license"))

        return WeatherHourlyResult(
            code=data.get("code"),
            updateTime=data.get("updateTime"),
            fxLink=data.get("fxLink"),
            hourly=hourly_list,
            refer=refer,
        )

    def get_weather_warning(self, lng: float, lat: float, lang: str = "zh") -> WeatherWarningResult:
        """
        获取天气灾害预警数据。
        :param lng: 经度
        :param lat: 纬度
        :param lang: 多语言设置，默认中文
        :return: WeatherWarningResult 实体
        """
        params = {"location": f"{lng:.2f},{lat:.2f}", "key": self.api_key, "lang": lang}
        url = f"{self.warning_url}/now"

        # 使用通用请求方法获取数据
        data = self._make_request(url, params)

        # 解析天气预警数据
        warning_data_list = data.get("warning", [])
        warning_list = []
        for warning_data in warning_data_list:
            warning = WeatherWarning(
                id=warning_data.get("id"),
                sender=warning_data.get("sender"),
                pubTime=warning_data.get("pubTime"),
                title=warning_data.get("title"),
                startTime=warning_data.get("startTime"),
                endTime=warning_data.get("endTime"),
                status=warning_data.get("status"),
                level=warning_data.get("level"),
                severity=warning_data.get("severity"),
                severityColor=warning_data.get("severityColor"),
                type=warning_data.get("type"),
                typeName=warning_data.get("typeName"),
                urgency=warning_data.get("urgency"),
                certainty=warning_data.get("certainty"),
                text=warning_data.get("text"),
                related=warning_data.get("related"),
            )
            warning_list.append(warning)

        refer_data = data.get("refer", {})
        refer = WeatherRefer(sources=refer_data.get("sources"), license=refer_data.get("license"))

        return WeatherWarningResult(
            code=data.get("code"),
            updateTime=data.get("updateTime"),
            fxLink=data.get("fxLink"),
            warning=warning_list,
            refer=refer,
        )
