import os

import pandas as pd
import pytest

from src.utils import load_transactions


@pytest.fixture
def sample_data(tmp_path):
    data = {
        'Дата операции': ['01.01.2023 12:00:00', '15.01.2023 18:30:00'],
        'Номер карты': ['1234567890123456', '9876543210987654'],
        'Сумма платежа': ['1000,50', '2000'],
        'Категория': ['Супермаркеты', 'Кафе'],
        'Статус': ['OK', 'OK']
    }
    df = pd.DataFrame(data)
    file_path = os.path.join(tmp_path, "test_operations.xlsx")
    df.to_excel(file_path, index=False)
    return file_path


def test_load_transactions(sample_data):
    df = load_transactions(sample_data)
    assert not df.empty
    assert len(df) == 2
