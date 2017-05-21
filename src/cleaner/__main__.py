"""
Simple module for doing a basic checks and cleanup of the scraped data.
"""
from os import path
import re
import time

import ProjUtils
from cleanup import AddGeo, ComputeLease, ExamineProperty, ReplaceFix, RootJsonFix
from cleanup.objects.ParsedDate import ParsedDate
from cleanup.objects.ReplacePair import ReplacePair
from db.mongodb.MongoImporter import MongoImporter

_JSON_LOC = path.join('data', 'json')
_LOG_LOC = path.join('data', 'cleanup.log')


def _null_fix() -> None:
    """
    Fix[es] to ensure nothing crashes because of a None value
    """
    ReplaceFix.run(_JSON_LOC, _LOG_LOC, ReplacePair(
        'blocks.apartments.lease_price_list.lease', 'null lease',
        lambda v: (v is None, '-')))


def _expand_address_acronym() -> None:
    """
    Expands address acronyms like NTH to NORTH
    """
    def expand(acro, expd):
        ReplaceFix.run(_JSON_LOC, _LOG_LOC, ReplacePair(
            'blocks.street', acro,
            lambda v: (acro in v, v.replace(acro, expd))))

    def re_expand(acro, expd):
        ReplaceFix.run(_JSON_LOC, _LOG_LOC, ReplacePair(
            'blocks.street', acro,
            lambda v: (True, re.sub(acro, expd, v))))

    curr_time = time.time()
    expand('BT ', 'BUKIT ')
    expand("C'WEALTH ", 'COMMONWEALTH ')
    expand('JLN ', 'JALAN ')
    re_expand(r'\bLOR ', 'LORONG ')
    expand('ST. ', 'SAINT ')
    expand('UPP ', 'UPPER ')
    re_expand(r' AVE\b', ' AVENUE')
    re_expand(r' CL\b', ' CLOSE')
    re_expand(r' CRES\b', ' CRESCENT')
    expand(' CTRL', ' CENTRAL')
    re_expand(r' DR\b', ' DRIVE')
    expand(' GDNS', ' GARDENS')
    expand(' HTS', ' HEIGHTS')
    expand(' NTH', ' NORTH')
    expand(' PK', ' PARK')
    re_expand(r' PL\b', ' PLACE')
    expand(' RD', ' ROAD')
    re_expand(r' ST\b', ' STREET')
    re_expand(r' TER\b', ' TERRACE')
    print('Expand Address Acronym: {:.2f} secs'.format(
        time.time() - curr_time))


def _date_to_dict() -> None:
    """
    Parses the date attribute into a dictionary
    """
    def func(val):
        to_parse = not isinstance(val, dict)
        datedict = ParsedDate.parse_date(val).to_dict() if to_parse else val
        return to_parse, datedict

    def parse_date(prop: str):
        ReplaceFix.run(_JSON_LOC, _LOG_LOC, ReplacePair(prop, '', func))

    curr_time = time.time()
    parse_date('blocks.lcd_date')
    parse_date('blocks.pcd_date')
    parse_date('blocks.dpd_date')
    print('Date to Dict: {:.2f} secs'.format(time.time() - curr_time))


def _change_types() -> None:
    """
    Changes the types of some attributes
    """
    curr_time = time.time()

    # blocks.apartments.area from float to int
    areas = ExamineProperty.retrieve(_JSON_LOC, 'blocks.apartments.area')
    if all([_ - int(_) == 0 for _ in areas]):
        ReplaceFix.run(_JSON_LOC, _LOG_LOC, ReplacePair(
            'blocks.apartments.area', 'to int', lambda v: (True, int(v))))

    print('Change Types: {:.2f} secs'.format(time.time() - curr_time))


def _check_properties(to_run: bool = True) -> None:
    """
    Checks properties to help make cleaning decisions

    Args:
        to_run (bool): If False, this function does not run
    """
    def check(prop):
        return ExamineProperty.check(_JSON_LOC, prop)

    if to_run:
        curr_time = time.time()
        check('blocks.apartments.area')
        check('blocks.apartments.floor')
        check('blocks.apartments.is_repurchased')
        check('blocks.apartments.lease_price_list.price')
        check('blocks.apartments.lease_price_list.lease')
        check('blocks.apartments.unit')
        check('blocks.block_code.block_num')
        check('blocks.block_code.contract')
        check('blocks.block_code.neighbourhood')
        check('blocks.dpd_date')
        check('blocks.flat_type')
        check('blocks.lcd_date')
        check('blocks.pcd_date')
        check('blocks.quota_chinese')
        check('blocks.quota_malay')
        check('blocks.quota_other')
        check('blocks.street')
        check('blocks.town')

        # Properties that appear after processing
        # check('blocks.lat')
        # check('blocks.long')
        check('blocks.title')

        print('Check Properties: {:.2f} secs'.format(time.time() - curr_time))


def main() -> None:
    """
    Main Function
    """
    ProjUtils.set_project_cwd()

    # Cleaning up
    RootJsonFix.run(_JSON_LOC, _LOG_LOC)
    _null_fix()
    _expand_address_acronym()
    _date_to_dict()
    ComputeLease.run(_JSON_LOC, _LOG_LOC)
    AddGeo.run(_JSON_LOC, _LOG_LOC)
    _change_types()

    # Check properties
    to_run = False
    _check_properties(to_run)

    # Import Data
    dbimporter = MongoImporter(_JSON_LOC)
    dbimporter.run()


if __name__ == '__main__':
    main()
    input('Press any key to exit...')
    exit(0)
