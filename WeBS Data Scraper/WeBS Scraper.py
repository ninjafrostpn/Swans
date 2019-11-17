import numpy as np
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
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
        EC.presence_of_all_elements_located((By.XPATH,
                                             '//table[@class="maintable"]/tbody/tr/td/div/*'))
    )
    print(" - Site and table loaded.\nExtracting data table...")
    # Joins table cells into a string, cells delineated using *
    # (Skips delineator which sits before the first cell)
    table = "".join([t.text if t.text != "" else "*" for t in table[1:]])

    # Replaces gaps left by supplementary data hiders with placeholders
    table = " ({} [{}])*".join(table.split("**"))

    # Gets the supplementary data sources and inserts them
    hiders = driver.find_elements_by_xpath('//div[@class="hider"]/*')
    hiders = [t.get_attribute("innerHTML") for t in hiders]
    hiders = re.split(r"</?em>", "".join(hiders))
    print(hiders)
    table = table.format(*hiders)

    # Breaks the string up into cells again and formats them as a table with 10 cells per row
    table = np.object_(table.split("*"))
    muteswa_table = table.reshape(-1, 10)
    print(" - Data table extracted.\n\n", table)

    # Finds the location dropdown menu and clicks it
    print("Extracting names for sites with data available...")
    dropdown = driver.find_element_by_xpath('//div[@id="locationFg"]/div[contains(@class, "select2-container")]')
    dropdown.click()

    # Finds the searchboxes (both visible and currently invisible)
    searchboxes = driver.find_elements_by_xpath('//input[contains(@class, "select2-input")]')
    for searchbox in searchboxes:
        # Checks that it's the visible searchbox
        if searchbox.is_displayed():
            # Clears it, just in case, then finds all the non-italicised dropdown elements
            # (The italicised ones don't appear to have any data on their tables)
            searchbox.clear()
            sitenames = driver.find_elements_by_xpath('//li[contains(@class, "select2-result") and '
                                                           'not(contains(@class, "italicSpecies"))]/div')

            # Extracts all the site names from this list
            print(" - Processing name data...")
            sitenames = ["".join(re.split(r"<span.*span>", sitename.get_attribute("innerHTML")))
                         for sitename in sitenames]
            print(" - Site names extracted.\n\n", sitenames)
    time.sleep(2)
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
"""
