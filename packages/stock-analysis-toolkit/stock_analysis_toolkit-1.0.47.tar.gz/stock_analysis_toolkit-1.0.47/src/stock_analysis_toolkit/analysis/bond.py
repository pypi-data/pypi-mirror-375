"""
Bond analysis utilities for computing key fixed income metrics.

Assumptions:
- Fixed coupon bonds with specified frequency (e.g., 1, 2, 4, 12)
- Day count conventions supported: ACT/365, ACT/360, 30/360 (simplified) for accrual calc
- Prices provided as clean price (per 100 face value)

All yields are in percent (annualized). Internally, calculations use decimals.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, Optional, Tuple, List
import math


@dataclass
class BondInput:
    isin: str
    issuer: str
    coupon: float  # annual coupon in percent of face value (e.g., 7.5 for 7.5%)
    frequency: int  # payments per year (1,2,4,12)
    maturity_date: date
    clean_price: float  # per 100 face
    face_value: float = 100.0
    settlement_date: Optional[date] = None
    day_count: str = "ACT/365"
    rating: Optional[str] = None
    benchmark_yield: Optional[float] = None  # in percent
    quantity: float = 1.0  # number of units (face blocks)
    # Optional embedded options; dates as date objects; prices per 100 face
    call_schedule: Optional[List[Tuple[date, float]]] = None
    put_schedule: Optional[List[Tuple[date, float]]] = None


@dataclass
class BondMetrics:
    ytm: Optional[float]
    macaulay_duration: Optional[float]
    modified_duration: Optional[float]
    convexity: Optional[float]
    current_yield: Optional[float]
    accrued_interest: Optional[float]
    dirty_price: Optional[float]
    spread: Optional[float]
    ytc: Optional[float] = None
    ytw: Optional[float] = None
    market_value: Optional[float] = None  # dirty value of position


# -----------------------
# Date helpers
# -----------------------

def to_date(d: str | date) -> date:
    if isinstance(d, date):
        return d
    return datetime.strptime(d, "%Y-%m-%d").date()


def add_months(d: date, months: int) -> date:
    # naive month add suitable for schedule generation
    year = d.year + (d.month - 1 + months) // 12
    month = (d.month - 1 + months) % 12 + 1
    day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return date(year, month, day)


def previous_coupon_date(settle: date, maturity: date, freq: int) -> date:
    months = 12 // freq
    d = maturity
    while d > settle:
        d = add_months(d, -months)
    return d


def next_coupon_date(settle: date, maturity: date, freq: int) -> date:
    months = 12 // freq
    d = previous_coupon_date(settle, maturity, freq)
    nd = add_months(d, months)
    return nd


def days_between(d1: date, d2: date, basis: str) -> float:
    if basis.upper() == "ACT/365":
        return (d2 - d1).days
    if basis.upper() == "ACT/360":
        return (d2 - d1).days * (360.0 / 365.0)
    if basis.upper() == "30/360":
        # simplified 30/360 US
        d1_day = min(d1.day, 30)
        d2_day = min(d2.day, 30)
        return (d2.year - d1.year) * 360 + (d2.month - d1.month) * 30 + (d2_day - d1_day)
    return (d2 - d1).days


def year_fraction(d1: date, d2: date, basis: str) -> float:
    days = days_between(d1, d2, basis)
    if basis.upper() == "ACT/360":
        return days / 360.0
    return days / 365.0


# -----------------------
# Core calculations
# -----------------------

def cash_flow_schedule(b: BondInput) -> Tuple[list[date], list[float]]:
    freq = b.frequency
    months = 12 // freq
    pay_dates = []
    d = b.maturity_date
    while True:
        pay_dates.append(d)
        nd = add_months(d, -months)
        if nd <= (b.settlement_date or date.today()):
            break
        d = nd
    pay_dates = sorted(pay_dates)
    coupon_payment = b.face_value * (b.coupon / 100.0) / freq
    cashflows = [coupon_payment] * (len(pay_dates) - 1) + [coupon_payment + b.face_value]
    return pay_dates, cashflows


def cash_flow_schedule_to(b: BondInput, end_date: date, redemption_value: float) -> Tuple[List[date], List[float]]:
    """Build cash flow schedule truncated to end_date with a redemption at end_date.
    redemption_value is per 100 face (e.g., 100 at maturity, or call price).
    """
    freq = b.frequency
    months = 12 // freq
    pay_dates = []
    d = b.maturity_date
    while d > end_date:
        d = add_months(d, -months)
    # build forward from first coupon >= settlement up to end_date
    settle = b.settlement_date or date.today()
    dates = []
    cur = d
    while cur <= end_date:
        if cur >= settle:
            dates.append(cur)
        cur = add_months(cur, months)
    # ensure final redemption at end_date
    if not dates or dates[-1] != end_date:
        dates.append(end_date)
    coupon_payment = b.face_value * (b.coupon / 100.0) / freq
    cashflows: List[float] = []
    for i, pd in enumerate(dates):
        if pd == end_date:
            cashflows.append(coupon_payment + (redemption_value / 100.0) * b.face_value)
        else:
            cashflows.append(coupon_payment)
    return dates, cashflows


def accrued_interest(b: BondInput) -> float:
    settle = b.settlement_date or date.today()
    prev_cpn = previous_coupon_date(settle, b.maturity_date, b.frequency)
    nxt_cpn = next_coupon_date(settle, b.maturity_date, b.frequency)
    accrual = year_fraction(prev_cpn, settle, b.day_count)
    period = year_fraction(prev_cpn, nxt_cpn, b.day_count)
    coupon_payment = b.face_value * (b.coupon / 100.0) / b.frequency
    return coupon_payment * (accrual / max(period, 1e-9))


def price_from_ytm(b: BondInput, ytm_pct: float) -> float:
    settle = b.settlement_date or date.today()
    pay_dates, cashflows = cash_flow_schedule(b)
    y = ytm_pct / 100.0
    freq = b.frequency
    pv = 0.0
    for pd, cf in zip(pay_dates, cashflows):
        t = year_fraction(settle, pd, b.day_count)
        pv += cf / ((1 + y / freq) ** (freq * t))
    return pv


def price_from_yield_to(b: BondInput, yld_pct: float, end_date: date, redemption_value: float) -> float:
    settle = b.settlement_date or date.today()
    pay_dates, cashflows = cash_flow_schedule_to(b, end_date, redemption_value)
    y = yld_pct / 100.0
    freq = b.frequency
    pv = 0.0
    for pd, cf in zip(pay_dates, cashflows):
        t = year_fraction(settle, pd, b.day_count)
        pv += cf / ((1 + y / freq) ** (freq * t))
    return pv


def ytm_from_price(b: BondInput, target_price: float, guess_pct: float = 8.0) -> Optional[float]:
    # Newton-Raphson on yield
    y = guess_pct / 100.0
    freq = b.frequency
    settle = b.settlement_date or date.today()
    pay_dates, cashflows = cash_flow_schedule(b)
    for _ in range(50):
        pv = 0.0
        dv = 0.0
        for pd, cf in zip(pay_dates, cashflows):
            t = year_fraction(settle, pd, b.day_count)
            denom = (1 + y / freq) ** (freq * t)
            pv += cf / denom
            dv += -cf * (t / (1 + y / freq)) / denom
        f = pv - target_price
        if abs(f) < 1e-6:
            return y * 100.0
        if dv == 0:
            break
        y -= f / dv
        if y < -0.99:
            y = 0.0001
    return None


def yield_to_date_from_price(b: BondInput, target_price: float, end_date: date, redemption_value: float, guess_pct: float = 8.0) -> Optional[float]:
    """Solve for yield to a specific end_date with redemption_value per 100 face."""
    y = guess_pct / 100.0
    freq = b.frequency
    settle = b.settlement_date or date.today()
    pay_dates, cashflows = cash_flow_schedule_to(b, end_date, redemption_value)
    for _ in range(50):
        pv = 0.0
        dv = 0.0
        for pd, cf in zip(pay_dates, cashflows):
            t = year_fraction(settle, pd, b.day_count)
            denom = (1 + y / freq) ** (freq * t)
            pv += cf / denom
            dv += -cf * (t / (1 + y / freq)) / denom
        f = pv - target_price
        if abs(f) < 1e-6:
            return y * 100.0
        if dv == 0:
            break
        y -= f / dv
        if y < -0.99:
            y = 0.0001
    return None


def duration_convexity(b: BondInput, ytm_pct: float) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    y = ytm_pct / 100.0
    freq = b.frequency
    settle = b.settlement_date or date.today()
    pay_dates, cashflows = cash_flow_schedule(b)
    pv_total = 0.0
    macaulay = 0.0
    convexity = 0.0
    for pd, cf in zip(pay_dates, cashflows):
        t = year_fraction(settle, pd, b.day_count)
        disc = (1 + y / freq) ** (freq * t)
        pv = cf / disc
        pv_total += pv
        macaulay += t * pv
        convexity += t * (t + 1 / freq) * pv
    if pv_total <= 0:
        return None, None, None
    macaulay /= pv_total
    modified = macaulay / (1 + y / freq)
    convexity = convexity / pv_total / ((1 + y / freq) ** 2)
    return macaulay, modified, convexity


def compute_bond_metrics(b: BondInput, benchmark_yield_pct: Optional[float] = None) -> BondMetrics:
    ai = accrued_interest(b)
    dirty = b.clean_price + ai
    # YTM from clean->dirty because clean excludes accrued
    ytm = ytm_from_price(b, dirty)
    mac, mod, conv = (None, None, None)
    if ytm is not None:
        mac, mod, conv = duration_convexity(b, ytm)
    current_yield = (b.coupon / 100.0) * b.face_value / max(b.clean_price, 1e-9)
    spread = None
    bench = benchmark_yield_pct if benchmark_yield_pct is not None else b.benchmark_yield
    if ytm is not None and bench is not None:
        spread = ytm - bench
    # Yield-to-Call and Yield-to-Worst
    ytc: Optional[float] = None
    yields: List[float] = [ytm] if ytm is not None else []
    # Choose next upcoming call/put dates only (>= settlement)
    settle = b.settlement_date or date.today()
    if b.call_schedule:
        for cdate, cprice in b.call_schedule:
            if cdate >= settle:
                y_c = yield_to_date_from_price(b, dirty, cdate, cprice)
                if y_c is not None:
                    yields.append(y_c)
        # YTC typically refers to nearest call date
        next_calls = sorted([d for d, _ in b.call_schedule if d >= settle])
        if next_calls:
            first_date = next_calls[0]
            first_price = next(p for d, p in b.call_schedule if d == first_date)
            ytc = yield_to_date_from_price(b, dirty, first_date, first_price)
    if b.put_schedule:
        for pdate, pprice in b.put_schedule:
            if pdate >= settle:
                y_p = yield_to_date_from_price(b, dirty, pdate, pprice)
                if y_p is not None:
                    yields.append(y_p)
    ytw = min(yields) if yields else None

    mv = dirty / 100.0 * b.face_value * b.quantity

    return BondMetrics(
        ytm=ytm,
        macaulay_duration=mac,
        modified_duration=mod,
        convexity=conv,
        current_yield=current_yield * 100.0,
        accrued_interest=ai,
        dirty_price=dirty,
        spread=spread,
        ytc=ytc,
        ytw=ytw,
        market_value=mv,
    )
