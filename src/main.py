import json
import os

import pandas as pd

from src.reports import spending_by_category
from src.services import investment_bank
from src.utils import get_last_transaction_date, load_transactions
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
        print(home_data)

        # Инвесткопилка
        print("\n[2] Инвесткопилка:")
        last_date = get_last_transaction_date(df)
        saved_result = investment_bank(df.to_dict("records"), last_date)

        if isinstance(saved_result, str):
            try:
                saved_data = json.loads(saved_result)
                if isinstance(saved_data, dict):
                    if "saved" in saved_data:
                        print(f"Накоплено: {saved_data['saved']:.2f} RUB")
                    elif "error" in saved_data:
                        print(f"Ошибка: {saved_data['error']}")
                else:
                    print("Ошибка: данные в неверном формате")
            except json.JSONDecodeError:
                print("Ошибка: неверный формат данных от инвесткопилки")
        else:
            print("Ошибка: инвесткопилка вернула некорректный тип данных")

        # Отчет по категориям
        print("\n[3] Отчет по категориям:")
        category = "Супермаркеты"
        if category not in df["категория"].unique():
            print(f"Категория '{category}' не найдена")
        else:
            report = spending_by_category(df, category)
            if isinstance(report, str):
                try:
                    report_data = json.loads(report)
                    if "error" in report_data:
                        print(report_data["error"])
                    else:
                        print(f"Категория: {report_data['category']}")
                        print(f"Период: {report_data['period_start']} - {report_data['period_end']}")
                        print(f"Всего потрачено: {report_data['total_spent']:.2f} RUB")
                        print(f"Количество транзакций: {report_data['transaction_count']}")
                except json.JSONDecodeError:
                    print("Ошибка: неверный формат отчета")
            else:
                print("Ошибка: функция вернула неожиданный тип данных")

    except Exception as e:
        print(f"\nОшибка: {e}")


if __name__ == "__main__":
    main()
