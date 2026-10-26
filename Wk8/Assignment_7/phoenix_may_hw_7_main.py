"""
This is the main body of code for Assignment 7. It normalizes the RAW_INSPECTIONS records
and performs various data transformations and analyses on them.
"""

from original_records import RAW_INSPECTIONS
from datetime import date
import pandas as pd
import normalize_helper_functions as nhf
from reject_records import ALL_REJECTS

# This prints the length of the list of records, just so I know how many records there are.
print(f"The length of the original RAW_INSPECTIONS list is {len(RAW_INSPECTIONS)}.")

# QUESTION 2: Normalize one record

def normalize_record(rec: dict) -> tuple[dict | None, str]: # This is the main function.
    """
    This function will take a record and normalize it.

    ARGUMENTS:
    rec: Must be DICTIONARY. It's the entry from the RAW_INSPECTIONS
    list of dictionaries that will be normalized.

    RETURNS:
    A TUPLE with two values. The first will be either a DICTIONARY containing the cleaned record
    or it will be empty (None) because the record was rejected. The second value will be a STRING
    that explains why the record was rejected if it was, or a blank string.
    """

    norm_record = {} # Establishes blank dictionary for the normalized record output.

    #1. Normalize hive_id by stripping whitespace and converting to uppercase.
    # Accepts only "H-" followed by 2 digits.
    h_id = rec.get("hive_id") # Gen AI was used to learn about get().

    norm_id = nhf.valid_hive_id(h_id) # Calls the valid_hive_id helper function from earlier.

    if norm_id is False:
        return (None, "invalid hive_id") # If hive_id is false, rejects for invalid hive id.

    norm_record["hive_id"] = norm_id # Sets norm_record to normalized hive id.

    #2 Parse inspection_date by accepting YYYY-MM-DD or MM-DD-YYYY and
    # storing as a datetime.date. Impossible dates are rejected.
    # Uses the parse_date helper function.
    inspection_date = nhf.parse_date(rec.get("inspection_date"))

    # If we failed to convert the date to a datetime.date, rejects for invalid date.
    if inspection_date is None:
        return (None, "invalid inspection_date")

    # Otherwise, sets norm_record to normalized date.
    norm_record["inspection_date"] = inspection_date

    #3 Normalize temp_f by removing the final "F" and converting to float.
    # None is fine. Reject values outside -20 thru 130.
    temp = rec.get("temp_f")

    if temp is None: # If there is no temp, sets norm_record temp to none.
        norm_record["temp_f"] = None
    else:
        try:
            if isinstance(temp, str): # If temp is a string, strips whitespaces.
                temp = temp.strip()

                if temp.upper().endswith("F"): # If temp ends with an F, removes it.
                    temp = temp[:-1].strip()

            temp = float(temp) # Tries to convert temp to a float.

        except (TypeError, ValueError):
            return (None, "temp_f bad input")

        if temp < -20 or temp > 130:
            return (None, "temp_f out of range") # If temp is under -20 or over 130, rejects.

        norm_record["temp_f"] = temp # If checks are passed, sets norm_record to normalized temp.

    #4 Normalize weight_lb by converting to float. If this fails, store
    # None but don't reject. Do reject any negative weight.
    weight = rec.get("weight_lb")

    # ERROR HANDLING: if converting to float causes an error, we just set weight to None.
    try: # Tries to convert weight to a float.
        weight = float(weight)
    except (TypeError, ValueError):
        weight = None # If conversion doesn't work, sets weight to None.

    if weight is not None and weight < 0: # Rejects if weight is negative.
        return (None, "negative weight")

    norm_record["weight_lb"] = weight # Sets norm_record to normalized weight.

    #5 Normalize mites by converting to type int. Reject any negative values.
    mites = rec.get("mites")

    try: # Tries to convert mites to type int.
        mites = int(mites)
    except (TypeError, ValueError):
        return (None, "invalid mites") # If conversion doesn't work, rejects for invalid mites.

    if mites < 0:
        return (None, "negative mites") # If mites are negative, rejects for negative mites.

    norm_record["mites"] = mites # If checks pass, sets norm_record mites to normalized mites.

    #6 Normalize queen_seen by converting "yes" and "no" values to booleans.
    # If already a boolean, keep as-is. Reject any other value besides boolean and yes/no.
    # Uses convert_bool helper function from earlier.
    queen_seen = nhf.convert_bool(rec.get("queen_seen"))

    if queen_seen is None: # If convert_bool returned None, rejects for invalid queen_seen.
        return (None, "invalid queen_seen")

    # Otherwise, sets norm_record queen_seen to normalized boolean value.
    norm_record["queen_seen"] = queen_seen

    #7 Normalize notes by converting any missing notes to an ampty string.
    notes = rec.get("notes")

    if notes is None: # Converts notes to empty string if it's none.
        notes = ""

    norm_record["notes"] = notes # Sets norm_record notes to normalized notes value.

    # If it's not rejected earlier, this returns the normalized record
    # and an empty reason string.
    return (norm_record,"")

print(f"Normalized 1st record's dictionary: {normalize_record(RAW_INSPECTIONS[0])}.")
print(f"Normalized 6th record's rejection output,"
      f" impossible date: {normalize_record(RAW_INSPECTIONS[5])}")

# QUESTION 3: Clean the collection and keep an audit trail

def clean_records(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    This function has normalize_record from the previous cell loop thru a whole list of records.

    ARGUMENTS:
    records: must be a LIST of DICTIONARIES. This is the list of records you are cleaning.

    RETURNS:
    A TUPLE with two lists. The first list is all cleaned records that
    were not rejected. The second list is all records that were rejected
    during the cleaning process.
    """
    cleaned = [] # Establishes blank list for normalized records
    rejected = [] # Blank list for rejected records.
    seen = [] # Blank list for records the function has "seen". Used to check for duplicates.

    # This uses enumerate to iterate thru the list of records, so we can access the index and value.
    for source_index, record in enumerate(records):
        #Gen AI was used to learn to use enumerate properly to access index and value.

        # Normalizes the record, assigns normalized record (index 0) to
        # "clean" and reason string (index 1) to "reason"
        clean = normalize_record(record)[0]
        reason = normalize_record(record)[1]

        # If normalization failed (i.e., clean is type None), adds to audit entry dictionary.
        if clean is None:
            audit_entry = {"source_index": source_index} # Adds source index first.

            # Adds hive_id second, if it is available.
            if "hive_id" in record:
                audit_entry["hive_id"] = record["hive_id"]

            audit_entry["reason"] = reason # Adds rejection reason third.

            # Adds the audit entry dictionary to the rejected list.
            rejected.append(audit_entry)
            # If it's rejected here, skips the remaining code
            # (checking for dupliates) since it's not needed.
            continue

        # Creates a key using hive_id and inspection_date to look for duplicates.
        key = (clean["hive_id"], clean["inspection_date"])

        # Checks for duplicates in the "seen" list. If it's in there,
        # adds the record to the rejected list.
        if key in seen:
            rejected.append({"source_index": source_index,
                "hive_id": clean["hive_id"],
                "reason": "duplicate inspection"})
            continue # If it's already in seen, skips the rest of
            # this code so it's not added a second time.

        # If the record is not a duplicate, we add it to the "seen" list and the "cleaned" list.
        seen.append(key)
        cleaned.append(clean)

    return (cleaned, rejected) # Returns tuple with list of cleaned and rejected records.


# This prints the total successes and rejections from the clean_records function.
print(f"For the original RAW_INSPECTIONS list, clean_records returns {len(clean_records(RAW_INSPECTIONS)[0])}"
       " successfully cleaned records and {len(clean_records(RAW_INSPECTIONS)[1])} rejections.\n")
print(f"The list of cleaned records is as follows: {clean_records(RAW_INSPECTIONS)[0]}.\n")
print(f"The list of rejections is as follows: {clean_records(RAW_INSPECTIONS)[1]}.\n")


def audit_counts(rejected: list[dict]) -> dict:
    """
    This goes through the rejections and creates a dictionary showing
    how many records were rejected for each reason.

    ARGUMENTS:
    rejected: must be LIST of DICTIONARIES. This is the list of rejected
    records from the clean_records function.

    RETURNS:
    a DICTIONARY showing rejection reasons as keys and the # of records
    rejected for each reason as values.
    """

    # This establishes a "counts" dictionary with every rejection reason. Values are set to 0 at the beginning.
    counts = {"invalid hive_id": 0, "invalid inspection_date": 0, "temp_f bad input": 0, "temp_f out of range": 0,
              "negative weight": 0, "invalid mites": 0, "negative mites": 0, "invalid queen_seen": 0,
              "duplicate inspection": 0}

    for rejection in rejected: # Iterates through each rejection in rejected list.
        reason = rejection["reason"] # Assigns the rejection reason str to the "reason" variable.

        counts[reason] += 1 # Adds one to the value for the rejection reason key.

    return counts # Returns the updated counts dictionary.

print(f"The output of audit_counts for the original RAW_INSPECTIONS list is: {audit_counts(clean_records(RAW_INSPECTIONS)[1])}.\n")

# Below are the 3 specific tests called for by the assignment.

# TEST 1
# Tests what happens if audit_counts has an empty input. All rejection counts are 0.
print(f"TEST 1: The output of function audit_counts with an empty input is: {audit_counts("")}.")

# TEST 2
# Tests what happens if audit counts has two duplicates (i.e., three of the same record).

# This establishes a list with three of the same record. So one is original, and two are duplicates.
TWO_DUPLICATES = [{"hive_id": "H-01", "inspection_date": "2026-08-01", "temp_f": 84,

"weight_lb": "142.5", "mites": 3, "queen_seen": True, "notes": "calm"},
{"hive_id": "H-01", "inspection_date": "2026-08-01", "temp_f": 84,

"weight_lb": "142.5", "mites": 3, "queen_seen": True, "notes": "calm"},
{"hive_id": "H-01", "inspection_date": "2026-08-01", "temp_f": 84,

"weight_lb": "142.5", "mites": 3, "queen_seen": True, "notes": "calm"}]

# The result is that the "duplicate inspection" reason has a count of 2, and everything else is a count of 0.
print(f"TEST 2: The output of function audit_counts with two duplicate records is: {audit_counts(clean_records(TWO_DUPLICATES)[1])}.")

#TEST 3
# Tests what happens if we use a collection where every record will be rejected.
# The result is that the rejection counts add up to 5, which is the length of the collection of records.
print(f"TEST 3: The output of function audit_counts with a collection of {len(ALL_REJECTS)} records where each record is rejected is: {audit_counts(clean_records(ALL_REJECTS)[1])}.")

# ASSIGNMENT 6, Question 4: HiveInspection class & HiveSummary class
# Doing this here so the classes can be used in later functions.
# calculate_risk from ASSIGNMENT 6, Question 1 is within the HiveInspection class.
# Gen AI was used to come up with potential ideas for classes, these were my
# top picks since they're more directly useful in the assignment.

class HiveInspection:
    """
    Represents one cleaned hive inspection and its associated risk information.

    A class makes sense for this assignment because each inspection contains
    several related pieces of information, such as hive ID, inspection date,
    temperature, weight, mite count, and queen status. The class keeps this
    related data together and provides methods for working with an individual
    inspection.

    Instance methods are used for operations involving a specific inspection.
    Static methods are used for general validation that does not depend on a
    particular inspection. The class method provides an alternate way to create
    an inspection from a dictionary.

    This class is used in the function add_risk_fields.
    """

    def __init__(
        self,
        hive_id: str,
        inspection_date: date,
        temp_f: float | None,
        weight_lb: float | None,
        mites: int,
        queen_seen: bool,
        notes: str
    ):
        """
        Initialize a HiveInspection object.

        ARGUMENTS:
        hive_id: The normalized ID of the hive.
        inspection_date: The date of the inspection.
        temp_f: The inspection temperature in F, or None.
        weight_lb: The hive weight in lbs, or None.
        mites: The number of mites found during the inspection.
        queen_seen: True if the queen was seen, otherwise False.
        notes: Notes from inspection.
        """

        self.hive_id = hive_id
        self.inspection_date = inspection_date
        self.temp_f = temp_f
        self.weight_lb = weight_lb
        self.mites = mites
        self.queen_seen = queen_seen
        self.notes = notes

        self.risk_score = 0
        self.risk_reasons = []

    # Used Gen AI to learn about using @ for decorators, then saw they were
    # already in the class slides. Good confirmation of its output, haha.
    @staticmethod
    def valid_mite_count(mites: int) -> bool:
        """
        Check whether a mite count is valid.

        ARGUMENTS:
        mites: The mite count to validate.

        RETURNS:
        True if mites is a non-negative integer, otherwise False.
        """

        return isinstance(mites, int) and mites >= 0

    @classmethod
    def from_dict(cls, record: dict):
        """
        Create a HiveInspection object from a cleaned record dictionary.

        ARGUMENTS:
        record: A dictionary containing the fields required to create a
            HiveInspection object.

        RETURNS:
        A new HiveInspection object populated from the dictionary.
        """

        return cls(
            hive_id=record["hive_id"],
            inspection_date=record["inspection_date"],
            temp_f=record["temp_f"],
            weight_lb=record["weight_lb"],
            mites=record["mites"],
            queen_seen=record["queen_seen"],
            notes=record["notes"]
        )

    # This is the function from question 1. Was originally a standalone function,
    # but it only needs to be defined in this class to be used.
    def calculate_risk(self, previous_weight: float | None = None) -> tuple[int, list[str]]:
        """
        Calculates and stores the risk score for this inspection.

        ARGUMENTS:
        self: since this is within a class, we don't need to specifically define the record
        argument anymore, but this represents a single inspection record.

        previous_weight: Float type. The previous valid weight for the same hive, or None
        if there is no previous valid weight.

        RETURNS:
        A tuple containing the integer risk score and a list of reason strings.

        If there is no previous weight or the current weight is missing,
        no weight-change points are awarded.
        """

        # Set named constants for risk thresholds and pts
        mites_risk_threshold = 8
        mites_risk_pts = 3

        queen_risk_pts = 2

        wgt_loss_threshold = 10
        wgt_loss_pts = 2

        low_temp_threshold = 55
        high_temp_threshold = 95
        temp_risk_pts = 1
        
        score = 0
        reasons = []

        if self.mites >= mites_risk_threshold:
            score += mites_risk_pts
            reasons.append("mites at or above 8")

        if self.queen_seen is False:
            score += queen_risk_pts
            reasons.append("queen not seen")

        # Missing prior or current wgt means no wgt change pts
        if previous_weight is not None and self.weight_lb is not None:
            weight_loss = previous_weight - self.weight_lb

            if weight_loss >= wgt_loss_threshold:
                score += wgt_loss_pts
                reasons.append("weight decreased by at least 10 lb")

        if self.temp_f is not None and (
            self.temp_f < low_temp_threshold
            or self.temp_f > high_temp_threshold
        ):
            score += temp_risk_pts
            reasons.append("temperature outside 55-95 F")

        self.risk_score = score
        self.risk_reasons = reasons

        return int(self.risk_score), self.risk_reasons

    def to_dict(self) -> dict:
        """
        Convert this HiveInspection object back into a dictionary.

        ARGUMENTS:
        None. This instance method uses the data stored in the object.

        RETURNS:
        A dictionary containing the inspection fields and risk information.
        """

        return {
            "hive_id": self.hive_id,
            "inspection_date": self.inspection_date,
            "temp_f": self.temp_f,
            "weight_lb": self.weight_lb,
            "mites": self.mites,
            "queen_seen": self.queen_seen,
            "notes": self.notes,
            "risk_score": self.risk_score,
            "risk_reasons": self.risk_reasons
        }

# Helper function for HiveSummary class
def convert_risk_label(score: int) -> str:
    """
    Convert a maximum risk score into its required risk label.

    ARGUMENTS:
    score: An integer representing the maximum risk score for a hive.
        Scores from 0 through 2 are considered low risk, scores from 3
        through 5 are considered review risk, and scores of 6 or higher
        are considered urgent risk.

    RETURNS:
    A string containing the appropriate risk label: "low", "review", or
    "urgent".
    """

    # ERROR HANDLING: checks if score is type int.
    # If not, raises a TypeError.
    if not isinstance(score, int):
        raise TypeError("score must be an integer")

    # ERROR HANDLING: checks if score is negative.
    # If it is, raises a ValueError.
    if score < 0:
        raise ValueError("score cannot be negative")

    if score <= 2:
        return "low"

    if score <= 5:
        return "review"

    return "urgent"

# HiveSummary class creation

class HiveSummary:
    """
    Represents a summary of inspections for one hive.

    A separate summary class makes sense because an individual inspection and
    an entire hive summary represent different types of data. HiveInspection
    stores information about one inspection, while HiveSummary stores
    information calculated across multiple inspections.

    Instance methods are used to create and retrieve summary information for
    a particular hive. The static method is used for calculating an average
    without depending on a particular HiveSummary object.

    This class is used in the function summarize_hive.
    """

    def __init__(self, records: list[dict], hive_id: str):
        """
        Initialize a HiveSummary object.

        ARGUMENTS:
        records: A list of risk-scored inspection dictionaries.
        hive_id: A string containing the ID of the hive to summarize.
        """

        self.hive_id = hive_id
        self.records = sorted(
            [
                record
                for record in records
                if record.get("hive_id") == hive_id
            ],
            key=lambda record: record["inspection_date"]
        )

    @staticmethod
    def calculate_average(values: list[float]) -> float | None:
        """
        Calculate an average while ignoring missing values.

        ARGUMENTS:
        values: A list of numeric values that may contain None values.

        RETURNS:
        The average of the available numeric values, or None if there are
        no available values.
        """

        valid_values = [
            value for value in values
            if value is not None
        ]

        if not valid_values:
            return None

        return sum(valid_values) / len(valid_values)

    def get_risk_label(self) -> str | None:
        """
        Determine the risk label based on the maximum risk score.

        ARGUMENTS:
        None. This instance method uses the records stored in the object.

        RETURNS:
        "low" for scores 0 through 2, "review" for scores 3 through 5,
        and "urgent" for scores of 6 or greater.

        Returns None if the hive has no records.
        """

        if not self.records:
            return None

        maximum_risk = max(
            record.get("risk_score", 0)
            for record in self.records
        )

        return convert_risk_label(maximum_risk)

    def to_dict(self) -> dict | None:
        """
        Create a summary dictionary for the hive.

        ARGUMENTS:
        None. This instance method uses the records stored in the object.

        RETURNS:
        A dictionary containing inspection_count, first_date, last_date,
        average_temp, latest_weight, total_mites, maximum_risk, and
        risk_label.

        Returns None if the hive has no records.
        """

        if not self.records:
            return None

        maximum_risk = max(
            record.get("risk_score", 0)
            for record in self.records
        )

        temperatures = [
            record.get("temp_f")
            for record in self.records
        ]

        return {
            "inspection_count": len(self.records),
            "first_date": self.records[0]["inspection_date"],
            "last_date": self.records[-1]["inspection_date"],
            "average_temp": self.calculate_average(temperatures),
            "latest_weight": self.records[-1]["weight_lb"],
            "total_mites": sum(
                record["mites"] for record in self.records
            ),
            "maximum_risk": maximum_risk,
            "risk_label": self.get_risk_label()
        }

def add_risk_fields(records: list[dict]) -> list[dict]:
    """
    Add risk information to copies of cleaned inspection records.

    ARGUMENTS:
    records: A list of cleaned inspection dictionaries.

    RETURNS:
    A new list of dictionaries containing the original inspection fields plus
    risk_score and risk_reasons. The original records are not modified.
    """

    inspections = [
        HiveInspection.from_dict(record)
        for record in records
    ]

    # Sort chronologically within each hive.
    inspections.sort(
        key=lambda inspection: (
            inspection.hive_id,
            inspection.inspection_date
        )
    )

    previous_weights = {}

    for inspection in inspections:
        previous_weight = previous_weights.get(inspection.hive_id)

        inspection.calculate_risk(previous_weight)

        # Only a non-missing weight becomes the previous valid weight.
        if inspection.weight_lb is not None:
            previous_weights[inspection.hive_id] = inspection.weight_lb

    return [
        inspection.to_dict()
        for inspection in inspections
    ]


cleaned_records, rejected_records = clean_records(RAW_INSPECTIONS)

risk_records = add_risk_fields(cleaned_records)

# QUESTION 1: Boundary tests for risk scoring

# Boundary Test 1: Mites exactly equal to 8.
# This should receive 3 points because the rule is "8 or greater."
mites_boundary = HiveInspection(
    hive_id="H-TEST",
    inspection_date=date(2026, 8, 1),
    temp_f=75.0,
    weight_lb=150.0,
    mites=8,
    queen_seen=True,
    notes=""
)

print(
    "BOUNDARY TEST 1 - mites = 8:",
    mites_boundary.calculate_risk()
)


# Boundary Test 2: Weight decreases by exactly 10 pounds.
# This should receive 2 points because the rule is "at least 10 pounds."
weight_boundary = HiveInspection(
    hive_id="H-TEST",
    inspection_date=date(2026, 8, 2),
    temp_f=75.0,
    weight_lb=140.0,
    mites=0,
    queen_seen=True,
    notes=""
)

print(
    "BOUNDARY TEST 2 - exactly 10 lb weight loss:",
    weight_boundary.calculate_risk(previous_weight=150.0)
)


# Boundary Test 3: Temperature exactly equal to 95.
# This should receive 0 temperature points because the rule is
# "below 55 or above 95." Temp of 95 is within range.
temperature_boundary = HiveInspection(
    hive_id="H-TEST",
    inspection_date=date(2026, 8, 3),
    temp_f=95.0,
    weight_lb=150.0,
    mites=0,
    queen_seen=True,
    notes=""
)

print(
    "BOUNDARY TEST 3 - temperature = 95:",
    temperature_boundary.calculate_risk()
)

# QUESTION 4: HiveInspection method tests
print("\nQUESTION 4: Class tests")
print("\nHiveInspection class method tests")
test_inspection = HiveInspection.from_dict(cleaned_records[0])

print("\nClass method - created inspection:")
print(test_inspection.hive_id)
print(test_inspection.inspection_date)
print(test_inspection.weight_lb)

# Instance method test for HiveInspection class
test_score, test_reasons = test_inspection.calculate_risk()

print("\nInstance method - risk calculation:")
print("Risk score:", test_score)
print("Risk reasons:", test_reasons)

# Static method test for HiveInspection class

print(
    "Static method - valid mite count:",
    HiveInspection.valid_mite_count(8)
)

print(
    "Static method - invalid mite count:",
    HiveInspection.valid_mite_count(-1)
)

# QUESTION 4: HiveSummary method tests

print("\nHiveSummary class method tests")

# STATIC METHOD TEST
# Tests calculate_average() with valid numeric values and a missing value.
# The None value should be ignored when calculating the average.
average_test = HiveSummary.calculate_average([70.0, 80.0, None, 90.0])

print(
    "Static method - calculate_average([70, 80, None, 90]):",
    average_test
)

# INSTANCE METHOD TEST
# Creates a HiveSummary object for H-01 using the risk-scored records.
# The records do not need to be supplied in chronological order because
# HiveSummary sorts its own copy.
summary_test = HiveSummary(risk_records[::-1], "H-01")

print(
    "Instance method - get_risk_label():",
    summary_test.get_risk_label()
)

# Assignment 6, Question 2:

# Some helper functions first.
def get_hive_records(records: list[dict], hive_id: str) -> list[dict]:
    """
    Return records belonging to one hive.

   ARGUMENTS:
    records: A list of inspection dictionaries. Each dictionary should contain
    a "hive_id" field identifying the hive associated with the inspection.
    
    hive_id: A string containing the ID of the hive whose inspection records
    should be returned.

    RETURNS:
    A list containing only the inspection records for the requested hive.
    Hive IDs are compared after stripping whitespace and converting them to
    uppercase. If hive_id is not a string, an empty list is returned.
    """

    if not isinstance(hive_id, str):
        return []

    normalized_hive_id = hive_id.strip().upper()

    return [
        record
        for record in records
        if record.get("hive_id") == normalized_hive_id
    ]


def average_temperature(records: list[dict]) -> float | None:
    """
    Calculate the average temperature while ignoring missing values.

    ARGUMENTS:
    records: A list of inspection dictionaries. Each dictionary may contain
        a "temp_f" field containing a numeric temperature value or None.
        Missing temperature values are ignored when calculating the average.

    RETURNS:
    The average temperature as a float. Returns None if there are no
    available temperature values in the records.
    """

    temperatures = [
        record["temp_f"]
        for record in records
        if record.get("temp_f") is not None
    ]

    if not temperatures:
        return None

    return sum(temperatures) / len(temperatures)

# Main function for Question 2
def summarize_hive(records: list[dict], hive_id: str) -> dict | None:
    """
    Create a summary of all risk-scored inspections for one hive.

    ARGUMENTS:
    records: A list of risk-scored inspection dictionaries.
    hive_id: A string containing the ID of the hive whose inspections
        should be summarized.

    RETURNS:
    A dictionary containing inspection_count, first_date, last_date,
    average_temp, latest_weight, total_mites, maximum_risk, and risk_label.

    Returns None if the requested hive has no records.
    """

    if not isinstance(records, list):
        raise TypeError("records must be a list")

    if not isinstance(hive_id, str):
        raise TypeError("hive_id must be a string")

    summary = HiveSummary(records, hive_id)

    return summary.to_dict()

hive_ids = sorted({record["hive_id"] for record in risk_records})

# Reversing the list of records to show it doesn't need to be sorted.
reversed_risk_records = list(reversed(risk_records))

print("\nH-01 summary using reversed input:")
print(summarize_hive(reversed_risk_records, "H-01"))

# Compares original and reversed summaries.
original_summary = summarize_hive(risk_records, "H-01")
reversed_summary = summarize_hive(reversed_risk_records, "H-01")

if original_summary == reversed_summary:
    print("TEST: Summary is independent of input order.")
else:
    print("TEST FAILED: Summary changed when input order changed.")

# Testing empty hive, returns None:
print("\nEmpty hive test:")
print(summarize_hive(risk_records, "H-99"))

# Testing missing temp:
print("\nH-03 summary:")
print(summarize_hive(risk_records, "H-03"))

# Test that average temp only uses the inspection where temp is present
h03_summary = summarize_hive(risk_records, "H-03")

print(
    "H-03 average temperature:",
    h03_summary["average_temp"]
)

# Testing risk-label boundaries
print("\nRisk label boundary tests:")

print("Score 0:", convert_risk_label(0))
print("Score 2:", convert_risk_label(2))
print("Score 3:", convert_risk_label(3))
print("Score 5:", convert_risk_label(5))
print("Score 6:", convert_risk_label(6))

#=============ASSIGNMENT 7 CODE==========================

df = pd.DataFrame(risk_records)

df['inspection_date'] = pd.to_datetime(df['inspection_date'])

# These assert statements ensure the total rows, unique hive IDs, and total mites match.
assert len(risk_records) == len(df), "Rows not equal"
unique_hive_ids = len({id['hive_id'] for id in risk_records})
# Gen AI used to learn about the nunique function in pandas, which counts unique values.
assert unique_hive_ids == df['hive_id'].nunique(), "Unique Hive IDs don't match"
all_mites = sum(id['mites'] for id in risk_records)
assert all_mites == df['mites'].sum(), "Total mites not equal"
# Adds column needs_attention for risk score greater than/equal to 3
df["needs_attention"] = df["risk_score"] >= 3

print("\n==========ASSIGNMENT 7 OUTPUT:==========")
# Displays dtypes per assignment instructions
print("\nBelow are the dtypes of each column in the DataFrame:")
print(df.dtypes)

print("\nBelow are the total missing values in each column of the DataFrame:")
# This counts missing values in a way that includes blank strings and lists, since df.isna only
# includes None values. Gen AI was used to learn how to use lambda to make an unnamed function
# that takes x as input and checks to see if it's a list.
for column in df.columns:
    missing = df[column].isna().sum() # Counts None values.
    blanks = (df[column] == '').sum() # Counts empty strings.
    empty_lists = df[column].apply(lambda x: isinstance(x, list) and len(x) == 0).sum()

    print(f"{column}: {missing+blanks+empty_lists}") # Prints total missing values.

# Exports df to csv for inspection
df.to_csv("clean_records_df.csv", index=False)

# This creates a filtered version of the dataframe that only includes rows needing attention
needs_attention_df = df[df["needs_attention"] == True]
needs_attention_df = needs_attention_df.drop(columns = ["temp_f", "weight_lb", "queen_seen", "notes", "needs_attention"])
# Exports needs_attention_df to csv for inspection
needs_attention_df.to_csv("needs_attention_df.csv", index=False)

def weight_change(frame: pd.DataFrame) -> pd.DataFrame:
    """
    This creates a DataFrame that shows hive weight changes over time.

    frame: DataFrame created earlier from the output of the add_risk_fields (which takes the output of clean_records as input).

    returns: a DataFrame with a column summarizing weight change over time.
    """
    # Sorts by date and then hive_id in case the input df is not already sorted.
    wgt_change = frame.sort_values(by = "inspection_date", ascending = True)
    wgt_change = wgt_change.sort_values(by = "hive_id", ascending = True)
    # This groups by hive_id to ensure changes between hives aren't calculated.
    # Gen AI was used to learn about using lambda to make small, unnamed functions. This one drops
    # missing values, calculates differences, and then reindexes the results in the proper order.
    wgt_change["wgt_incr_decr"] = (wgt_change.groupby("hive_id")["weight_lb"].transform(lambda s: s.dropna().diff().reindex(s.index)))
    # Drops unneeded columns for easier viewing
    wgt_change = wgt_change.drop(columns = ["temp_f", "mites", "queen_seen", "notes", "risk_score", "risk_reasons", "needs_attention"])

    return wgt_change

# This runs the weight_change function with cleaned records and exports to a csv for viewing
changes_in_wgt = weight_change(df)
changes_in_wgt.to_csv("changes_in_wgt.csv", index=False)

def monthly_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """
    This creates a DataFrame that shows inspection summaries by month and year

    frame: DataFrame created earlier from the output of the add_risk_fields (which takes the output of clean_records as input).

    returns: a DataFrame with inspections summarized by month and year.
    """
    monthly = frame.copy()
    # StackOverflow used to learn to use pandas datetime tools to group by months.
    monthly["month"] = monthly["inspection_date"].dt.to_period("M")
    monthly = (
        monthly.groupby("month")
            # Gen AI used to learn how to use .agg to aggregate multiple columns at once
            # when using groupby.
        .agg(
            avg_temp=("temp_f", "mean"),
            avg_weight=("weight_lb", "mean"),
            avg_mites=("mites", "mean"),
            avg_risk=("risk_score", "mean"),
            attention_rate=("needs_attention", "mean")
            # The mean of needs_attention indicates the % of records needing attention
        )
    ) # As mentioned prior, gen ai used to learn about lambda
    monthly["attention_rate"] = (monthly["attention_rate"].map(lambda x: f"{x:.2%}"))

    return monthly

print(f"\nBelow is the summary of inspection results by month:\n{monthly_summary(df)}")
