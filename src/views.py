import logging
from datetime import datetime
from typing import Dict

from src.utils import filter_by_period, get_last_transaction_date, load_transactions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_greeting(time: datetime) -> str:
    hour = time.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    return "Доброй ночи"


def home_page() -> Dict:
    """Генерирует данные для главной страницы."""
    try:
        df = load_transactions("data/operations.xlsx")
        last_date = get_last_transaction_date(df)
        last_month_data = filter_by_period(df, last_date)

        if last_month_data.empty:
            return {"error": f"Нет данных за {last_date.strftime('%B %Y')}"}

        # Анализ данных
        cards_data = []
        for card, group in last_month_data.groupby("номер_карты"):
            total = group["сумма_платежа"].sum()
            cards_data.append(
                {
                    "last_digits": card,
                    "total_spent": round(float(total), 2),
                    "cashback": round(float(abs(total)) / 100, 2),
                }
            )

        top_trans = last_month_data.nlargest(5, "сумма_платежа")[
            ["дата_операции", "сумма_платежа", "категория", "описание"]
        ]
        top_trans["дата_операции"] = top_trans["дата_операции"].dt.strftime("%d.%m.%Y")

        return {
            "greeting": get_greeting(last_date),
            "last_date": last_date.strftime("%d.%m.%Y %H:%M:%S"),
            "cards": cards_data,
            "top_transactions": top_trans.to_dict("records"),
            "currency_rates": [{"currency": "USD", "rate": 75.0}],  # Заглушка
            "stock_prices": [{"stock": "AAPL", "price": 150.0}],  # Заглушка
        }
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return {"error": str(e)}
