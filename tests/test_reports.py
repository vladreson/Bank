import json
import os
from typing import Generator

import pandas as pd
import pytest
from pandas import DataFrame

from src.reports import spending_by_category


@pytest.fixture
def sample_data() -> Generator[DataFrame, None, None]:
    # Pytest fixtures, которые возвращают генераторы, лучше типизировать так
    yield pd.DataFrame(
        {
            "дата_операции": pd.to_datetime(["2023-01-15"]),
            "сумма_платежа": [1000],
            "категория": ["Супермаркеты"],
            "статус": ["OK"],
        }
    )


def test_spending_by_category(sample_data: DataFrame, tmp_path: str) -> None:
    os.chdir(tmp_path)
    result_json = spending_by_category(sample_data, "Супермаркеты")
    assert isinstance(result_json, str)  # для mypy и безопасности
    result = json.loads(result_json)
    # Декодируем JSON
    assert result["total_spent"] == 1000
