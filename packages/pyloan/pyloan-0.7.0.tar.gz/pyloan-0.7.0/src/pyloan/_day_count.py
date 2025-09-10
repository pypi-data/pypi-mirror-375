# -*- coding: utf-8 -*-
"""
This module contains functions for calculating the number of days between two dates
based on different day count conventions.
"""
import calendar as cal
from datetime import datetime
from typing import Dict, Callable, Tuple

def _thirty_e_360_isda(dt1: datetime, dt2: datetime) -> Tuple[int, int]:
    """
    Calculates the number of days using the 30E/360 ISDA convention (a.k.a 30/360 German).
    This is a simplified version where every month is treated as having 30 days.
    """
    y1, m1, d1 = dt1.year, dt1.month, dt1.day
    y2, m2, d2 = dt2.year, dt2.month, dt2.day

    # If the start date is the last day of the month, it is treated as the 30th.
    if d1 == cal.monthrange(y1, m1)[1]:
        d1 = 30

    # If the end date is the last day of the month, it is treated as the 30th.
    if d2 == cal.monthrange(y2, m2)[1]:
        d2 = 30

    return (360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)), 360


def _thirty_e_360(dt1: datetime, dt2: datetime) -> Tuple[int, int]:
    """
    Calculates the number of days using the 30E/360 convention.
    This is method is identical to 30E/360 ISDA, except for February.
    February is a special case; it is never adjusted and its actual
    number of days (28 or 29) are used for calculation.
    """
    y1, m1, d1 = dt1.year, dt1.month, dt1.day
    y2, m2, d2 = dt2.year, dt2.month, dt2.day

    # If the start date is the last day of the month, it is treated as the 30th.
    if d1 == 31:
        d1 = 30

    # If the end date is the last day of the month, it is treated as the 30th.
    if d2 == 31:
        d2 = 30

    return (360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)), 360


def _actual_365(dt1: datetime, dt2: datetime) -> Tuple[int, int]:
    """
    Calculates the day count using the A/365 convention.
    This is a standard for loans in the UK, Australia, and New Zealand.
    """
    return (dt2 - dt1).days, 365


def _actual_360(dt1: datetime, dt2: datetime) -> Tuple[int, int]:
    """
    Calculates the day count using the A/360 convention.
    This is common for short-term and floating-rate loans, especially in the US and Europe.
    """
    return (dt2 - dt1).days, 360


def _actual_actual(dt1: datetime, dt2: datetime) -> Tuple[int, int]:
    """
    Calculates the day count using the A/A convention.
    This is considered the most accurate method and is sometimes used for
    mortgages and government bonds.
    """
    y1, y2 = dt1.year, dt2.year
    days = (dt2 - dt1).days
    
    if y1 == y2:
        return days, 366 if cal.isleap(y1) else 365
    
    # Calculate days in the first and last years of the period
    days_in_y1 = (datetime(y1 + 1, 1, 1) - dt1).days
    days_in_y2 = (dt2 - datetime(y2, 1, 1)).days
    
    # Get number of full years in between
    full_years = y2 - y1 - 1
    
    # Sum the days from all parts of the period
    day_count = days_in_y1 + days_in_y2
    
    # Add days for the full years
    for y in range(y1 + 1, y2):
        day_count += 366 if cal.isleap(y) else 365
    
    # The denominator is determined by the number of days in the year of the coupon payment
    days_in_year = 366 if cal.isleap(y2) else 365
    
    return day_count, days_in_year


# Create a dictionary to map method names to functions
DAY_COUNT_METHODS: Dict[str, Callable[[datetime, datetime], Tuple[int, int]]] = {
    '30E/360 ISDA': _thirty_e_360_isda,
    '30E/360': _thirty_e_360,
    'A/365': _actual_365,
    'A/360': _actual_360,
    'A/A': _actual_actual,
}
