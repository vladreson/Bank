import logging
import os
from datetime import datetime
from typing import cast

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_transactions(file_path: str) -> pd.DataFrame:
    """Загружает и предобрабатывает транзакции из Excel файла."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не найден")

        df = pd.read_excel(file_path, dtype={"Дата операции": str, "Номер карты": str, "Сумма платежа": str})

        # Стандартизация колонок
        df.columns = df.columns.str.lower().str.replace(" ", "_")

        # Проверка обязательных колонок
        required_cols = {"дата_операции", "номер_карты", "сумма_платежа", "категория"}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Отсутствуют колонки: {missing}")

        # Преобразование дат
        df["дата_операции"] = pd.to_datetime(df["дата_операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")

        # Обработка числовых значений
        df["сумма_платежа"] = pd.to_numeric(df["сумма_платежа"].str.replace(",", "."), errors="coerce")

        # Фильтрация валидных данных
        df = df[df["статус"].str.upper() == "OK"] if "статус" in df.columns else df
        df = df.dropna(subset=["дата_операции", "сумма_платежа"])
        df["номер_карты"] = df["номер_карты"].str[-4:]

        return df

    except Exception as e:
        logger.error(f"Ошибка загрузки: {e}")
        raise


def get_last_transaction_date(df: pd.DataFrame) -> datetime:
    """Возвращает последнюю дату транзакции с явным приведением типа."""
    last_date = df['дата_операции'].max()
    # Явное приведение типа для mypy
    return cast(datetime, last_date.to_pydatetime())


def filter_by_period(df: pd.DataFrame, end_date: datetime, months: int = 1) -> pd.DataFrame:
    """Фильтрует транзакции за указанный период."""
    start_date = end_date - pd.DateOffset(months=months)
    return df[(df["дата_операции"] >= start_date) & (df["дата_операции"] <= end_date)]
