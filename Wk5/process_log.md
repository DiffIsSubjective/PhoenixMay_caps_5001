# QUESTION 1: Data Contract and Pseudocode for Data Cleaner

Establish RAW_INSPECTIONS dictionary with values from assignment.

## Helper functions:

DEFINE valid_hive_id(value):
    """
    This will check if the hive_id is in the proper format.

    ARGUMENTS:
    value: can be any type, but this will return FALSE if it's not a string. This is the hive_id we're checking.

    RETURNS: TRUE if hive_id is valid, FALSE if it's not.
    """
        if value is not a string:
            return FALSE
        hive_id = value stripped of whitespace and converted to UPPERCASE
        if hive_id is not 4 characters long:
            RETURN FALSE
        if hive_id does not start with "H-":
            RETURN FALSE
        if hive_id does not end with 2 digits:
            RETURN FALSE
        else:
            RETURN hive_id (normalized version of original hive ID)
        
===== End of valid_hive_id function =====

DEFINE parse_date(value):
    """
    Returns a datetime.date or None if the date is invalid.

    ARGUMENTS:
    value: can be any type, but will return NONE if it's not a datetime.date or a string.

    RETURNS:
    value converted to a datetime.date, or NONE if conversion fails.
    """
        if value is already a datetime.date:
            RETURN value
        if value is not a string:
            RETURN NONE
        use datetime.strptime to try using formats YYYY-MM-DD or MM/DD/YYYY (slashes or dashes OK as separators) to convert str to datetime.date
            if conversion works:
                return datetime.date value
            if conversion fails:
                RETURN NONE
        
===== End of parse_date function ======

DEFINE convert_bool(value):
    """
    Converts yes/no queen_seen strings to booleans.
    
    ARGUMENTS:
    value: can be any type, but the function will return None if it's not a string or boolean.

    RETURNS:
    value converted into a boolean, or None if conversion fails.
    """
        if already boolean:
            RETURN value
        else:
            if value is a string:
                strip whitespaces from queen_seen for consistency
                change queen_seen to lowercase for consistency
                if queen_seen is "yes":
                    norm_record["queen_seen"] = True
                elif queen_seen is "no":
                    norm_record["queen_seen"] = False
            RETURN NONE if it hasn't returned anything by this point
        
===== End of convert_bool function =====

## Main function:

DEFINE function normalize_record(record: dict) -> tuple[dict | None, str]:
    """
    This function will take a record and normalize it.

    ARGUMENTS:
    record: Must be DICTIONARY. It's the entry from the RAW_INSPECTIONS list of dictionaries that will be normalized.

    RETURNS:
    A TUPLE with two values. The first will be either a DICTIONARY containing the cleaned record or it will be empty (None) if
    the record was rejected. The second value will be a STRING that explains why the record was rejected if it was, or a blank string.
    """

    norm_record = {}   #This sets up a blank dictionary for the final normalized record.

    #1. Normalize hive_id by stripping whitespace and converting to uppercase. Accepts only "H-" followed by 2 digits.
    NOTE: this will have its own HELPER FUNCTION called valid_hive_id.
        call valid_hive_id with input record.get("hive_id")
        if valid_hive_id is FALSE:
            RETURN (None, "Invalid hive_id")
        else:
            set norm_record["hive_id"] to output from valid_hive_id


    #2 Parse inspection_date by accepting YYYY-MM-DD or MM-DD-YYYY and storing as a datetime.date. Impossible dates are rejected.
    NOTE: This will have its own HELPER FUNCTION called parse_date.
        call parse_date with input record.get("inspection_date")
        if parse_date returns None:
            RETURN (None, "Invalid inspection_date")
        else:
            set norm_record["inspection_date"] to datetime.date returned by parse_date


    #3 Normalize temp_f by removing the final "F" and converting to float. None is fine. Reject values outside -20 thru 130.
        if temp_f value is None:
            norm_record["temp_f"] = None
        otherwise:
            if temp_f ends with "F":
                strip final char
            convert to float
            if conversion fails:
                change temp_f to None
            if value is outside less than -20 or above 130:
                RETURN (None, "temp_f out of range")
            else:
                set norm_record["temp_f"] to normalized temp


    #4 Normalize weight_lb by converting to float. If this fails, store None but don't reject. Do reject any negative weight.
        try to convert to float
        if conversion fails:
            weight_lb = None
        otherwise:
            if value is less than 0:
                RETURN (None, "negative weight")
            else:
                set norm_record["weight_lb"] to normalized weight
                

    #5 Normalize mites by converting to type int. Reject any negative values.
        try to convert to int
        if conversion fails:
            RETURN (None, "Invalid mites")
        if value is negative:
            RETURN (None, "Negative mites")
        else:
            set norm_record["mites"] to normalized mites


    #6 Normalize queen_seen by converting "yes" and "no" values to booleans. If already a boolean, keep as-is. Reject any other value besides boolean.
    NOTE: This will have its own HELPER FUNCTION called convert_bool.
        call convert_bool with input record.get("queen_seen")
        if convert_bool returns None:
            RETURN (None, "invalid queen_seen")
        else:
            set norm_record["queen_seen"] to boolean returned by convert_bool
                

        #7 Normalize notes by converting any missing notes to an ampty string.
            if notes = None:
                norm_record["notes"] = ""
            else:
                norm_record["notes"] = record.get("notes")

    RETURN (norm_record, "")


## Two Edge Cases

One edge case could be if the inspection_date value is February 29th on a non-leap year. Since that would be an impossible date, it should be
rejected, but only on certain years, which would be tricky to program manually. Using Python's datetime.date() function will solve this by
only allowing actual leap years.

A second edge case could be if the weight is a non-number, like "fifty lbs". Since the instructions say to not reject invalid weight unless
it's negative, I included a section to change the weight to type None if converting it to float fails.

## Prediction

I predict that 2 records will be rejected, 1 for an impossible date and 1 for a negative mite value. This doesn't include duplicates since
this function isn't getting rid of duplicates, that's the next one.