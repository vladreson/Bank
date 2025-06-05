import json
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.services import investment_bank


@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    return [
        {"дата_операции": datetime(2023, 1, 1), "сумма_платежа": 1712, "статус": "OK"},
        {"дата_операции": datetime(2023, 1, 2), "сумма_платежа": 1234, "статус": "OK"},
    ]


@pytest.mark.parametrize(
    "amount,limit,expected",
    [
        (1712, 50, 38),
        (1234, 100, 66),
        (999, 10, 1),
    ],
)
def test_investment_bank_with_params(amount: int, limit: int, expected: int) -> None:
    data = [{"дата_операции": datetime(2023, 1, 1), "сумма_платежа": amount, "статус": "OK"}]
    result = json.loads(investment_bank(data, datetime(2023, 1, 1), limit))
    assert result["saved"] == expected


@patch("src.services.filter_by_period")
def test_investment_bank_with_mock(mock_filter: MagicMock, sample_transactions: List[Dict[str, Any]]) -> None:
    """Тестирование функции инвесткопилки с моками."""
    mock_df = MagicMock()
    mock_df.empty = False
    mock_df.__getitem__.return_value = pd.Series([1712, 1234])
    mock_filter.return_value = mock_df

    result = json.loads(investment_bank(sample_transactions, datetime(2023, 1, 1)))
    assert "saved" in result
