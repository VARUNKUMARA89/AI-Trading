"""Indian equity transaction charges (NSE cash segment).

Defaults follow a typical discount-broker schedule. Rates change with budgets
and exchange circulars, so every number lives in config.toml [charges] and can
be updated without touching code.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

DEFAULTS = {
    "brokerage_intraday_pct": 0.03,   # % of turnover per order...
    "brokerage_intraday_cap": 20.0,   # ...capped at Rs 20 per executed order
    "brokerage_delivery_pct": 0.0,
    "brokerage_delivery_cap": 0.0,
    "stt_intraday_sell_pct": 0.025,   # on sell side only
    "stt_delivery_pct": 0.1,          # on buy and sell
    "exchange_txn_pct": 0.00297,      # NSE
    "sebi_per_crore": 10.0,
    "stamp_intraday_buy_pct": 0.003,  # buy side only
    "stamp_delivery_buy_pct": 0.015,
    "gst_pct": 18.0,                  # on brokerage + exchange + SEBI
    "dp_charge_per_sell": 15.93,      # delivery sells, per scrip per day (incl. GST)
}


@dataclass
class ChargeBreakdown:
    brokerage: float = 0.0
    stt: float = 0.0
    exchange: float = 0.0
    sebi: float = 0.0
    stamp: float = 0.0
    gst: float = 0.0
    dp: float = 0.0

    @property
    def total(self) -> float:
        return round(self.brokerage + self.stt + self.exchange + self.sebi + self.stamp + self.gst + self.dp, 2)

    def as_dict(self) -> dict:
        d = {k: round(v, 2) for k, v in asdict(self).items()}
        d["total"] = self.total
        return d


def compute(side: str, qty: int, price: float, product: str, rates: dict | None = None) -> ChargeBreakdown:
    r = {**DEFAULTS, **(rates or {})}
    turnover = qty * price
    side = side.upper()
    intraday = product == "intraday"
    c = ChargeBreakdown()
    if intraday:
        c.brokerage = min(turnover * r["brokerage_intraday_pct"] / 100, r["brokerage_intraday_cap"])
        if side == "SELL":
            c.stt = turnover * r["stt_intraday_sell_pct"] / 100
        if side == "BUY":
            c.stamp = turnover * r["stamp_intraday_buy_pct"] / 100
    else:
        cap = r["brokerage_delivery_cap"]
        b = turnover * r["brokerage_delivery_pct"] / 100
        c.brokerage = min(b, cap) if cap > 0 else b
        c.stt = turnover * r["stt_delivery_pct"] / 100
        if side == "BUY":
            c.stamp = turnover * r["stamp_delivery_buy_pct"] / 100
        else:
            c.dp = r["dp_charge_per_sell"]
    c.exchange = turnover * r["exchange_txn_pct"] / 100
    c.sebi = turnover * r["sebi_per_crore"] / 1e7
    c.gst = (c.brokerage + c.exchange + c.sebi) * r["gst_pct"] / 100
    return c
