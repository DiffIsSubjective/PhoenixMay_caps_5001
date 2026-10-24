"""
This module contains three helper functions that are called in normalize_record.
The helper functions are valid_hive_id, parse_date_ and convert_bool.
"""

from datetime import date, datetime

def valid_hive_id(value): # Helper function
    """
    Checks for H- followed by exactly two digits.
    
    ARGUMENTS:
    value: can be any type, but will return False if not a string.
    This is the Hive ID we're checking to see if it's properly formatted.

    RETURNS:
    True if the Hive ID is in proper format, False if not.
    """

    if not isinstance(value, str): # Checks if hive_id is a string. If not, returns False.
        return False

    hv_id = value.strip().upper() # Strips whitespace from hive_id string and makes it uppercase.

    if len(hv_id) != 4: # If hive_id isn't exactly 4 characters, returns False.
        return False

    if hv_id[0:2] != "H-": # If the first two characters aren't "H-", returns False.
        return False

    # If the last two characters aren't digits, returns False.
    if not hv_id[2].isdigit() or not hv_id[3].isdigit():
        return False

    return hv_id # Returns normalized hive_id if all criteria is met.


def parse_date(value): # Helper function
    """"
    Returns a datetime.date or None if the date is invalid.

    ARGUMENTS:
    value: can be any type. The date you are trying to convert to a datetime.date().

    RETURNS:
    value converted to a datetime.date or None if it's an invalid date.
    """

    # Gen AI was used to learn about the isinstance function, since I wanted to do
    # different things with different data types and wanted to see what could be used besides type.
    if isinstance(value, date): # Checks if the value is already a date, returns it if so.
        return value

    if not isinstance(value, str): # Checks if the value is a string, returns None if it isn't.
        return None

# This tries using YYYY-MM-DD or MM-DD-YYYY, with dashes (-) and slashes (/) to format the
# string into a datetime.date.
# If it succeeds, then it returns a datetime.date. If all attempts fail, returns None.
    for fmt in ["%m-%d-%Y", "%m/%d/%Y", "%Y-%m-%d", "%Y/%m/%d"]:
        # ERROR HANDLING: if we get a ValueError here, we just continue trying other formats.
        try:
            return datetime.strptime(value, fmt).date()
        # Used Gen AI to learn about ValueError.
        except ValueError:
            continue

    return None


def convert_bool(value): # Helper function
    """
    Converts yes/no queen_seen strings to booleans.
    
    ARGUMENTS:
    value: can be any type, but the function will return None if it's not a string or boolean.

    RETURNS:
    value converted into a boolean, or None if conversion fails.
    """

    if isinstance(value, bool): # Checks if value is already boolean. If so, returns it as-is.
        return value

    # Checks if the value is a string. If so, strips whitespaces and makes it lowercase.
    if isinstance(value, str):
        value = value.strip().lower()

        if value == "yes": # Changes "yes" str to True.
            return True

        if value == "no": # Changes "no" str to False.
            return False

    return None # Returns None if it doesn't return a boolean value with the above code.
