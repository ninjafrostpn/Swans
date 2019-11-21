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

# Script First Worked on: 2019-11-20
# By: Charles S Turvey

webs_site = "https://app.bto.org/webs-reporting/"
muteswan_site = webs_site + "?tab=numbers&speciescode=46"

print("Opening driver...")
driver = webdriver.Firefox()
print(" - Driver opened.")

try:
    print("Creating 'BirdCSVs' directory...")
    os.mkdir("BirdCSVs")
    print(" - Created 'BirdCSVs' directory.")
except FileExistsError:
    print(" - There already exists a 'BirdCSVs' directory.")

try:
    print("Loading WeBS site...")
    driver.get(muteswan_site)
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
    birdnamedropdown = driver.find_element_by_xpath('//div[@id="speciesFg"]'
                                                    '/div[contains(@class, "select2-container")]')
    birdnamedropdown.click()
    searchboxes = driver.find_elements_by_xpath('//input[contains(@class, "select2-input")]')
    birdsearchbox = None
    for searchbox in searchboxes:
        # Checks that it's the visible searchbox
        if searchbox.is_displayed():
            birdsearchbox = searchbox
    birdsearchbox.clear()

    birdnames = []
    try:
        print(" - Checking for 'birdnames.txt'...")
        birdnamesfile = open("birdnames.txt", "x", encoding="utf-8")
        print(" -  - Created new 'birdnames.txt'.")
        birdnames = driver.find_elements_by_xpath('//li[contains(@class, "select2-result")]'
                                                  '/div')
        print(" - Processing name data...")
        birdnames = ["".join(re.split(r"<span.*span>", birdname.get_attribute("innerHTML")))
                     for birdname in birdnames]
        print(" -  - Writing site names to 'birdnames.txt'...")
        birdnamesfile.write("\n".join(birdnames))
    except FileExistsError:
        print(" -  - Found old 'birdnames.txt'...")
        # TODO: Variable needs a better name
        ohgoonthen = input("\nUse this file?\n"
                           " - Enter to proceed with this name list,\n"
                           " - o then Enter to overwrite it.\n"
                           ">>> ").lower()
        if ohgoonthen == "o":
            birdnamesfile = open("birdnames.txt", "w", encoding="utf-8")
            # TODO: Reroute this code to avoid duplication
            print(" -  - Old 'birdnames.txt' overwritten.")
            birdnames = driver.find_elements_by_xpath('//li[contains(@class, "select2-result")]'
                                                      '/div')
            print(" - Processing name data...")
            birdnames = ["".join(re.split(r"<span.*span>", birdname.get_attribute("innerHTML")))
                         for birdname in birdnames]
            print(" -  - Writing site names to 'birdnames.txt'...")
            birdnamesfile.write("\n".join(birdnames))
        else:
            birdnamesfile = open("birdnames.txt", "r", encoding="utf-8")
            birdnames = birdnamesfile.read()
            birdnames = birdnames.split("\n")
    finally:
        birdnamesfile.close()
    print(" -  - Bird names ready.\n\n", birdnames, "\n - Bird names extracted.")

    while True:
        birdname = input("\nEnter bird name or regex pattern, case insensitive\n>>> ")
        print("Finding bird name matches...")
        matcher = re.compile(birdname, re.IGNORECASE)
        chosenbirdnames = list(filter(matcher.search, birdnames))
        if len(chosenbirdnames) == 0:
            print(" - No bird name matches found.")
            continue
        print(" - Bird name matches found ({}).\n\n".format(len(chosenbirdnames)), "\n".join(chosenbirdnames), sep="")
        ohgoonthen = input("\nUse these birds?\n"
                           " - Enter to proceed with extracting data for these birds,\n"
                           " - n then Enter to try a different search.\n"
                           ">>> ")
        if ohgoonthen == "n":
            continue

        overwritepolicy = ""
        for birdname in chosenbirdnames:
            print("\nExtracting data table [{}]...".format(time.strftime("%H:%M:%S")))
            try:
                print(" - Creating '{}.csv'...".format(birdname))
                birdfile = open("BirdCSVs//{}.csv".format(birdname), "x", encoding="utf-8", newline="")
            except FileExistsError:
                print(" -  - Found old '{}.csv'...".format(birdname))
                overwritepolicy = input("\nKeep this file?\n"
                                        " - Enter to keep the old file,\n"
                                        " - a then Enter to keep all,\n"
                                        " - o then Enter to overwrite it,\n"
                                        " - x then Enter to overwrite all.\n"
                                        ">>> ").lower()
                if overwritepolicy.lower() in ["o", "x"]:
                    print(" -  - Overwriting old '{}.csv'...".format(birdname))
                    birdfile = open("BirdCSVs//{}.csv".format(birdname), "w", encoding="utf-8", newline="")
                    print(" -  - Old '{}.csv' overwritten.".format(birdname))
                else:
                    print(" -  - Old '{}.csv' kept.\n - Table extraction skipped.".format(birdname))  # TODO: Fix this...

            print(" - Navigating to page...")
            birdsearchbox.send_keys(birdname + "\n")
            time.sleep(1)

            birdwriter = csv.writer(birdfile)
            nextpagebutton = driver.find_element_by_xpath('//button[@id="nextLot"]')
            backyearbutton = driver.find_element_by_xpath('//span[@id="wr_backInTime"]')
            finalyearbutton = driver.find_element_by_xpath('//span[@id="wr_forwardToEnd"]')
            birdpage = 1

            while True:
                try:
                    finalyearbutton.click()
                except UnexpectedAlertPresentException:
                    print(" - Reaching end of table...")
                    # This Exception being raised means that the alert is dismissed anyway
                    # driver.switch_to.alert.dismiss()
                    birdwriter.writerow(["END"])
                    break
                accesstime = time.strftime("%Y-%m-%d %H:%M:%S")
                print(" - Processing page {} [{}]...".format(birdpage, time.strftime("%H:%M:%S")))
                birdtable = driver.find_element_by_xpath('//table[@class="maintable"]'
                                                         '/tbody[@id="wr_webs_report"]'
                                                         '/..'
                                                         '/..')
                birdtable = read_html(birdtable.get_attribute("innerHTML"))[0]
                for i in range(3):
                    for j in range(5):
                        backyearbutton.click()
                    pagetable = driver.find_element_by_xpath('//table[@class="maintable"]'
                                                             '/tbody[@id="wr_webs_report"]'
                                                             '/..'
                                                             '/..')
                    pagetable = read_html(pagetable.get_attribute("innerHTML"))[0]
                    birdtable = pd.concat([birdtable, pagetable[pagetable.columns[2:7]]], axis=1)
                cols = birdtable.columns.tolist()
                cols = [cols[0]] + cols[22:] + cols[17:22] + cols[12:17] + cols[2:7] + cols[8:11]
                print(cols)

                try:
                    if cols == origcols:
                        # TODO: Somehow avoid code duplication here? Need me some functions
                        birdtable = birdtable[cols]
                        birdtable = birdtable.assign(WebPageNo=birdpage, RoughTimeAccessed=accesstime)
                        birdtable = np.object_(birdtable)

                        for row in birdtable:
                            birdwriter.writerow(row)
                        nextpagebutton.click()
                        birdpage += 1
                    else:
                        print(" -  - Error in page processing; table headings do not match.")
                except NameError:
                    origcols = cols
                    birdtable = birdtable[cols]
                    birdtable = birdtable.assign(WebPageNo=birdpage, RoughTimeAccessed=accesstime)
                    birdtable = np.object_(birdtable)

                    birdwriter.writerow(cols)
                    for row in birdtable:
                        birdwriter.writerow(row)
                    nextpagebutton.click()
                    birdpage += 1
            birdfile.close()
            print(" - Data table extracted.\n\n", birdtable, "\n")
            birdnamedropdown.click()
            del origcols  # This code is a mess
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
https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
https://pandas.pydata.org/pandas-docs/stable/user_guide/merging.html
https://stackoverflow.com/questions/3640359/regular-expressions-search-in-list
https://www.techbeamers.com/handle-alert-popup-selenium-python/
https://stackoverflow.com/questions/12555323/adding-new-column-to-existing-dataframe-in-python-pandas
"""
