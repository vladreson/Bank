import logging
from datetime import datetime

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_transactions(file_path: str) -> pd.DataFrame:
    """Загружает транзакции из Excel файла."""
    try:
        df = pd.read_excel(file_path)

        # Преобразование и очистка данных
        df["дата_операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")

        # Обработка суммы платежа (для числовых и строковых значений)
        if "Сумма платежа" in df.columns:
            if df["Сумма платежа"].dtype == object:
                df["сумма_платежа"] = df["Сумма платежа"].str.replace(",", ".").astype(float)
            else:
                df["сумма_платежа"] = df["Сумма платежа"].astype(float)

        # Обработка номера карты (преобразуем в строку)
        if "Номер карты" in df.columns:
            df["номер_карты"] = df["Номер карты"].astype(str)

        # Остальные поля
        optional_fields = {"Категория": "категория", "Описание": "описание", "Статус": "статус"}

        for src, dest in optional_fields.items():
            if src in df.columns:
                df[dest] = df[src]

        # Выбираем только нужные колонки (те, которые существуют)
        available_columns = [
            col
            for col in ["дата_операции", "номер_карты", "сумма_платежа", "категория", "описание", "статус"]
            if col in df.columns
        ]

        return df[available_columns].dropna(subset=["дата_операции", "сумма_платежа"])

    except Exception as e:
        logger.error(f"Ошибка загрузки данных: {e}")
        return pd.DataFrame()


def get_last_transaction_date(df: pd.DataFrame) -> datetime:
    """Возвращает дату последней транзакции."""
    if df.empty:
        return datetime.now()
    max_date = df["дата_операции"].max()
    return max_date.to_pydatetime() if pd.notnull(max_date) else datetime.now()


def filter_by_period(df: pd.DataFrame, end_date: datetime, months_back: int = 1) -> pd.DataFrame:
    """
    Фильтрует транзакции за указанный период.
    """
    try:
        if df.empty:
            return pd.DataFrame()

        start_date = end_date - pd.DateOffset(months=months_back)
        mask = (df["дата_операции"] >= start_date) & (df["дата_операции"] <= end_date)
        return df.loc[mask].copy()
    except Exception as e:
        logger.error(f"Ошибка фильтрации по периоду: {e}")
        return pd.DataFrame()
