import csv
import numpy as np
import os
import pandas as pd
from pandas.io.html import read_html
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
import time
import winsound

# Script First Worked on: 2019-11-20
# By: Charles S Turvey

webs_site = "https://app.bto.org/webs-reporting/"
muteswan_site = webs_site + "?tab=numbers&speciescode=46"

print("Opening driver...")
driver = webdriver.Firefox()
print(" - Driver opened.")

try:
    print("Creating 'csvdata' directory...")
    os.mkdir("csvdata")
    print(" - Created 'csvdata' directory.")
except FileExistsError:
    print(" - There already exists a 'csvdata' directory.")

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
                           " - o then Enter to overwrite it\n"
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

    while True:
        print("Extracting data table...")
        overwritepolicy = ""
        try:
            print(" - Creating 'birds.csv'...")
            birdfile = open("csvdata//birds.csv", "x", encoding="utf-8", newline="")
        except FileExistsError:
            print(" -  - Found old 'birds.csv'...")
            overwritepolicy = input("\nKeep this file?\n"
                                    " - Enter to keep the old file,\n"
                                    " - a then enter to keep all\n"
                                    " - o then Enter to overwrite it,\n"
                                    " - x then Enter to overwrite all\n"
                                    ">>> ").lower()
            if overwritepolicy.lower() in ["o", "x"]:
                print(" -  - Overwriting old 'birds.csv'...")
                birdfile = open("csvdata//birds.csv", "w", encoding="utf-8", newline="")
                print(" -  - Old 'birds.csv' overwritten.")
            else:
                print(" -  - Old 'birds.csv' kept.\n - Table extraction skipped.")  # TODO: Fix this...

        birdwriter = csv.writer(birdfile)
        birdwriter.writerow(["Site",
                             *["{}/{}".format(i % 100, (i+1) % 100) for i in range(98, 117)],
                             "MaximalMonthOf18", "Mean5yr", "Mean12/13-17/18"])
        nextpagebutton = driver.find_element_by_xpath('//button[@id="nextLot"]')
        backyearbutton = driver.find_element_by_xpath('//span[@id="wr_backInTime"]')
        finalyearbutton = driver.find_element_by_xpath('//span[@id="wr_forwardToEnd"]')
        birdpage = 1
        totalbirdpages = int(driver.find_element_by_xpath('//select[@id="pageNo"]'
                                                          '/option[last()]').get_attribute("value"))

        while True:
            print(" - Processing page {}...".format(birdpage))
            finalyearbutton.click()
            table = driver.find_element_by_xpath('//table[@class="maintable"]'
                                                 '/tbody[@id="wr_webs_report"]'
                                                 '/..'
                                                 '/..')
            table = read_html(table.get_attribute("innerHTML"))[0]
            for i in range(3):
                for j in range(5):
                    backyearbutton.click()
                table = driver.find_element_by_xpath('//table[@class="maintable"]'
                                                     '/tbody[@id="wr_webs_report"]'
                                                     '/..'
                                                     '/..')
                table = read_html(table.get_attribute("innerHTML"))[0]
                birdtable = pd.concat([table, table[table.columns[2:7]]], axis=1)
            cols = birdtable.columns.tolist()
            cols = [cols[0]] + cols[12:] + cols[2:7] + cols[8:11]
            birdtable = birdtable[cols]
            birdtable = np.object_(birdtable)

            for row in birdtable:
                birdwriter.writerow(row)

            if birdpage == totalbirdpages:
                birdwriter.writerow(["END"] * 12)
                break
            else:
                nextpagebutton.click()
                birdpage += 1
        birdfile.close()
        print(" - Data table extracted.\n\n", birdtable, "\n")
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
"""
