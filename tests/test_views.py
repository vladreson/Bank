import json
from datetime import datetime
from typing import Generator
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from pandas import DataFrame

from src.views import get_greeting, home_page


@pytest.fixture
def sample_transactions() -> Generator[DataFrame, None, None]:
    yield pd.DataFrame(
        {
            "дата_операции": [datetime(2023, 1, 1, 12)],
            "номер_карты": ["1234567890123456"],
            "сумма_платежа": [1000.50],
            "категория": ["Супермаркеты"],
            "описание": ["Покупка в магазине"],
            "статус": ["OK"],
        }
    )


@pytest.mark.parametrize(
    "hour,expected", [(8, "Доброе утро"), (13, "Добрый день"), (20, "Добрый вечер"), (2, "Доброй ночи")]
)
def test_get_greeting_with_params(hour: int, expected: str) -> None:
    """Тестируем функцию приветствия с разными часами"""
    test_time = datetime(2023, 1, 1, hour)
    assert get_greeting(test_time) == expected


@patch("src.views.load_transactions")
@patch("src.views.get_last_transaction_date")
@patch("src.views.FinanceAPI")
def test_home_page_with_mocks(
    mock_finance_api: MagicMock, mock_get_date: MagicMock, mock_load: MagicMock, sample_transactions: DataFrame
) -> None:
    """Тестируем home_page с моками зависимостей"""
    mock_load.return_value = sample_transactions
    mock_get_date.return_value = datetime(2023, 1, 1, 12)

    mock_api_instance = MagicMock()
    mock_api_instance.get_currency_rates.return_value = [{"currency": "USD", "rate": 75.0}]
    mock_api_instance.get_stock_prices.return_value = [{"stock": "AAPL", "price": 150.0}]
    mock_finance_api.return_value = mock_api_instance

    result = json.loads(home_page())

    assert result["greeting"] == "Добрый день"
    assert len(result["cards"]) == 1
    assert result["cards"][0]["last_digits"] == "3456"
    assert result["currency_rates"][0]["currency"] == "USD"
    assert result["stock_prices"][0]["stock"] == "AAPL"

    mock_load.assert_called_once_with("data/operations.xlsx")
    mock_api_instance.get_currency_rates.assert_called_once()
    mock_api_instance.get_stock_prices.assert_called_once()


def test_home_page_error_handling() -> None:
    """Тестируем обработку ошибок в home_page"""
    with patch("src.views.load_transactions", side_effect=Exception("Test error")):
        result = json.loads(home_page())
        assert "error" in result
        assert "Test error" in result["error"]
