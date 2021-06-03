from dataclasses import dataclass
from typing import Optional


@dataclass
class StockExchangeDispatch:
    company_name: str
    content: str
    date: str
    sentiment: Optional[float] = None
