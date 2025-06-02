import pandas as pd
import pytest

from src.services import investment_bank


@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'дата_операции': pd.to_datetime(['2023-01-01']),
        'сумма_платежа': [1712],
        'статус': ['OK']
    })


def test_investment_bank(sample_data):
    assert investment_bank(sample_data, 50) == 38
