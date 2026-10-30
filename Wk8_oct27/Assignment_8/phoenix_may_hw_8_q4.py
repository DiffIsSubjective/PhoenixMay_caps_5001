"""
Describe the dataset:
This dataset contains observations related to concrete compressive strength. According
to the author, "concrete is the most important material in civil engineering," and so
understanding variables that contribute to its strength is critical to those in the field.

This dataset contains 8 input variables (cement, blast furnace slag, fly ash, water,
superplasticizer, coarse aggregate, fine aggregate, and age. age is measured in days
and the rest in kg per m^3) and 1 output variable (compressive stength, measured in
megapascals). It has 1030 rows of data and no missing values.
"""

import pandas as pd
import numpy as np
# Gen AI used to ensure all columns get shown
pd.set_option('display.max_columns', None)

# Load file into dataframe
# File was originally a 97-2003 XLS file, but I converted it to a CSV. I
# exported the dataframe to its own CSV and compared it to the original
# XLS to ensure no data was being lost.
concrete = pd.read_csv("Concrete_Data.csv")

# Renaming columns to something more concise
concrete = concrete.rename(columns={
    "Cement (component 1)(kg in a m^3 mixture)": "cement",
    "Blast Furnace Slag (component 2)(kg in a m^3 mixture)": "blast_furnace_slag",
    "Fly Ash (component 3)(kg in a m^3 mixture)": "fly_ash",
    "Water  (component 4)(kg in a m^3 mixture)": "water",
    "Superplasticizer (component 5)(kg in a m^3 mixture)": "superplasticizer",
    "Coarse Aggregate  (component 6)(kg in a m^3 mixture)": "coarse_agg",
    "Fine Aggregate (component 7)(kg in a m^3 mixture)": "fine_agg",
    "Age (day)": "age",
    "Concrete compressive strength(MPa, megapascals) ": "strength"
    })

# This code calculates sample std dev and var, which is the default in pandas.
# I checked the results by calculating it manually in Excel. Sample makes more
# sense because this dataset is not for every piece of concrete in the world,
# just a sample of 1030.
summary_concrete = concrete.agg({
    col: [
        "mean",
        "median",
        # Gen AI used for this. Convert all modes to strings and join them with a comma
        # Just using "mode" returns a series, which causes a TypeError
        lambda x: ", ".join(x.mode().astype(str)) if not x.mode().empty else "None",
        "std", 
        "var"
    ]
    for col in concrete.columns
})

# Renaming lambda row to mode
summary_concrete.index = ["Mean", "Median", "Mode", "Std Dev", "Variance"]
print(summary_concrete)

# I decided to do the covariance and correlation coefficient between the age
# and strength columns. I wanted to see if, ignoring other factors, there's
# a significant relationship between concrete's age and its strength, and
# if strength increases or decreases over time.

# Covariance of age and strength is 347.060. This shows the relationship
# is positive. However, the exact value doesn't mean much, since covariance
# is not scaled and can be anywhere from positive to negative infinity.
print("\nCovariance between Age and Strength:")
print(np.cov(concrete["age"], concrete["strength"]))
# The correlation coefficient between age and strength is 0.329. This
# means there is a positive but weak correlation.
# From this, it looks like strength generally goes up over time, but
# age is not a good predictor of strength on its own.
print("\nCorrelation coefficient between Age and Strength:")
print(np.corrcoef(concrete["age"], concrete["strength"]))


#Takeaway findings:
#One thing I've noticed is that it's tricky to work with data where you're
#unfamiliar with the units. I wasn't an engineering student, so measuring
#things in kg per cubic meter is foreign to me, but according to Google
#this is the standard way to measure density.

#Most of the variables in this dataset have a lot of variability. For example,
#Blast Furnace Slag, Fly Ash, Superplasticizer, and Age all have standard deviations
#close to or greater than their mean values. This gives us a wider range of
#circumstances to analyze, which is nice, but this much variability runs the risk
#of introducing random noise that can seem like patterns.

#As mentioned above, age and strength have a positive relationship, but it's
#pretty weak at a 32.9% correlation coefficient. So concrete generally gets
#stronger over time, but it is not a great predictor on its own. The author
#of the dataset said the strength of concrete is a "highly nonlinear function
#of age and ingredients," which checks out. It will take more complex measures
#to make a model that can predict strength more accurately.

# Export to CSV for visual inspection if desired
concrete.to_csv("concrete_df.csv", index=False)
