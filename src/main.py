import json
import os

import pandas as pd

from src.reports import spending_by_category
from src.services import investment_bank
from src.utils import load_transactions
from src.views import home_page


def print_sample(df: pd.DataFrame, n: int = 3) -> None:
    """Печатает пример данных."""
    sample = df[["дата_операции", "категория", "сумма_платежа"]].head(n)
    print("\nПример транзакций:")
    print(sample.to_string(index=False))
    print(f"\nДиапазон дат: {df['дата_операции'].min()} - {df['дата_операции'].max()}")


def main() -> None:
    try:
        # Загрузка данных
        data_path = "data/operations.xlsx"
        if not os.path.exists(data_path):
            print(f"Файл {data_path} не найден!")
            return

        print("Загрузка данных...")
        df = load_transactions(data_path)

        if df.empty:
            print("Нет данных для анализа")
            return

        print(f"\nУспешно загружено {len(df)} транзакций")
        print_sample(df)

        # Главная страница
        print("\n[1] Главная страница:")
        home_data = home_page()
        print(json.dumps(home_data, indent=2, ensure_ascii=False))

        # Инвесткопилка
        print("\n[2] Инвесткопилка:")
        saved = investment_bank(df)
        print(f"Накоплено: {saved:.2f} RUB")

        # Отчет по категориям
        print("\n[3] Отчет по категориям:")
        category = "Супермаркеты"
        if category not in df["категория"].unique():
            print(f"Категория '{category}' не найдена")
        else:
            report = spending_by_category(df, category)
            if "error" in report:
                print(report["error"])
            else:
                print(f"Категория: {report['category']}")
                print(f"Период: {report['period_start']} - {report['period_end']}")
                print(f"Всего потрачено: {report['total_spent']:.2f} RUB")
                print(f"Количество транзакций: {report['transaction_count']}")

    except Exception as e:
        print(f"\nОшибка: {e}")


if __name__ == "__main__":
    main()
