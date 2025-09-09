# -*- coding: utf-8 -*-

def generate_sequence(r, n):
    """
    Generate a sequence of strings with incrementing numeric suffix.

    :param r: Base string ending with a number (e.g., 'XXX001')
    :param n: Number of elements in the sequence
    :return: List of generated sequence strings

    Example:
        >>> generate_sequence('XXX001', 2)
        ['XXX001', 'XXX002']
    """
    if n == 1:
        return [r]

    prefix = r[:-2]
    last_two_digits = int(r[-2:])
    sequence = [f"{prefix}{str(i).zfill(2)}" for i in range(last_two_digits, last_two_digits + n)]
    return sequence


def sql_column_get(column):
    """
    Extract column name from a SQL expression like 'table.column'.

    :param column: Column string, optionally prefixed by table name
    :return: Column name without table prefix if present

    Example:
        >>> sql_column_get('user.id')
        'id'
    """
    column_list = column.split('.')
    return column_list[1] if len(column_list) > 1 else column_list[0]


def format_msg(input_str):
    """
    Format message based on leading symbol '<' or '>'.

    If input starts with '<' or '>', returns a list of numbers in a range:
    - '<': Returns range from (number - 30) to number (exclusive)
    - '>': Returns range from number to (number + 30) (exclusive)

    Otherwise, returns a list containing the original string.

    :param input_str: Input string that may start with '<' or '>'
    :return: List of formatted messages or numbers

    Example:
        >>> format_msg('<100')
        [70, 71, ..., 99]
    """
    if not input_str or input_str[0] not in ('<', '>'):
        return [input_str]

    symbol = input_str[0]
    try:
        number = int(input_str[1:])
    except ValueError:
        return [input_str]

    range_map = {
        '<': range(number - 30, number),
        '>': range(number, number + 30)
    }

    return list(range_map.get(symbol, []))
