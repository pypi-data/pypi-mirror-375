import statistics

from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Tuple
from period_tracker.data import load_entries


def get_starts(entries: Optional[List[Dict[str, str]]] = None) -> List[date]:
    """Return a list of period start dates."""
    if entries is None:
        entries = load_entries()
    return [datetime.strptime(entry["start"], "%Y-%m-%d").date() for entry in entries]


def avg_cyc(dates: List[date]) -> int:
    """Return average cycle length in days."""
    if len(dates) < 2:
        return 28
    return round(statistics.mean(cycle_lengths(dates)))


def avg_period(entries: Optional[List[Dict[str, str]]] = None) -> int:
    """Return average period duration."""
    if entries is None:
        entries = load_entries()
    return round(statistics.mean(period_lengths(entries))) if entries else 5


def cycle_lengths(dates: List[date]) -> List[int]:
    """Return list of cycle lengths in days."""
    dates = sorted(dates)
    return [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]


def period_lengths(entries: List[Dict[str, str]]) -> List[int]:
    """Return list of period durations in days."""
    return [
        (
            datetime.strptime(e["end"], "%Y-%m-%d")
            - datetime.strptime(e["start"], "%Y-%m-%d")
        ).days
        + 1
        for e in entries
    ]


def analyse(entries: Optional[List[Dict[str, str]]] = None) -> Dict:
    """Return cycle stats: avg, std dev, min, max."""
    if entries is None:
        entries = load_entries()
    dates = get_starts(entries)
    lengths = cycle_lengths(dates)
    if not lengths:
        return {
            "cycle_lengths": [],
            "avg": None,
            "std_dev": None,
            "min": None,
            "max": None,
        }

    return {
        "cycle_lengths": lengths,
        "avg": round(statistics.mean(lengths), 1),
        "std_dev": (round(statistics.stdev(lengths), 1) if len(lengths) > 2 else None),
        "min": min(lengths),
        "max": max(lengths),
    }


def predict(
    entries: Optional[List[Dict[str, str]]] = None, luteal_phase_len: int = 14
) -> Tuple[int, date, Tuple[date, date], date]:
    """Predict next period, ovulation, fertile window."""
    if entries is None:
        entries = load_entries()
    dates = get_starts(entries)
    dates = sorted(dates)

    if not dates:
        # No data, return reasonable defaults or raise an error
        raise ValueError("No period data available for prediction.")

    last = dates[-1]
    avg = avg_cyc(dates)
    next_period = last + timedelta(days=avg)
    ovulation = next_period - timedelta(days=luteal_phase_len)
    fertile = (
        ovulation - timedelta(days=2),
        ovulation + timedelta(days=2),
    )
    return avg, next_period, fertile, last


def forecast_windows(
    last: date, avg_len: int, luteal_phase_len: int = 14, count: int = 5
) -> List[Dict[str, date]]:
    """Forecast future fertile windows and periods."""
    future = []
    for i in range(1, count + 1):
        next_period = last + timedelta(days=avg_len * i)
        ovulation = next_period - timedelta(days=luteal_phase_len)
        fertile_start = ovulation - timedelta(days=2)
        fertile_end = ovulation + timedelta(days=2)
        future.append(
            {
                "cycle": i,
                "next_period": next_period,
                "fertile_start": fertile_start,
                "fertile_end": fertile_end,
                "ovulation_day": ovulation,
            }
        )
    return future
