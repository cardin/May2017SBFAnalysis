from typing import ClassVar, Dict, Optional


class ParsedDate(object):
    """
    Represents a parsed date literal.

    Class Attributes:
        _current_month (int): No. of months since 0 AD to May 2017
        _monthToNum (Dict): string2num for month

    Attributes:
        date (Optional[int]): Day 1 - 30
        month (Optional[int]): Month 1 - 12
        year (Optional[int]): Year AD
        quarter (Optional[int]): 1 - 4
        months_since (Optional[int]): Months since 0 AD
        is_null (bool): If true, this ParsedDate is empty
    """
    _current_month: ClassVar[int] = 2017 * 12 + 5
    _monthToNum: ClassVar[Dict] = {
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'May': 5,
        'Jun': 6,
        'Jul': 7,
        'Aug': 8,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dec': 12
    }

    day: Optional[int]
    month: Optional[int]
    year: Optional[int]
    quarter: Optional[int]
    months_since: Optional[int]
    is_null: bool

    def __init__(self, year: Optional[int] = None, month: Optional[int] = None,
                 day: Optional[int] = None, quarter: Optional[int] = None,
                 months_since: Optional[int] = None) -> None:
        self.is_null = year is None
        self.year = year
        self.month = month
        self.day = day
        self.quarter = quarter
        self.months_since = months_since

    @classmethod
    def parse_date(cls, date_str: str) -> 'ParsedDate':
        """
        Instantiates based on a date literal

        Args:
            date_str (str): A date literal
        Returns:
            ParsedDate: The parsed date
        """
        # Return None if empty string
        if date_str == '-' or 'keys' in date_str.lower():
            return ParsedDate()

        # 4Q/2018
        # 07/2017
        result: ParsedDate
        if '/' in date_str:
            date_parts = date_str.split('/')
            year = int(date_parts[1])
            month_str = date_parts[0]
            if 'Q' in month_str:
                quarter = int(month_str[0])
                months_since = (year * 12 + quarter * 3) - cls._current_month
                result = ParsedDate(year, quarter=quarter,
                                    months_since=months_since)
            else:
                month = int(month_str)
                months_since = (year * 12 + month) - cls._current_month
                result = ParsedDate(year, month=month,
                                    months_since=months_since)
        else:
            # 01 Apr 1978
            date_parts = date_str.split(' ')
            day = int(date_parts[0])
            month = cls._monthToNum[date_parts[1]]
            year = int(date_parts[2])
            months_since = (year * 12 + month) - cls._current_month
            result = ParsedDate(year, month=month, day=day,
                                months_since=months_since)
        return result

    def to_dict(self) -> Optional[Dict]:
        """
        To Dictionary

        Returns:
            Dict: dictionary. One-way transformation.
        """
        if self.is_null:
            return None
        dict_obj = {'year': self.year, 'month': self.month, 'day': self.day,
                    'quarter': self.quarter, 'months_since': self.months_since}
        return dict_obj
