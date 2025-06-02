import json
import logging
import os
from typing import Dict

import pandas as pd

from src.utils import filter_by_period, get_last_transaction_date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ensure_dir(path: str) -> None:
    """Создает директорию если не существует."""
    os.makedirs(path, exist_ok=True)


def spending_by_category(df: pd.DataFrame, category: str, months_back: int = 3) -> Dict:
    """Анализирует траты по категории."""
    try:
        last_date = get_last_transaction_date(df)
        period_data = filter_by_period(df, last_date, months_back)

        filtered = period_data[period_data["категория"].str.lower() == category.lower()]

        if filtered.empty:
            return {"error": f"Нет данных по категории '{category}'"}

        # Подготовка результата
        result = {
            "category": category,
            "period_start": (last_date - pd.DateOffset(months=months_back)).strftime("%d.%m.%Y"),
            "period_end": last_date.strftime("%d.%m.%Y"),
            "total_spent": round(float(filtered["сумма_платежа"].sum()), 2),
            "transaction_count": len(filtered),
            "average_spending": round(float(filtered["сумма_платежа"].mean()), 2),
        }

        # Сохранение отчета
        ensure_dir("reports")
        report_file = f"reports/report_{category.lower()}_{last_date.strftime('%Y%m')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return result
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return {"error": str(e)}
