from datetime import datetime

import pandas as pd

from src.views import get_greeting, home_page


def test_get_greeting():
    """Тест функции приветствия"""
    assert get_greeting(datetime(2023, 1, 1, 8, 0)) == "Доброе утро"
    assert get_greeting(datetime(2023, 1, 1, 13, 0)) == "Добрый день"
    assert get_greeting(datetime(2023, 1, 1, 20, 0)) == "Добрый вечер"
    assert get_greeting(datetime(2023, 1, 1, 2, 0)) == "Доброй ночи"


def test_home_page(monkeypatch):
    """Тест главной страницы с полными тестовыми данными"""
    test_data = pd.DataFrame({
        'дата_операции': [datetime.now()],
        'номер_карты': ['3456'],
        'сумма_платежа': [1000.50],
        'категория': ['Супермаркеты'],
        'описание': ['Покупка в магазине'],
        'статус': ['OK']
    })

    # Мокируем функцию загрузки данных
    monkeypatch.setattr('src.views.load_transactions', lambda _: test_data)

    result = home_page()

    # Проверяем структуру ответа
    assert 'greeting' in result
    assert 'cards' in result
    assert 'top_transactions' in result

    # Проверяем данные карты (теперь ожидаем последние 4 цифры)
    assert len(result['cards']) == 1
    assert result['cards'][0]['last_digits'] == '3456'  # Последние 4 цифры
    assert result['cards'][0]['total_spent'] == 1000.50

    # Проверяем топ транзакции
    assert len(result['top_transactions']) == 1
    assert result['top_transactions'][0]['сумма_платежа'] == 1000.50
