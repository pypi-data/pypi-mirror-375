from typing import Optional
from pydantic import BaseModel


class MidgardPool(BaseModel):
    annualPercentageRate: float
    asset: str
    assetDepth: int
    assetPrice: float
    assetPriceUSD: float
    earnings: int
    earningsAnnualAsPercentOfDepth: float
    liquidityUnits: int
    lpLuvi: float
    nativeDecimal: int
    poolAPY: float
    runeDepth: int
    saversAPR: float
    saversDepth: int
    saversUnits: int
    saversYieldShare: Optional[float] = None
    status: str
    synthSupply: int
    synthUnits: int
    totalCollateral: int
    totalDebtTor: int
    units: int
    volume24h: int
