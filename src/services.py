import math

import pandas as pd

from src.utils import filter_by_period, get_last_transaction_date


def investment_bank(df: pd.DataFrame, limit: int = 50) -> float:
    """Рассчитывает сумму для инвесткопилки через округление транзакций."""
    try:
        last_date = get_last_transaction_date(df)
        last_month_data = filter_by_period(df, last_date).copy()  # Создаем явную копию

        if last_month_data.empty:
            return 0.0

        # Используем .loc для избежания предупреждения
        last_month_data.loc[:, "округление"] = (last_month_data["сумма_платежа"] / limit).apply(math.ceil) * limit

        total = (last_month_data["округление"] - last_month_data["сумма_платежа"]).sum()
        return round(float(total), 2)

    except Exception as e:
        print(f"Ошибка в расчете инвесткопилки: {e}")
        return 0.0
