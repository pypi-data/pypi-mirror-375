"""
Unit tests for date utilities
"""

import unittest
from datetime import datetime, timedelta
from pytz import timezone

import os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(root, 'src', 'utilities_hki'))

from date_utils import get_next_market_day
from date_utils import get_prev_market_day


eastern = timezone('US/Eastern')


def day_generator(year, month, weekday):
    """
    Generate all dates in a month that fall on a given weekday.
    """
    if isinstance(weekday, str):
        weekday = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'].index(weekday.lower())

    d = datetime(year, month, 1)
    while d.weekday() != weekday:
        d += timedelta(days=1)
    while d.month == month:
        yield d
        d += timedelta(days=7)


class TestDateUtils(unittest.TestCase):
    """
    Test date utilities.
    """

    def test_get_next_market_day(self):
        """
        Test date_utils.get_next_market_day().
        """
        
        pairs = [
            ("2021-01-01", "2021-01-04"), # market holiday
            ("2025-01-06", "2025-01-07"), # market day
            ("2024-02-29", "2024-03-01"), # leap year
            ("2025-02-28", "2025-03-03"), # non-leap year, but Friday
            ("2024-11-01", "2024-11-04"), # DST transition
            ("2024-12-21", "2024-12-23"), # weekend
            ]
        with self.subTest('date only, no timezone'):
            for date, next_date in pairs:
                dt = datetime.strptime(date, "%Y-%m-%d")
                next_dt = datetime.strptime(next_date, "%Y-%m-%d")
                msg = f"date: {date}, next_date: {next_date}"
                self.assertEqual(get_next_market_day(dt).date(), next_dt.date(), msg)
                # without explicitly dropping the time
                self.assertEqual(get_next_market_day(dt), next_dt, msg)

        with self.subTest('entire datetime with timezone, midnight'):
            for date, next_date in pairs:
                dt = eastern.localize(datetime.strptime(date, "%Y-%m-%d"))
                next_dt = eastern.localize(datetime.strptime(next_date, "%Y-%m-%d"))
                msg = f"date: {date}, next_date: {next_date}"
                # timezone must be provided to ensure timing is correct on DST transition
                self.assertEqual(get_next_market_day(dt, eastern), next_dt, msg)

        # set the pairs to 08:00:00
        utc = timezone('UTC')
        with self.subTest('entire datetime with UTC timezone, 08:00'):
            for date, next_date in pairs:
                dt = utc.localize(datetime.strptime(date + " 08:00", "%Y-%m-%d %H:%M"))
                next_dt = utc.localize(datetime.strptime(next_date + " 08:00", "%Y-%m-%d %H:%M"))
                msg = f"date: {date}, next_date: {next_date}"
                self.assertEqual(get_next_market_day(dt), next_dt, msg)

        with self.subTest('additional dates, no timezone'):
            # wednesdays in March 2025
            for dt in day_generator(2025, 3, 'wed'):
                self.assertEqual(get_next_market_day(dt), dt + timedelta(1))

            # sundays in April 2025
            for dt in day_generator(2025, 4, 'sun'):
                self.assertEqual(get_next_market_day(dt), dt + timedelta(1))

            # saturdays in June 2025
            for dt in day_generator(2025, 6, 'sat'):
                self.assertEqual(get_next_market_day(dt), dt + timedelta(2))


    def test_get_prev_market_day(self):
        """
        Test date_utils.get_prev_market_day().
        """
        
        pairs = [
            ("2021-01-04", "2020-12-31"), # market holiday on previous Friday
            ("2025-01-07", "2025-01-06"), # market day
            ("2024-03-01", "2024-02-29"), # leap year
            ("2025-03-03", "2025-02-28"), # non-leap year, but Monday
            ("2024-11-04", "2024-11-01"), # DST transition
            ("2024-12-22", "2024-12-20"), # weekend
            ]
        with self.subTest('date only, no timezone'):
            for date, prev_date in pairs:
                dt = datetime.strptime(date, "%Y-%m-%d")
                prev_dt = datetime.strptime(prev_date, "%Y-%m-%d")
                msg = f"date: {date}, prev_date: {prev_date}"
                self.assertEqual(get_prev_market_day(dt).date(), prev_dt.date(), msg)
                # without explicitly dropping the time
                self.assertEqual(get_prev_market_day(dt), prev_dt, msg)
                
        with self.subTest('entire datetime with timezone, midnight'):
            for date, prev_date in pairs:
                dt = eastern.localize(datetime.strptime(date, "%Y-%m-%d"))
                prev_dt = eastern.localize(datetime.strptime(prev_date, "%Y-%m-%d"))
                # timezone must be provided to ensure timing is correct on DST transition
                self.assertEqual(get_prev_market_day(dt, eastern), prev_dt, msg)

        # set the pairs to 08:00:00
        utc = timezone('UTC')
        with self.subTest('entire datetime with UTC timezone, 08:00'):
            for date, prev_date in pairs:
                dt = utc.localize(datetime.strptime(date + " 08:00", "%Y-%m-%d %H:%M"))
                prev_dt = utc.localize(datetime.strptime(prev_date + " 08:00", "%Y-%m-%d %H:%M"))
                msg = f"date: {date}, prev_date: {prev_date}"
                self.assertEqual(get_prev_market_day(dt), prev_dt, msg)
        
        with self.subTest('additional dates, no timezone'):
            # wednesdays in March 2025
            for dt in day_generator(2025, 3, 'wed'):
                self.assertEqual(get_prev_market_day(dt), dt - timedelta(1))

            # saturdays in June 2025
            for dt in day_generator(2025, 6, 'sat'):
                self.assertEqual(get_prev_market_day(dt), dt - timedelta(1))

            # sundays in August 2025
            for dt in day_generator(2025, 8, 'sun'):
                self.assertEqual(get_prev_market_day(dt), dt - timedelta(2))


if __name__ == '__main__':
    unittest.main()
