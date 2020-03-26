# This file contains functions related to formatting..

import math
from datetime import date


def get_today_date_formatted(date_format):
    today = date.today()
    formatted_date = today.strftime(date_format)
    return formatted_date


def get_string_no_decimals(string):
    return string.split('.', 1)[0]


def get_int_no_decimals(string):
    if str(string).isalpha():
        return string

    decimal = float(string)
    aprox_number = math.ceil(decimal)
    return int(aprox_number)
