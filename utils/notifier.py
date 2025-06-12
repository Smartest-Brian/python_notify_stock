from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    TextMessage,
    ImageMessage,
)

from config import Config
from utils.chart_generator import ChartGenerator
from utils.time_helper import TimeHelper


class Notifier:
    """負責發送 LINE Messaging API 通知"""

    def __init__(self, config, class_time_helper, class_chart_generator):
        self.config = config
        self.channel_token = config.LINE_CHANNEL_ACCESS_TOKEN
        self.user_id = config.LINE_USER_ID
        self.time_helper = class_time_helper
        self.chart_generator = class_chart_generator

    def _push_messages(self, messages):
        configuration = Configuration(access_token=self.channel_token)
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            request = PushMessageRequest(to=self.user_id, messages=messages)
            messaging_api.push_message_with_http_info(request)

    def line_notify_message_text(self, msg):
        """發送純文字通知 (保持舊介面名稱相容)"""
        self._push_messages([TextMessage(text=msg)])

    def send(self, ticker, strategy_results, price_data):
        """發送通知，包括文字與圖表"""
        notify_message = self.format_message(ticker, strategy_results)
        self.chart_generator.generate_chart(ticker, price_data)

        messages = [TextMessage(text=notify_message)]
        if self.chart_generator.is_chart_generated():
            image_url = self.chart_generator.chart_fig
            messages.append(
                ImageMessage(
                    original_content_url=image_url,
                    preview_image_url=image_url,
                )
            )
        else:
            print("Warning: Chart not found, skipping image attachment.")

        self._push_messages(messages)
        self.chart_generator.remove_chart()

    def format_message(self, ticker, strategy_results):
        """格式化通知訊息"""
        now = self.time_helper.get_timezone(self.config.TIMEZONE_OFFSET)
        strategy_text = "\n".join(strategy_results)
        return f"{now}\n{ticker}：{strategy_text}"


if __name__ == "__main__":
    config = Config()
    time_helper = TimeHelper()
    chart_generator = ChartGenerator()
    notifier = Notifier(config, time_helper, chart_generator)

    notifier.line_notify_message_text("test")
