import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

from src.utils import filter_by_period, get_last_transaction_date, load_transactions

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_greeting(time: datetime) -> str:
    hour = time.hour
    if 5 <= hour < 12:
        return "Доброе утро"  # Простая строка без f-префикса
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    return "Доброй ночи"


class FinanceAPI:
    def __init__(self) -> None:
        self.api_key = os.getenv("EXCHANGE_RATES_API_KEY")
        self.finnhub_key = os.getenv("FINNHUB_API_KEY")

    def get_currency_rates(self) -> List[Dict]:
        """Получение курсов валют"""
        if not self.api_key:
            return [{"currency": "USD", "rate": 75.0}]

        try:
            url = "https://api.apilayer.com/exchangerates_data/latest?base=RUB"
            response = requests.get(url, headers={"apikey": self.api_key}, timeout=5)
            response.raise_for_status()
            rates = response.json().get("rates", {})
            return [
                {"currency": "USD", "rate": round(1 / rates.get("USD", 75), 2)},
                {"currency": "EUR", "rate": round(1 / rates.get("EUR", 85), 2)},
            ]
        except Exception as e:
            logger.error(f"Currency API error: {e}")
            return [{"currency": "USD", "rate": 75.0}]

    def get_stock_prices(self) -> List[Dict]:
        """Получение котировок акций"""
        if not self.finnhub_key:
            return [{"stock": "AAPL", "price": 150.0}]

        try:
            url = f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={self.finnhub_key}"
            response = requests.get(url, timeout=5)
            data = response.json()
            return [{"stock": "AAPL", "price": round(data.get("c", 150), 2)}]
        except Exception as e:
            logger.error(f"Stocks API error: {e}")
            return [{"stock": "AAPL", "price": 150.0}]


def home_page(current_time: Optional[str] = None) -> str:
    """Генерация данных для главной страницы"""
    try:
        api = FinanceAPI()
        df = load_transactions("data/operations.xlsx")
        last_date = (
            datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S") if current_time else get_last_transaction_date(df)
        )

        last_month_data = filter_by_period(df, last_date)

        if last_month_data.empty:
            return json.dumps({"error": "No data available"})

        # Формирование данных карт
        cards_data = []
        for card, group in last_month_data.groupby("номер_карты"):
            total = group["сумма_платежа"].sum()
            cards_data.append(
                {
                    "last_digits": str(card)[-4:],
                    "total_spent": round(float(total), 2),
                    "cashback": round(float(abs(total)) / 100, 2),
                }
            )

        # Топ транзакции
        top_trans = last_month_data.nlargest(5, "сумма_платежа")[
            ["дата_операции", "сумма_платежа", "категория", "описание"]
        ]
        top_trans["дата_операции"] = top_trans["дата_операции"].dt.strftime("%d.%m.%Y")

        # Формирование результата
        result = {
            "greeting": get_greeting(last_date),
            "last_date": last_date.strftime("%d.%m.%Y %H:%M:%S"),
            "cards": cards_data,
            "top_transactions": top_trans.to_dict("records"),
            "currency_rates": api.get_currency_rates(),
            "stock_prices": api.get_stock_prices(),
        }

        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error in home_page: {e}")
        return json.dumps({"error": str(e)})
