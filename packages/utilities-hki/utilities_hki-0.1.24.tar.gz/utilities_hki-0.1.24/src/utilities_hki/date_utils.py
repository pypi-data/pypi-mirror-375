
from datetime import datetime, timedelta
import pytz
eastern = pytz.timezone('US/Eastern')
import pandas_market_calendars as mcal


def get_prev_market_day(dt, tz=None, nyse_holidays=None):
    """
    Get previous market day, accounting for weekends and market holidays.

    Parameters
    ----------
    dt : datetime.datetime
        Current datetime.
    tz : pytz.timezone, optional
        Timezone to use for the datetime. The hour in the output may 
        not match expectations unless a timezone is provided.
    nyse_holidays : tuple, optional
        NYSE market holidays.

    Returns
    -------
    datetime.datetime
        Previous market day datetime.
    """
    if tz is not None: dt = dt.replace(tzinfo=None)

    ydt = dt - timedelta(1)  # yesterday

    # check if previous day the weekend
    if ydt.weekday() == 5: ydt -= timedelta(1)
    elif ydt.weekday() == 6: ydt -= timedelta(2)

    # check for holiday
    if nyse_holidays is None:
        nyse_holidays = mcal.get_calendar('NYSE').holidays().holidays
    if ydt.date() in nyse_holidays: ydt -= timedelta(1)

    # check for weekend again
    if ydt.weekday() == 6: ydt -= timedelta(2)

    if tz is not None: ydt = tz.localize(ydt)
    
    return ydt


def get_prev_market_days(dt, n, ascending=True):
    """
    Get the previous n market days.

    Parameters
    ----------
    dt : datetime.datetime
        Date for which to get previous market days.
    n : int
        Number of previous market days to get.
    ascending : bool, optional
        Flag to sort dates in ascending (chronological) order. The default is True.

    Returns
    -------
    list of datetime.datetime
        List of previous market days.
    """
    nyse_holidays = mcal.get_calendar('NYSE').holidays().holidays

    prev_days = []
    while len(prev_days) < n:
        dt = get_prev_market_day(dt, nyse_holidays=nyse_holidays)
        prev_days.append(dt)
    
    if ascending: 
        return sorted(prev_days)
    else:
        return prev_days


def get_next_market_day(dt, tz=None, nyse_holidays=None):
    """
    Get next market day, accounting for weekends and market holidays.

    Parameters
    ----------
    dt : datetime.datetime
        Current datetime.
    tz : pytz.timezone, optional
        Timezone to use for the datetime. The hour in the output may 
        not match expectations unless a timezone is provided.
    nyse_holidays : tuple, optional
        NYSE market holidays.

    Returns
    -------
    datetime.datetime
        Next market day datetime.
    """
    if tz is not None: dt = dt.replace(tzinfo=None)

    next_dt = dt + timedelta(1)

    # check if next day the weekend
    if next_dt.weekday() == 5: next_dt += timedelta(2)
    elif next_dt.weekday() == 6: next_dt += timedelta(1)

    # check for holiday
    if nyse_holidays is None:
        nyse_holidays = mcal.get_calendar('NYSE').holidays().holidays
    if next_dt.date() in nyse_holidays: next_dt += timedelta(1)

    # check for weekend again
    if next_dt.weekday() == 5: next_dt += timedelta(2)

    if tz is not None: next_dt = tz.localize(next_dt)

    return next_dt


def is_not_market_day(dt, nyse_holidays=None):
    """
    Check if a given date is a market holiday or weekend.

    Parameters
    ----------
    dt : datetime.datetime
        Date to check.
    nyse_holidays : tuple
        NYSE market holidays.

    Returns
    -------
    bool
        True if date is not a market day, False otherwise.
    """
    
    # check for weekend
    if dt.weekday() in [5, 6]: return True
    
    # check for holiday
    if nyse_holidays is None: 
        nyse_holidays = mcal.get_calendar('NYSE').holidays().holidays
    if dt.date() in nyse_holidays: return True

    return False


def market_dates(start_date, end_date):
    """
    Get market dates between start and end dates.

    Parameters
    ----------
    start_date : datetime.datetime or str
        Start date. If str, must be in YYYY-MM-DD format.
    end_date : datetime.datetime or str
        End date. Not included in the output.
        If str, must be in YYYY-MM-DD format.

    Returns
    -------
    list of datetime.datetime
        List of market dates between start and end dates.
    """
    nyse_holidays = mcal.get_calendar('NYSE').holidays().holidays

    # if input dates are strings, convert to datetime
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")

    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    dates = []
    while start_date < end_date:
        if (not start_date.date() in nyse_holidays) and (start_date.weekday() < 5):
            dates.append(start_date)
        start_date += timedelta(days=1)

    return dates


# QUARTERLY DATES ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def get_quarter_start(dt):
    """
    Get start date of the current quarter.

    Parameters
    ----------
    dt : datetime.datetime
        Current datetime

    Returns
    -------
    datetime.datetime
        Datetime of last quarter end.
    """

    # get current month and year
    month = dt.month
    year = dt.year

    # calculate first day of current quarter
    quarter_start = datetime(year, ((month-1) // 3) * 3 + 1, 1).astimezone(eastern)
    return quarter_start


def get_last_quarter_end(dt):
    """
    Get date of last quarter end.

    Parameters
    ----------
    dt : datetime.datetime
        Current datetime

    Returns
    -------
    datetime.datetime
        Datetime of last quarter end.
    """

    # calculate first day of current quarter
    quarter_start = get_quarter_start(dt)

    # calculate last day of previous quarter
    last_quarter_end = eastern.normalize(quarter_start - timedelta(1))

    return last_quarter_end
