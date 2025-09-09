from enum import Enum
from typing import Literal


class Coin(str, Enum):
    """Cryptocurrency"""

    ton = "ton"
    usdt = "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs"


LiteralCoin = Literal[
    "ton",
    "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs"
]


class Asset(str, Enum):
    """Cryptocurrency"""

    ton = "TON"
    usdt = "USDT"


LiteralAsset = Literal[
    "TON",
    "USDT"
]
