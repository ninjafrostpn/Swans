# Script First Worked on: 2019-12-04
# By: Charles S Turvey

import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# List of the WeBS sites corresponding to the 9 WWT sites {using sources 0, 1}
centresitenames = ["Strangford Lough",      # WWT Castle Espie
                   "Solway Estuary",        # WWT Caerlaverock
                   "WWT Washington",        # WWT Washington
                   "WWT Martin Mere",       # WWT Martin Mere
                   "Burry Inlet",           # WWT Llanelli
                   "Severn Estuary",        # WWT Slimbridge
                   "Arun Valley",           # WWT Arundel
                   "London Wetland Centre"  # WWT London
                   "Ouse Washes"]           # WWT Welney


# Gets and processes population data from the csvs in the BirdCSVs folder
def getbirddata(birdname):
    # Read out the raw data from the csv corresponding to the bird name requested
    birdfilename = "-".join(birdname.split("/"))
    birdfile = open("../../WeBS Data Scraper/BirdCSVs/{}.csv".format(birdfilename))
    birdtable = np.object_([row for row in csv.reader(birdfile)])
    # Extract the population and location data from it
    birdloc = birdtable[1:, 0]
    birdpop = birdtable[1:, 1:-1]
    # Build a table representing the raw data
    birdtable = pd.DataFrame({birdtable[0, i]: birdtable[1:, i] for i in range(len(birdtable[0]))})
    # Iterate through all the strings representing
    for i, row in enumerate(birdpop):
        for j, val in enumerate(row):
            # Convert any string that says "nan" into an actual np.nan
            if val != "nan":
                # Convert any string representing an array into an array
                val = val[1:-1].split(", ")
                # Replace any incomplete counts with np.nan
                if val[1] != "2":
                    # And finally extract any complete counts
                    birdpop[i, j] = int(val[0])
                    continue
            birdpop[i, j] = np.nan
    birdpop = np.float32(birdpop)
    return birdtable, birdloc, birdpop


print(*getbirddata("Mute Swan"), sep="\n")

"""
0 https://www.wwt.org.uk/wetland-centres/
1 http://app.bto.org/websonline/sites/data/sites-data.jsp
"""
