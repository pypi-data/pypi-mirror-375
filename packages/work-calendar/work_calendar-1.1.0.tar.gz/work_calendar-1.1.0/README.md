[![license: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![PyPI](https://img.shields.io/pypi/v/work-calendar?label=pypi%20work-calendar)
![ruff](https://github.com/Polyrom/work-calendar/actions/workflows/linter.yml/badge.svg)
![tests](https://github.com/Polyrom/work-calendar/actions/workflows/tests.yml/badge.svg)

# Work Calendar

A simple no-nonsense library to find out whether a day is a working day in Russia.

Data obtained from [consultant.org](https://www.consultant.ru). I try to parse it as soon as the official calendar for the following year is published, which is normally late summer or early autumn.

Data available **for years 2015-2027**. Feel free to use the [raw json file](work_calendar/total.json).

## Installation

```bash
pip install work-calendar
```

## Usage

```python
from datetime import date

import work_calendar

new_years_holiday = date(2020, 1, 2)
weekend = date(2021, 4, 4)
workday = date(2020, 6, 3)
for day in [new_years_holiday, weekend, workday]:
    if work_calendar.is_workday(day):
        print(f"{day.strftime('%A %d.%m.%Y')} is a workday in Russia")
    else:
        print(f"{day.strftime('%A %d.%m.%Y')} is not a workday in Russia")

dt_out_of_bounds = dt = date(2090, 1, 2)
try:
    work_calendar.is_workday(dt_out_of_bounds)
except work_calendar.NoDataForYearError:
    print(f"No data found for date {dt_out_of_bounds} in work calendar!")
```

**Output**

```
Thursday 02.01.2020 is not a workday in Russia
Sunday 04.04.2021 is not a workday in Russia
Wednesday 03.06.2020 is a workday in Russia
No data found for date 2090-01-02 in work calendar!
```
