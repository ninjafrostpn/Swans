# Script First Worked on: 2019-11-20
# By: Charles S Turvey

# TODO: Try to cut down on some of these dependencies...
import csv
import numpy as np
import os
import pandas as pd
from pandas.io.html import read_html
import re
from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
import time

# Further Requirements to be downloaded and added to system path:
# - Firefox browser (https://www.mozilla.org/en-GB/firefox/new/)
# - geckodriver (https://github.com/mozilla/geckodriver/releases)
# System may need restart after path variables have been updated


# Urls to the data portal and to the mute swan species page
webs_url = "https://app.bto.org/webs-reporting/"
muteswan_url = webs_url + "?tab=numbers&speciescode=46"

# Open an instance of Firefox, through which to obtain the data
print("Opening driver...")
driver = webdriver.Firefox()
print(" - Driver opened.")

# Create the directory for the population tables to go into, if it doesn't already exist
try:
    print("Creating 'BirdCSVs' directory...")
    os.mkdir("BirdCSVs")
    print(" - Created 'BirdCSVs' directory.")
except FileExistsError:
    print(" - There already exists a 'BirdCSVs' directory.")

# Open the mute swan page in the Firefox browser
try:
    print("Loading WeBS site...")
    driver.get(muteswan_url)
    # Wait until the table elements have loaded
    WebDriverWait(driver, 60).until(
        ec.presence_of_element_located((By.XPATH, '//table[@class="maintable"]'
                                                  '/tbody'
                                                  '/tr'
                                                  '/td'
                                                  '/div'
                                                  '/*'))
    )
    print(" - Site loaded.")

    print("Extracting bird name list...")
    # Get the elements for the bird species dropdown and its respective searchbox
    birdnamedropdown = driver.find_element_by_xpath('//div[@id="speciesFg"]'
                                                    '/div[contains(@class, "select2-container")]')
    birdnamedropdown.click()
    searchboxes = driver.find_elements_by_xpath('//input[contains(@class, "select2-input")]')
    birdsearchbox = None
    for searchbox in searchboxes:
        # Check that it's the visible searchbox (just made so by clicking on the dropdown list)
        if searchbox.is_displayed():
            birdsearchbox = searchbox
    # Clear any text in the searchbox, just in case
    birdsearchbox.clear()

    # Get the full list of bird species/subspecies/variants from the available dropdown list
    # or from a file that was saved as a copy of this earlier
    birdnames = []
    try:
        print(" - Checking for 'birdnames.txt'...")
        # Try to create a birdnames file
        birdnamesfile = open("birdnames.txt", "x", encoding="utf-8")
        print(" -  - Created new 'birdnames.txt'.")
        # If a success, that means none existed yet
        # Get the contents of the bird name dropdown
        birdnames = driver.find_elements_by_xpath('//li[contains(@class, "select2-result")]'
                                                  '/div')
        print(" - Processing name data...")
        # Extract the bird names from each of the dropdown's elements
        birdnames = ["".join(re.split(r"<span.*span>", birdname.get_attribute("innerHTML")))
                     for birdname in birdnames]
        print(" -  - Writing site names to 'birdnames.txt'...")
        # Save these to the file for later use
        birdnamesfile.write("\n".join(birdnames))
    except FileExistsError:
        print(" -  - Found old 'birdnames.txt'...")
        # If there already exists a file with the names in, give the option to use it
        # TODO: Variable needs a better name
        ohgoonthen = input("\nUse this file?\n"
                           " - Enter to proceed with this name list,\n"
                           " - o then Enter to overwrite it.\n"
                           ">>> ").lower()
        if ohgoonthen == "o":
            # Overwrite the old file with a blank new one
            birdnamesfile = open("birdnames.txt", "w", encoding="utf-8")
            # TODO: Reroute this code to avoid duplication
            print(" -  - Old 'birdnames.txt' overwritten.")
            # Get the contents of the bird name dropdown
            birdnames = driver.find_elements_by_xpath('//li[contains(@class, "select2-result")]'
                                                      '/div')
            print(" - Processing name data...")
            # Extract the bird names from each of the dropdown's elements
            birdnames = ["".join(re.split(r"<span.*span>", birdname.get_attribute("innerHTML")))
                         for birdname in birdnames]
            print(" -  - Writing site names to 'birdnames.txt'...")
            # Save these to the file for later use
            birdnamesfile.write("\n".join(birdnames))
        else:
            # Otherwise read the names from a previously saved file
            birdnamesfile = open("birdnames.txt", "r", encoding="utf-8")
            birdnames = birdnamesfile.read()
            birdnames = birdnames.split("\n")
    finally:
        # Always sure to close the file afterwards (Although python would probably clean up otherwise anyway)
        birdnamesfile.close()
    print(" -  - Bird names ready.\n\n", birdnames, "\n - Bird names extracted.")

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
        ohgoonthen = input("\nUse these birds?\n"
                           " - Enter to proceed with extracting data for these birds,\n"
                           " - n then Enter to try a different search.\n"
                           ">>> ")
        if ohgoonthen == "n":
            # Return to asking for a new selection if selection not confirmed
            continue

        # Go through each bird name in the selection and download the relevant table
        overwritepolicy = ""
        for birdname in chosenbirdnames:
            # Take baseline table read against which to check if updates have actually occurred later
            birdtable = driver.find_element_by_xpath('//table[@class="maintable"]'
                                                     '/tbody[@id="wr_webs_report"]'
                                                     '/..'
                                                     '/..')
            birdtablehtml = birdtable.get_attribute("innerHMTL")
            print("\nExtracting data table [{}]...".format(time.strftime("%H:%M:%S")))
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
                if overwritepolicy not in ["a", "o"]:
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

            print(" - Navigating to page...")
            # Enter the bird's name into the species searchbox and hit Enter ("\n")
            birdsearchbox.send_keys(birdname + "\n")
            # Wait a moment to give the page a chance to load
            time.sleep(1)  # TODO: find a way to do this more efficiently, but just as certainly
            # Initialise interface for easily writing to the csv file
            birdwriter = csv.writer(birdfile)
            # Get the elements which move the table to the next page...
            nextpagebutton = driver.find_element_by_xpath('//button[@id="nextLot"]')
            # ...slide the table back one year...
            backyearbutton = driver.find_element_by_xpath('//span[@id="wr_backInTime"]')
            # ...and move forward to the latest available year (usually "17/18" or "2018")
            finalyearbutton = driver.find_element_by_xpath('//span[@id="wr_forwardToEnd"]')
            # For storing the number of the current page of the current bird species' table
            birdpage = 1

            while True:
                try:
                    # Make sure that the table starts off at the far right of this page
                    finalyearbutton.click()
                except UnexpectedAlertPresentException:
                    # If the finalyearbutton is pressed whilst the "you are viewing the last page" alert is still
                    # visible, then this Exception is raised
                    # (This Exception being raised also means that the alert is dismissed)
                    print(" - Reaching end of table...")
                    # Write an obvious END on the csv
                    birdwriter.writerow(["END"])
                    # Go to finalise and close the csv
                    break
                # Gets the current GMT time in a neat format
                accesstime = time.strftime("%Y-%m-%d %H:%M:%S")
                print(" - Processing page {} [{}]...".format(birdpage, time.strftime("%H:%M:%S")))
                # Get the element corresponding to the visible table
                newbirdtablehtml = birdtablehtml
                checks = 0
                while birdtablehtml == newbirdtablehtml:
                    # This loop checks whether the data has actually changed since the last read, as a safeguard
                    if checks == 5:
                        break
                    print(" -  - Attempting to grab table data (0:{})...".format(checks))
                    time.sleep(1)
                    newbirdtablehtml = birdtable.get_attribute("innerHTML")
                    checks += 1
                birdtablehtml = newbirdtablehtml
                # Convert the html of the table into a DataFrame of population data + Supplementary info
                birdtabledata = read_html(birdtable.get_attribute("innerHTML"))[0]
                # Scroll back 5 years 3 times, to bring the total table range to 20 years
                for i in range(3):
                    for j in range(5):
                        backyearbutton.click()
                    time.sleep(1)
                    # Get the table each 5 new years
                    newbirdtablehtml = birdtablehtml
                    checks = 0
                    while birdtablehtml == newbirdtablehtml:
                        # This loop checks whether the data has actually changed since the last read, as a safeguard
                        if checks == 5:
                            break
                        print(" -  - Attempting to grab table data ({}:{})...".format(i + 1, checks))
                        time.sleep(0.1)
                        newbirdtablehtml = birdtable.get_attribute("innerHTML")
                        checks += 1
                    birdtablehtml = newbirdtablehtml
                    # Convert its html into a DataFrame, as before
                    pagetabledata = read_html(birdtablehtml)[0]
                    # Connect the new data columns onto the end of the existing table
                    birdtabledata = pd.concat([birdtabledata, pagetabledata[pagetabledata.columns[2:7]]], axis=1)
                # Add columns giving the table page number and time of access as metadata alongside the population data
                birdtabledata = birdtabledata.assign(WebPageNo=birdpage, RoughTimeAccessed=accesstime)
                # Get the column names and organise them Site - Population (oldest to youngest) - Metadata
                cols = birdtabledata.columns.tolist()
                cols = [cols[0]] + cols[22:27] + cols[17:22] + cols[12:17] + cols[2:7] + cols[8:11] + cols[27:]
                print(cols)

                try:
                    # origcols contains the first set of column names extracted for this species this session
                    # If it already exists (i.e., this is not the first page) and this page's column names match...
                    if cols == origcols:
                        # TODO: Somehow avoid code duplication here? Need me some functions
                        # Rearrange the downloaded table data as above
                        birdtabledata = np.object_(birdtabledata[cols])

                        # Write each row of the downloaded table to the csv file
                        for row in birdtabledata:
                            birdwriter.writerow(row)
                        # Move on to the next page of data
                        # N.B. This raises an alert (handled above) if there are no more pages
                        nextpagebutton.click()
                        birdpage += 1
                    else:
                        print(" -  - Error in page processing; table headings do not match.")
                        # If the column names don't match... uh... do something?
                        input("We're going to have to skip this one for now\n>>> ")
                        # TODO: Set up some options for what to do at this point
                except NameError:
                    # If origcols doesn't yet exist, this is the first page, so set the standard for column names
                    origcols = cols
                    # Rearrange the downloaded table data as per cols above
                    birdtabledata = np.object_(birdtabledata[cols])

                    # Write each row of the downloaded table to the csv file
                    birdwriter.writerow(cols)
                    for row in birdtabledata:
                        birdwriter.writerow(row)

                    # Move on to the next page of data
                    # N.B. This raises an alert (handled above) if there are no more pages
                    nextpagebutton.click()
                    birdpage += 1
                time.sleep(1)
            # Close the csv file, now that nothing more need be written to it
            birdfile.close()
            print(" - Data table extracted.\n\n", birdtabledata, "\n")
            # Reset ready for the next bird name
            birdnamedropdown.click()
            del origcols
finally:
    # Shut Firefox if there is some kind of error
    print("Closing driver...")
    driver.close()
    print(" - Driver closed.")

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
"""
