"""
和风天气API自定义异常模块
包含所有天气API相关的异常类定义
"""


class WeatherError(Exception):
    """和风天气API异常基类"""

    def __init__(self, message: str, error_code: str = None, response_text: str = None):
        """
        初始化天气异常
        :param message: 错误消息
        :param error_code: 错误代码
        :param response_text: 响应文本（用于调试）
        """
        super().__init__(message)
        self.error_code = error_code
        self.response_text = response_text
        self.message = message

    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class WeatherNetworkError(WeatherError):
    """网络相关异常"""

    pass


class WeatherAPIError(WeatherError):
    """API业务逻辑异常"""

    pass


class WeatherParseError(WeatherError):
    """数据解析异常"""

    pass
