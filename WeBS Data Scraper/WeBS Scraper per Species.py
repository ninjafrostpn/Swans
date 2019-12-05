# Script First Worked on: 2019-11-20
# By: Charles S Turvey
# With huge thanks to BitBait for pointing out requests and BeautifulSoup!

from bs4 import BeautifulSoup
import csv
import json
import numpy as np
import os
import pandas as pd
import re
import requests
import time

# Urls to the data portal and to the mute swan species page
webs_url = "https://app.bto.org/webs-reporting/"
iddatarequest = webs_url + "NumbersUniqueSpecies?reported_year=2017&selected_species="

# The names of the requests for rows of data
# SpecLocReport will only return up to the first 120 lines, but must be requested before Pasteriser will return
# anything, since it gets the session's cookies
requestnames = ["SpecLocReport", "Pasteriser"]

# The request template (all one string lines are one string, just formatted in unusual python {source 0})
# (Request format discovered using the Networks tab of the Chrome analysis window; thanks BitBait!)
template = (
    # The website
    "https://app.bto.org/webs-reporting/"

    # The first year of the desired WeBS report edition (2005 up to 2017, we're using 17/18 so 2017)
    # (Years later than 2017 default to 2017 (writing this in Dec 2019), earlier than 2005 fail)
    "{}?reported_year=2017"

    # The first table row index to collect...
    "&start_at={:d}"

    # ... and the number of rows to get starting from this, inclusive
    # (Request appears to only return data from rows 0-120; any range outside of these returns nothing)
    "&go_on_for={:d}"

    # Whether or not to include supplementary data (presumably can be y or n)
    "&inc_supps=y"

    # For location selection, the ID corresponding to the location selected
    # e.g. "LOC648397" for the "Severn Estuary" location page
    # Must be "" for species selection
    "&loc_id="

    # For location selection, where the location is (argument omitted in species searches):
    # "GB" for Great Britain
    # "NI" for Northern Ireland
    # (Others may exist, but doesn't seem to mind omission anyway)
    # "&reg_label=GB"

    # For species selection, the ID  corresponding to the species selected
    # e.g. "46" for the "Mute Swan" page
    # Must be "" for location selection
    "&species_code={:d}"

    # For location pages, the group of birds to filter by:
    # "" for all (must be set to this for species pages)
    # "WIL" for Wildfowl (Like Ducks, Geese, Swans...)
    # "WAD" for Waders (As in shoreline wading birds)
    # "GUL" for Gulls
    # "TER" for Terns
    # "OTH" for Others (Like Kingfishers, Coot, Moorhen, Heron, Cormorant...)
    "&birdy="

    # For location pages, whether to sort by taxon (y or n, but must be n for species pages)
    "&taxonsort=n"

    # For species pages, the region to filter by:
    # (the "-" in -1, -2, -3 or -4 may also be replaced with 0 indexed values to get specific regions)
    # "0" for all (must be set to this for location pages)
    # "-1" for English counties
    # "-2" for Welsh counties
    # "-3" for Scottish counties
    # "-4" for Northern Irish Counties
    # "-5" for the Isle of Man
    # "-6" for the Channel Islands
    # "-7" for Offshore counties
    "&area=0"

    # For species pages, the type of habitat to filter by:
    # "0" for all (must be set to this for location pages)
    # "1" for natural inland still water
    # "2" for reservoir
    # "3" for gravel pit
    # "4" for river or marsh
    # "5" for open coast
    # "6" for estuarine
    # "7" for goose or swan 'fields'
    # "8" for unknown
    "&habicat=0"

    # Looks like a "cachebusting" parameter; ensures that each request distinct to avoid being served old data?
    # This one appears to be made up of the time since the epoch to 3 D.P. at the first open of the page
    # to which one is added each time a new request is made {discovered thanks to source 3}
    "&_={:d}"
)


def birdtablegetter(speciescode, startrow=0, rows=100, mode=1):
    timestamp = int(time.time() * 1000)
    requesttext = template.format(requestnames[mode], startrow, rows, speciescode, timestamp)
    r = s.get(requesttext)
    # Proceeds if the request succeeded
    if r.status_code == 200:
        return json.loads(r.text)


# Start a web session, so that cookies will persist between data requests
print("Opening session...")
s = requests.Session()
print(" - Session opened.")

# Create the directory for the population tables to go into, if it doesn't already exist
try:
    print("Creating 'BirdCSVs' directory...")
    os.mkdir("BirdCSVs")
    print(" - Created 'BirdCSVs' directory.")
except FileExistsError:
    print(" - There already exists a 'BirdCSVs' directory.")


try:
    print("Extracting bird name list...")
    # Get the full list of bird species/subspecies/variants from the site
    # or from a file that was saved as a copy of this earlier
    try:
        print(" - Checking for 'birdnames.csv'...")
        # Try to create a birdnames file
        birdiddatafile = open("birdnames.csv", "x", encoding="utf-8", newline="")
        print(" -  - Created new 'birdnames.csv'.")
        # If a success, that means none existed yet
        # TODO: Variable needs a better name
        iddataoverwritepolicy = "o"
    except FileExistsError:
        print(" -  - Found old 'birdnames.csv'...")
        # If there already exists a file with the names in, give the option to use it
        iddataoverwritepolicy = input("\nUse this file?\n"
                                      " - Enter to proceed with this name list,\n"
                                      " - o then Enter to overwrite it.\n"
                                      ">>> ").lower()
        if iddataoverwritepolicy == "o":
            # Overwrite the old file with a blank new one
            birdiddatafile = open("birdnames.csv", "w", encoding="utf-8", newline="")
            print(" -  - Old 'birdnames.csv' overwritten.")
    # Write to the bird name/id/etc file if necessary
    if iddataoverwritepolicy == "o":
        # Get the contents of the bird name dropdown
        iddatahtml = s.get(iddatarequest).text
        iddatahtml = "".join(iddatahtml.split("\\"))
        iddatasoup = BeautifulSoup(iddatahtml)
        # Extract bird names and species ids from it
        print(" - Processing name data...")
        birdiddata = [[o.string, int(o["value"]), o["data-taxon"],
                       o["data-reg"], o["data-migratoriness"], o["data-ranginess"]]
                      for o in iddatasoup.find_all("option")[1:]]
        print(" -  - Writing site names to 'birdnames.csv'...")
        # Save these to the file for later use
        birdnameswriter = csv.writer(birdiddatafile)
        birdnameswriter.writerow(["Name", "ID", "Binomial", "IsSummerMigrant", "MigrantStatus", "Range"])
        for row in birdiddata:
            print(row)
            birdnameswriter.writerow(row)
    else:
        # Otherwise read the names from a previously saved file
        birdiddatafile = open("birdnames.csv", "r", encoding="utf-8", newline="")
        birdiddata = [row for row in csv.reader(birdiddatafile)]
    # Always sure to close the file afterwards (Although python would probably clean up otherwise anyway)
    birdiddatafile.close()
    birdiddata = np.object_(birdiddata[1:])
    print(birdiddata)
    birdnames = birdiddata[:, 0]
    print(" -  - Bird names etc ready.\n\n", birdnames, "\n - Bird names etc extracted.")

    while True:
        # Take input of regex to match a set of bird names whose tables to download
        birdname = input("\nEnter bird name or regex pattern, case insensitive\n>>> ")
        print("Finding bird name matches...")
        matcher = re.compile(birdname, re.IGNORECASE)
        chosenbirdnames = list(filter(matcher.search, birdnames))
        if len(chosenbirdnames) == 0:
            print(" - No bird name matches found.")
            # Simply go back and ask again if none match the request
            continue
        print(" - Bird name matches found ({}).\n\n".format(len(chosenbirdnames)), "\n".join(chosenbirdnames), sep="")
        # Confirm selection before moving on
        iddataoverwritepolicy = input("\nUse these birds?\n"
                                      " - Enter to proceed with extracting data for these birds,\n"
                                      " - n then Enter to try a different search.\n"
                                      ">>> ")
        if iddataoverwritepolicy == "n":
            # Return to asking for a new selection if selection not confirmed
            continue

        chosenmask = np.isin(birdnames, chosenbirdnames)
        chosenbirdiddata = birdiddata[chosenmask]
        # Go through each bird name in the selection and download the relevant table
        overwritepolicy = ""
        for birdname, birdid, _, birdsummig in chosenbirdiddata[:, :4]:
            # Initialise the session
            birdtablegetter(int(birdid), rows=1, mode=0)
            print("\nExtracting data table for {} [{}]...".format(birdname, time.strftime("%H:%M:%S")))
            # Prevent issues with file name misinterpretation as folder/file by replacing all /s with -s
            birdfilename = "-".join(birdname.split("/"))
            try:
                print(" - Creating '{}.csv'...".format(birdfilename))
                # Try to create a csv to save the data to
                birdfile = open("BirdCSVs//{}.csv".format(birdfilename), "x", encoding="utf-8", newline="")
            except FileExistsError:
                print(" -  - Found old '{}.csv'...".format(birdfilename))
                # If it failed, then one already exists
                # Therefore treat according to overwrite policy already set, or ask for a choice on that matter
                if overwritepolicy not in ["a", "x"]:
                    overwritepolicy = input("\nKeep this file?\n"
                                            " - Enter to keep the old file,\n"
                                            " - a then Enter to keep all,\n"
                                            " - o then Enter to overwrite it,\n"
                                            " - x then Enter to overwrite all.\n"
                                            ">>> ").lower()
                if overwritepolicy.lower() in ["o", "x"]:
                    print(" -  - Overwriting old '{}.csv'...".format(birdfilename))
                    # Overwrite existing csv with blank file
                    birdfile = open("BirdCSVs//{}.csv".format(birdfilename), "w", encoding="utf-8", newline="")
                    print(" -  - Old '{}.csv' overwritten.".format(birdfilename))
                else:
                    print(" -  - Old '{}.csv' kept.\n - Table extraction skipped.".format(birdfilename))
                    # Skip forward to next bird name if this csv kept
                    continue
            # Initialise interface for easily writing to the csv file
            birdwriter = csv.writer(birdfile)
            # Initialise the DataFrame
            birdtabledata = pd.DataFrame({"Site": [], **{str(i): [] for i in range(1947, 2018)}})
            # Gets the current GMT time in a neat format
            accesstime = time.strftime("%Y-%m-%d %H:%M:%S")
            # Obtain the raw data from servers
            # (10000 rows requested since total no of sites is an order of magnitude lower; definitely gets all of them)
            print(" - Requesting raw data [{}]...".format(accesstime))
            birdtableraw = birdtablegetter(int(birdid), 0, 10000)
            print(" -  - Raw data obtained [{}].".format(time.strftime("%Y-%m-%d %H:%M:%S")))
            # Process the data into the DataFrame
            print(" - Converting raw data to DataFrame [{}]...".format(time.strftime("%Y-%m-%d %H:%M:%S")))
            n = len(birdtableraw)
            for i, row in enumerate(birdtableraw):
                print(" -  - Converting site {} of {} [{}]...".format(i, n, time.strftime("%Y-%m-%d %H:%M:%S")))
                # Input data to dataframe:
                #   Site gives the name of the recording site (oddly enough)
                #   Columns headed with calendar years have items which are each a four-part array:
                #       [Population record (during month of WeBS year where highest numbers were recorded),
                #        Count completeness (?): 1 for "complete" count, 2 for "incomplete",
                #        Month of year where this population record was taken (or "" when population record is 0),
                #        Count supplementariness: 0 for Core counts, 1 for supplementary counts,
                #        The name of the supplementary count scheme,
                #        The name of the group from which the supplementary count came]
                #       (The array can also be replaced by a nan, where pandas fills in the blanks in a site's row)
                # TODO: Have it separate out the components of each array representing a data point
                birdtabledata = birdtabledata.append({"Site": row["siteName"], **row["allYears"]}, ignore_index=True)
            # Add column for time of access as metadata alongside the population data
            birdtabledata = birdtabledata.assign(RoughTimeAccessed=accesstime)
            # Convert calendar year column names to WeBS years (No overlap in abbreviation for another 30yr yet)
            # (But don't do this for Summer Migrants, since the calendar year is used for these)
            if birdsummig != "y":
                birdtabledata = birdtabledata.rename(columns={str(i): "{:02d}/{:02d}".format(i % 100, (i + 1) % 100)
                                                              for i in range(1947, 2018)})
            print(" -  - DataFrame complete [{}].".format(time.strftime("%Y-%m-%d %H:%M:%S")))
            print(birdtabledata.columns)
            # Write the data to the csv file
            print(" - Writing data to file [{}]...".format(time.strftime("%Y-%m-%d %H:%M:%S")))
            birdwriter.writerow(birdtabledata.columns)
            birdwriter.writerows(np.object_(birdtabledata))
            print(" -  - Data written to file [{}].".format(time.strftime("%Y-%m-%d %H:%M:%S")))
            # Close the csv file, now that nothing more need be written to it
            birdfile.close()
            print(" - Data table extracted.\n\n", birdtabledata, "\n")
finally:
    # Shut the session if there is some kind of error or the script terminates
    print("Closing session...")
    s.close()
    print(" - Session closed.")

"""
Handy Webpages
--------------------------
https://docs.python.org/3/tutorial/errors.html
https://selenium.dev/selenium/docs/api/py/api.html
https://www.w3schools.com/xml/xpath_syntax.asp
https://stackoverflow.com/questions/25062365/python-parsing-html-table-generated-by-javascript
https://www.bto.org/our-science/projects/wetland-bird-survey/publications/webs-annual-report/online-reports
https://www.bto.org/sites/default/files/webs_methods.pdf
https://app.bto.org/webs-reporting/?tab=numbers&locid=LOC648397
https://stackoverflow.com/questions/29807856/selenium-python-how-to-get-texthtml-source-from-div#comment47745057_29808188
https://stackoverflow.com/questions/35573625/getting-current-select-value-from-drop-down-menu-with-python-selenium
https://docs.python.org/3/library/functions.html?highlight=open#open
https://docs.python.org/3/tutorial/controlflow.html
https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html
https://stackoverflow.com/questions/3640359/regular-expressions-search-in-list
https://www.techbeamers.com/handle-alert-popup-selenium-python/
https://stackoverflow.com/questions/12555323/adding-new-column-to-existing-dataframe-in-python-pandas
https://www.gobirding.eu/Photos/Swoose.php
https://www.gobirding.eu/Photos/HybridGeese.php
https://2.python-requests.org//en/v1.1.0/api/#module-requests
https://stackoverflow.com/a/17630918
https://benbernardblog.com/web-scraping-and-crawling-are-perfectly-legal-right/
https://bto.org/robots.txt
https://stackoverflow.com/a/3687765
https://www.bto.org/our-science/projects/wetland-bird-survey
https://beautiful-soup-4.readthedocs.io/en/latest/#quick-start
"""
