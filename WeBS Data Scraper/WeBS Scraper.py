import csv
import numpy as np
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
import time

webs_site = "https://app.bto.org/webs-reporting/"
muteswan_site = webs_site + "?tab=numbers&speciescode=46"
severnestuary_site = webs_site + "?tab=numbers&locid=LOC648397"

print("Opening driver...")
driver = webdriver.Firefox()
print(" - Driver opened.")
try:
    print("Loading WeBS site...")
    driver.get(muteswan_site)
    print(" - Waiting for table to load...")
    table = WebDriverWait(driver, 60).until(
        ec.presence_of_all_elements_located((By.XPATH, '//table[@class="maintable"]'
                                                       '/tbody'
                                                       '/tr'
                                                       '/td'
                                                       '/div'
                                                       '/*'))
    )
    print(" - Site and table loaded.\nExtracting data table...")

    overwritepolicy = ""
    try:
        print(" - Creating 'muteswans.csv'...")
        muteswanfile = open("muteswans.csv", "x", encoding="utf-8", newline="")
    except FileExistsError:
        print(" -  - Found old 'muteswans.csv'...")
        overwritepolicy = input("\nKeep this file?\n"
                                " - Enter to keep the old file,\n"
                                " - a then enter to keep all\n"
                                " - o then Enter to overwrite it,\n"
                                " - x then Enter to overwrite all\n"
                                ">>> ").lower()
        if overwritepolicy.lower() in ["o", "x"]:
            print(" -  - Overwriting old 'muteswans.csv'...")
            muteswanfile = open("muteswans.csv", "w", encoding="utf-8", newline="")
            print(" -  - Old 'muteswans.csv' overwritten.")
        else:
            print(" -  - Old 'muteswans.csv' kept.\n - Table extraction skipped.")

    # Joins table cells into a string, cells delineated using *
    # (Skips delineator which sits before the first cell)
    table = "".join([t.text if t.text != "" else "*" for t in table[1:]])

    # Replaces gaps left by supplementary data hiders with placeholders
    table = " ({} [{}])*".join(table.split("**"))

    # Gets the supplementary data sources and inserts them
    hiders = driver.find_elements_by_xpath('//div[@class="hider"]'
                                           '/*')
    hiders = [t.get_attribute("innerHTML") for t in hiders]
    hiders = re.split(r"</?em>", "".join(hiders))
    print(hiders)
    table = table.format(*hiders)

    # Breaks the string up into cells again and formats them as a table with 10 cells per row
    table = np.object_(table.split("*"))
    muteswantable = table.reshape(-1, 10)
    muteswanwriter = csv.writer(muteswanfile)
    muteswanwriter.writerow(["Site",
                             "13/14", "14/15", "15/16", "16/17", "17/18",
                             "MaximalMonth", "Mean5yr", "Mean12/13-17/18"])
    for row in muteswantable:
        muteswanwriter.writerow(row)
    muteswanfile.close()
    # TODO: extend this to include more pages of mute swans
    print(" - Data table extracted.\n\n", muteswantable, "\n")

    # Finds the location dropdown menu and clicks it
    # TODO: probably change this to use the list of mute swan sites, not just EVERY site
    print("Extracting names for sites with data available...")
    sitenamedropdown = driver.find_element_by_xpath('//div[@id="locationFg"]'
                                                    '/div[contains(@class, "select2-container")]')
    sitenamedropdown.click()

    # Finds the searchboxes (both visible and currently invisible)
    searchboxes = driver.find_elements_by_xpath('//input[contains(@class, "select2-input")]')
    locationsearchbox = None
    sitenames = []
    for searchbox in searchboxes:
        # Checks that it's the visible searchbox
        if searchbox.is_displayed():
            # Clears it, just in case, then finds all the non-italicised dropdown elements
            # (The italicised ones don't appear to have any data on their tables)
            locationsearchbox = searchbox
            searchbox.clear()
            try:
                print(" - Checking for 'sitenames.txt'...")
                sitenamesfile = open("sitenames.txt", "x", encoding="utf-8")
                print(" -  - Created new 'sitenames.txt'.")
                sitenames = driver.find_elements_by_xpath('//li[contains(@class, "select2-result") and '
                                                               'not(contains(@class, "italicSpecies"))]'
                                                          '/div')

                # Extracts all the site names from this list
                print(" - Processing name data...")
                sitenames = ["".join(re.split(r"<span.*span>", sitename.get_attribute("innerHTML")))
                             for sitename in sitenames]
                print(" -  - Writing site names to 'sitenames.txt'...")
                sitenamesfile.write("\n".join(sitenames))
            except FileExistsError:
                print(" -  - Found old 'sitenames.txt'.")
                sitenamesfile = open("sitenames.txt", "r", encoding="utf-8")
                ohgoonthen = input("\nUse this file?\n"
                                   " - Enter to proceed with this name list,\n"
                                   " - o then Enter to overwrite it\n"  # TODO: Implement this.
                                   ">>> ").lower()
                if ohgoonthen.lower() == "o":
                    quit()
                print(" - Reading old 'sitenames.txt'...")
                sitenames = sitenamesfile.read()
                sitenames = sitenames.split("\n")
            finally:
                sitenamesfile.close()
            print(" -  - Site names ready.\n\n", sitenames, "\n")

    # Now for the real data extraction. This will enter each site name in turn and get the relevant data table
    print("Extracting individual site data tables...")
    sitetables = []
    for sitename in sitenames:
        print(" - Extracting data table for " + sitename + "...")
        try:
            print(" -  - Creating '" + sitename + ".csv'...")
            sitefile = open(sitename + ".csv", "x", encoding="utf-8", newline="")
        except FileExistsError:
            print(" -  -  - Found old '" + sitename + ".csv'...")
            if overwritepolicy.lower() == "a":
                print(" -  -  - Old '" + sitename + ".csv' kept.\n -  - Data extraction skipped for this site.")
                continue
            elif overwritepolicy.lower() == "x":
                print(" -  -  - Overwriting old '" + sitename + ".csv'...")
                sitefile = open(sitename + ".csv", "w", encoding="utf-8", newline="")
                print(" -  -  - Old '" + sitename + ".csv' overwritten.")
            else:
                overwritepolicy = input("\nKeep this file?\n"
                                        " - Enter to keep the old file,\n"
                                        " - a then enter to keep all\n"
                                        " - o then Enter to overwrite it,\n"
                                        " - x then Enter to overwrite all\n"
                                        ">>> ").lower()
                if overwritepolicy.lower() in ["o", "x"]:
                    print(" -  -  - Overwriting old '" + sitename + ".csv'...")
                    sitefile = open(sitename + ".csv", "w", encoding="utf-8", newline="")
                    print(" -  -  - Old '" + sitename + ".csv' overwritten.")
                else:
                    print(" -  -  - Old '" + sitename + ".csv' kept.\n -  - Data extraction skipped for this site.")
                    continue
        print(" -  - Navigating to page...")
        locationsearchbox.send_keys(sitename + "\n")
        time.sleep(1)

        # Ensure that the bird group selector is set to wildfowl
        print(" -  - Selecting correct table settings...\n -  -  - Selecting wildfowl...")
        birdgroupdropdown = driver.find_element_by_xpath('//select[@id="birdgroup"]')
        while birdgroupdropdown.get_attribute("value") != "WIL":
            birdgroupdropdown.send_keys("wi")
        time.sleep(1)

        # Ensure that supplementary data are always included
        print(" -  -  - Selecting supplementary data...")
        suppbutton = driver.find_element_by_xpath('//input[@id="supps"]')
        if not suppbutton.is_selected():
            suppbutton.click()
        time.sleep(1)

        # Ensure that the birds are arranged in descending 5-year mean abundance
        print(" -  -  - Selecting sort descending by 5-year-mean abundance...")
        mean5descendingbutton = driver.find_element_by_xpath('//th[@id="mean5"]'
                                                             '/span[@class="hal"]'
                                                             '/span[contains(@class, "toggleDown")]')
        if "activeSort" not in mean5descendingbutton.get_attribute("class"):
            mean5descendingbutton.click()
        time.sleep(1)
        print(" -  -  - Settings set.")

        table = driver.find_elements_by_xpath('//table[@class="maintable"]'
                                              '/tbody'
                                              '/tr'
                                              '/td'
                                              '/div'
                                              '/*')

        # TODO: Maybe break out the table parsing to a separate function
        # Joins table cells into a string, cells delineated using *
        # (Skips delineator which sits before the first cell)
        table = "".join([t.text if t.text != "" else "*" for t in table[1:]])
        # TODO: Fix potential issue with wildfowl-free sites yielding a spurious "**" sequence (may be misinterpreted)

        # Replaces gaps left by supplementary data hiders with placeholders
        table = " ({} [{}])*".join(table.split("**"))

        # Gets the supplementary data sources and inserts them
        hiders = driver.find_elements_by_xpath('//div[@class="hider"]'
                                               '/*')
        hiders = [t.get_attribute("innerHTML") for t in hiders]
        hiders = re.split(r"</?em>", "".join(hiders))
        print(hiders)
        table = table.format(*hiders)

        # Breaks the string up into cells again and formats them as a table with 10 cells per row
        table = np.object_(table.split("*"))
        sitetables.append(table.reshape(-1, 10))
        sitewriter = csv.writer(sitefile)
        sitewriter.writerow(["Species",
                             "13/14", "14/15", "15/16", "16/17", "17/18",
                             "MaximalMonth", "Mean5yr", "Mean12/13-17/18"])
        for row in sitetables[-1]:
            sitewriter.writerow(row)
        sitefile.close()
        print(" -  - Data table extracted.\n\n", sitetables[-1], "\n")
        sitenamedropdown.click()
finally:
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
"""
