import datetime
import json
from functools import cache
from pathlib import Path


class NoDataForYearError(Exception):
    def __init__(self, year: int):
        self.year = year
        self.message = f"No data found for year {self.year}"
        super().__init__(self.message)


def is_workday(date_to_check: datetime.date) -> bool:
    """Determine if a given date is a workday in Russia.

    Args:
    ----
        date_to_check: The date to check.

    Returns:
    -------
        True if the given date is a day off, False otherwise.

    """
    return not __is_in_days_off(date_to_check)


def __is_in_days_off(day: datetime.date) -> bool:
    holidays_data = __load_holidays_data()
    date_ = datetime.date.strftime(day, "%Y-%m-%d")
    year_str = str(day.year)
    if year_str not in holidays_data:
        raise NoDataForYearError(day.year)
    return date_ in holidays_data[year_str]


@cache
def __load_holidays_data() -> dict[str, str]:
    data_path = Path(__file__).parent / "total.json"
    with data_path.open() as f:
        return json.loads(f.read())
