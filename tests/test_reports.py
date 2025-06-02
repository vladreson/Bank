import os

import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'дата_операции': pd.to_datetime(['2023-01-15']),
        'сумма_платежа': [1000],
        'категория': ['Супермаркеты'],
        'статус': ['OK']
    })


def test_spending_by_category(sample_data, tmp_path):
    os.chdir(tmp_path)
    result = spending_by_category(sample_data, 'Супермаркеты')
    assert result['total_spent'] == 1000
