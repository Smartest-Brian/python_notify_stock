import re
from datetime import datetime, timedelta

import pandas as pd
import requests


class DataLoader:
    def __init__(self, class_config, class_notifier):
        self.config = class_config
        self.notifier = class_notifier

    def get_etf_ticker_list(self):
        """ 取得 ETF 的股票清單 """
        url = f"https://www.zacks.com/funds/etf/{self.config.ETF_SYMBOL}/holding"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
        }

        try:
            with requests.Session() as req:
                req.headers.update(headers)
                r = req.get(url)
                ticker_list = re.findall(r'etf\\\/(.*?)\\', r.text)

            return ticker_list

        except requests.exceptions.RequestException as e:
            self.notifier.line_notify_message_text(f"❌ 取得 ETF 股票清單失敗: {e}")
            return []  # 返回空列表以防止主程式崩潰

    def get_stock_data(self, ticker):
        """取得指定股票的數據 (Alpha Vantage)"""
        api_key = self.config.ALPHAVANTAGE_API_KEY
        url = (
            f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={api_key}"
        )

        try:
            response = requests.get(url)
            data = response.json()
            time_series = data.get("Time Series (Daily)", {})

            if not time_series:
                self.notifier.line_notify_message_text(
                    f"⚠️ 無法獲取 {ticker} 的歷史數據"
                )
                return None

            df = pd.DataFrame.from_dict(time_series, orient="index")
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)
            df.rename(
                columns={
                    "1. open": "Open",
                    "2. high": "High",
                    "3. low": "Low",
                    "4. close": "Close",
                    "5. volume": "Volume",
                },
                inplace=True,
            )
            df = df[["Open", "High", "Low", "Close", "Volume"]].astype(float)

            try:
                days = int(self.config.PERIOD_LENGTH.rstrip("d"))
                df = df.tail(days)
            except Exception:
                pass

            return df

        except Exception as e:
            self.notifier.line_notify_message_text(
                f"❌ 無法取得 {ticker} 的股票數據: {e}"
            )
            return None
