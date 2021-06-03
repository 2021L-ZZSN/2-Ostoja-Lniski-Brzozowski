import datetime


def next_working_day(date: str):
    """
    :param date: date in 'YYYY-MM-DD' format
    :return: next day in 'YYYY-MM-DD' format
    """
    return change_working_day(date, 1)


def previous_working_day(date: str):
    """
    :param date: date in 'YYYY-MM-DD' format
    :return: previous day in 'YYYY-MM-DD' format
    """
    return change_working_day(date, -1)


def change_working_day(date: str, day_delta: int):
    """
    :param day_delta: positive values increases day, negative subtracts.
    :param date: date in 'YYYY-MM-DD' format
    :return: previous day in 'YYYY-MM-DD' format
    """
    excluded = (6, 7)
    day_delta = 1 if day_delta >= 0 else -1
    date_as_datetime = _date_str_to_datetime(date)
    date_as_datetime += datetime.timedelta(days=day_delta)
    while date_as_datetime.isoweekday() in excluded:
        date_as_datetime += datetime.timedelta(days=day_delta)
    return _date_datetime_to_str(date_as_datetime)


def _date_str_to_datetime(date: str) -> datetime.date:
    """
    :param date: date in 'YYYY-MM-DD' format
    """
    values = date.split('-')
    return datetime.date(year=int(values[0]), month=int(values[1]), day=int(values[2]))


def _date_datetime_to_str(date: datetime.date) -> str:
    return f'{date.year}-{date.month}-{date.day}'
