import json
import logging
import math
from datetime import datetime
from typing import Dict, List, Union

import pandas as pd

from src.utils import filter_by_period

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def investment_bank(transactions: Union[List[Dict], pd.DataFrame], month: datetime, limit: int = 50) -> str:
    try:
        if isinstance(transactions, pd.DataFrame):
            df = transactions
        else:
            df = pd.DataFrame(transactions)

        last_month_data = filter_by_period(df, month).copy()

        last_month_data["округление"] = (last_month_data["сумма_платежа"] / limit).apply(math.ceil) * limit

        total = (last_month_data["округление"] - last_month_data["сумма_платежа"]).sum()

        return json.dumps({"saved": round(float(total), 2)}, ensure_ascii=False)

    except Exception as e:
        logger.error("Ошибка в расчете инвесткопилки: %s", e)
        return json.dumps({"error": str(e)})
