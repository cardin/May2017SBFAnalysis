"""
Fixes the lease on lease_price_list
"""
import json
import os
from os import path
from typing import Dict

from .objects.CleanupLog import CleanupLog

_PROCESS_NAME = 'ComputeLease'


def run(json_loc: str, log_loc: str) -> None:
    """
    Computes the remaining lease by making a few changes:
        * Changes numeric strings to int
        * Computes strings (e.g. -, Remaining, keys collection date) to int

    The assumptions it makes to compute remaining lease:
        * Lease is 99 years by default
        * If lcd, pcd, dpd dates are before May'17, remaining lease is below 99 years
        * If lcd, pcd, dpd dates are after May'17, 99 lease begins on latest date

    Args:
        json_loc (str): location of JSON folder
        log_loc (str): location of cleaning log
    """
    if CleanupLog.has_done(_PROCESS_NAME, log_loc):
        print('Skipping {}'.format(_PROCESS_NAME))
        return

    # Iterate through all files
    print('--------------------------------')
    print('[ComputeLease]')
    for root, _, filenames in os.walk(json_loc):
        print('Running directory {}'.format(root))

        for filename in filenames:
            filepath = path.join(root, filename)

            # Open the file
            data: Dict
            with open(filepath) as fstream:
                data = json.load(fstream)
                fstream.close()

            if _compute_lease(data):  # if modified
                # Save the file
                with open(filepath, 'w') as fstream:
                    json.dump(data, fstream, indent=4)
    CleanupLog.log_done(_PROCESS_NAME, log_loc)


def _compute_lease(data: Dict) -> bool:
    """
    Computes the remaining lease.

    Args:
        data (dict): Dictionary (aka JSON)

    Returns:
        bool: Whether a change was made to `data`
    """
    for block in data['blocks']:
        lease_left = _precompute_remaining_lease(block)

        for apt in block['apartments']:
            for lease_price in apt['lease_price_list']:
                lease = lease_price['lease']

                # early termination. already processed
                if isinstance(lease, int):
                    return False

                if lease.isdigit():
                    lease_price['lease'] = int(lease)
                else:
                    lease_price['lease'] = lease_left
    return True


def _precompute_remaining_lease(block: Dict) -> int:
    """
    Computes the lease remaining, based on lcd, pcd, and dpd dates

    Args:
        block (Dict): Dictionary containing the block


    Returns:
        int: Remaining lease in years
    """
    months = []
    if block['lcd_date']:
        months.append(block['lcd_date']['months_since'])
    if block['pcd_date']:
        months.append(block['pcd_date']['months_since'])
    if block['dpd_date']:
        months.append(block['dpd_date']['months_since'])
    longest_months = max(months) if months else 0

    lease_left: int
    if longest_months >= 0:
        lease_left = 99
    else:
        lease_left = 99 - abs(round(longest_months / 12.0))
    return lease_left
