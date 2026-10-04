## NOTE:
Originally, calculate_risk was its own standalone function, but when I added the HiveInspection class,
I decided it made more sense to include it in there. But it still functions the way described here!

## PSEUDOCODE FOR CALCULATE_RISK

DEFINE named constants for all risk thresholds and point values

mites_risk_threshold = 8
mites_risk_pts = 3

queen_risk_pts = 2

wgt_loss_threshold = 10
wgt_loss_pts = 2

low_temp_threshold = 55
high_temp_threshold = 95
temp_risk_pts = 1


FUNCTION calculate_risk(self, previous_weight: float or None) -> Tuple [Int, List[str]]:
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

    SET score to 0
    SET reasons to an empty list

    IF mites is greater than or equal to the mite threshold:
        ADD mite points to score
        ADD a mite-related reason to reasons

    IF queen_seen is False:
        ADD queen points to score
        ADD a queen-related reason to reasons

    IF previous_weight exists AND current weight exists:
        CALCULATE weight loss as previous_weight minus current weight

        IF weight loss is greater than or equal to the weight-loss threshold:
            ADD weight points to score
            ADD a weight-related reason to reasons
    ELSE:
        Do not add any weight-change points
        # No previous weight or missing current weight earns no weight change points.

    IF temperature is below the low-temperature threshold
       OR temperature is above the high-temperature threshold:
        ADD temperature points to score
        ADD a temperature-related reason to reasons

    RETURN Tuple containing score and reasons

## PSEUDOCODE FOR ADD_RISK_FIELDS
The doc string below explains what this function does. Since it's related to the risk calculation,
I decided to include its pseudocode here as well, largely for practice.

FUNCTION add_risk_fields(records: list[dict]) -> list[dict]:
    """
    Add risk_score and risk_reasons to copies of cleaned inspection records.
    Records are sorted chronologically within each hive before risk is
    calculated. The original records are not modified.
    The previous weight is tracked separately for each hive. Only a non-missing
    current weight becomes the previous valid weight for the next inspection.

    ARGUMENTS:
    records: list of dictionaries. These are the cleaned records from clean_records.

    RETURNS:
    A new list of dictionaries containing the original fields plus
    risk_score and risk_reasons.
    """
    Make copies of all records so the clean records are not modified.

    Sort the copies by hive_id and inspection_date.

    SET previous_weight for each hive to no previous weight.

    FOR each record in chronological order:
        Get the previous valid weight for that hive.

        Calculate the risk score and reasons using calculate_risk.

        Add risk_score and risk_reasons to the copied record.

        IF the current weight is not missing:
            Make the current weight the previous valid weight for that hive.

    RETURN the copied records in chronological order within each hive.