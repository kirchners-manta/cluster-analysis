### Script for the modified CSDF formalism

# This script shall be applied to a CSDF file, usually named "cluster_significance_df.csv"
# It requires the files "cluster_distance_df.csv" and  "cluster_polymer_df.csv" to be located in the same directory
# Syntax: python3 csdf_formalism.py <csdf_file>

###############################################################################
# module imports
import numpy as np
import pandas as pd
import sys
import os
from pathlib import Path

# read in CSDF path from command line
csdf_file = sys.argv[1]

# define the path to the CDDF and CPDF files from CSDF
cddf_file = str(Path(csdf_file).parent) + "/cluster_distance_df.csv"
cpdf_file = str(Path(csdf_file).parent) + "/cluster_polymer_df.csv"

# read in the files as dataframes
csdf = pd.read_csv(csdf_file, sep=";")
cddf = pd.read_csv(cddf_file, sep=";")
cpdf = pd.read_csv(cpdf_file, sep=";")

# define the threshhold for finding the integration borders
# the lower integration border is defined as the leftmost distance, where the CDDF reaches 1% of the maximum peak hight
# the upper integration border is defined as the rightmost distance, where the CDDF reaches 1% of the maximum peak hight
threshhold = 0.01 * np.max(cddf["  Occurrence"])

# find the minimum and maximum distance according to above deinition
min_dist = np.min(cddf["# Cutoff Distance / pm"][cddf["  Occurrence"] >= threshhold])
max_dist = np.max(cddf["# Cutoff Distance / pm"][cddf["  Occurrence"] >= threshhold])

# print the results (uncomment if not wanted)
print("Boundaries from CDDF in pm:", min_dist, " / ", max_dist)

# generate new data frame by integration of the CPDF with CDDF integration borders
# create an empty list
integ = []

# iterate over all columns beginning with the third column
for j, col in enumerate(cpdf.columns.to_list()[2:]):

    # sum up all values in column in range between min_dist and max_dist
    raw = np.sum(
        cpdf[col][
            (cpdf["# Cutoff Distance / pm"] >= min_dist)
            & (cpdf["# Cutoff Distance / pm"] <= max_dist)
        ]
    )

    # append data to the list
    integ.append([j + 1, raw])

# create new data frame from the list
csdf_from_cddf = pd.DataFrame(integ, columns=["# Cluster Size", "  Percentage"])

# rescale sum of CSDF values to 100 %
csdf_from_cddf["  Percentage"] = (
    csdf_from_cddf["  Percentage"] / np.sum(csdf_from_cddf["  Percentage"]) * 100
)

# export the data frame to a csv file
save_location = os.path.join(
    os.path.realpath("./"), str(Path(csdf_file).parent) + "csdf_from_cddf.csv"
)
csdf_from_cddf.to_csv(save_location, sep=";", index=False)
