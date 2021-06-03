from dataclasses import dataclass
from typing import Optional


@dataclass
class StockExchangeDispatch:
    company_name: str
    text_content: str
    date: str
    sentiment: Optional[float] = None
