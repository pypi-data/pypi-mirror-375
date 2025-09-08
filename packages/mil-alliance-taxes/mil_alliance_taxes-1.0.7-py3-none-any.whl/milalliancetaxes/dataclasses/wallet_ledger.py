from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

@dataclass
class WalletLedger:
    id: int
    date: datetime
    amount: Decimal
    ref_type: str
    generated_by: int