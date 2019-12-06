# Script First Worked on: 2019-12-04
# By: Charles S Turvey

import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Which plots to plot and whether to display or save them
whichplots = ["-WWTpop", "-top10pop", "WWTcombinedpop"]
showfigures = True
savefigures = True


def showsave(filename):
    if savefigures:
        plt.savefig("{}.png".format(filename), dpi=200)
    if showfigures:
        plt.show()
    else:
        plt.clf()


# Labels for the WeBS years
yearlabels = ["{:02d}/{:02d}".format(i % 100, (i + 1) % 100) for i in range(1945, 2021)]

# List of the WeBS sites corresponding to the 9 WWT sites {using sources 0, 1}
WWTsitenames = ["Strangford Lough",       # WWT Castle Espie
                "Solway Estuary",         # WWT Caerlaverock
                "WWT Washington",         # WWT Washington
                "WWT Martin Mere",        # WWT Martin Mere
                "Burry Inlet",            # WWT Llanelli
                "Severn Estuary",         # WWT Slimbridge
                "Arun Valley",            # WWT Arundel
                "London Wetland Centre",  # WWT London
                "Ouse Washes"]            # WWT Welney


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


def plotpop(birdname, birdpop, birdloc, sitemask=None, maskname=""):
    if sitemask is None:
        sitemask = [True] * len(birdloc)
    # Resize the visible figure to fit the screen, then resize the figure object to match
    # (The second line may not work on all systems. See other answers around {source  3})
    mng = plt.get_current_fig_manager().window
    mng.state("zoomed")
    plt.gcf().set_size_inches(mng.winfo_width() / 100, mng.winfo_height() / 100)
    # Plot grid lines
    plt.hlines(10 ** np.arange(0, 5), 0, 76, "#BBBBBB", "--")
    # Plot each site as a new trace
    for row in birdpop[sitemask]:
        plt.plot(row, ".-")
    # Add a title
    plt.title("{} Populations over the years {}".format(birdname, maskname))
    # The y scale is logarithmic until below 1, at which point it's linear to allow 0s to be plotted
    plt.yscale("symlog", linthreshy=1)
    # Define the bounds of the figure
    plt.xlim(0, 75)
    plt.ylim(0, 10000)
    # Labels every 5 years for 75 years on the x axis
    plt.xticks(range(0, 76, 5), yearlabels[::5])
    # Label the y axis with actual numbers, with space-separated thousands {source 2}
    plt.yticks([0, *(10 ** np.arange(0, 5))],
               ["{:,}".format(i).replace(",", " ") for i in [0, *(10 ** np.arange(0, 5))]])
    # Label the axes
    plt.xlabel("WeBS Sampling Year")
    plt.ylabel("Max {} Population Recorded in Period".format(birdname))
    # Add the figure legend
    plt.legend(birdloc[sitemask], fontsize=7)


def selectsites(fromsites, choosesites):
    sortedmask = np.argsort(fromsites)
    return sortedmask[np.searchsorted(fromsites[sortedmask], choosesites)]


# Import the data for the three main swanses
MStable, MSloc, MSpop = getbirddata("Mute Swan")
WStable, WSloc, WSpop = getbirddata("Whooper Swan")
BStable, BSloc, BSpop = getbirddata("Bewick's Swan")

# Plot the top 10 sites' population as they come off the database
if "top10pop" in whichplots:
    maskname = "at the 10 sites with highest recent 5-year average population"
    plotpop("Mute Swan", MSpop, MSloc, range(10), maskname=maskname)
    showsave("Top 10 MS Sites")
    plotpop("Whooper Swan", WSpop, WSloc, range(10), maskname=maskname)
    showsave("Top 10 WS Sites")
    plotpop("Bewick's Swan", BSpop, BSloc, range(10), maskname=maskname)
    showsave("Top 10 BS Sites")

# Plot populations for the sites
if "WWTpop" in whichplots:
    maskname = "at sites with WWT centres"
    plotpop("Mute Swan", MSpop, MSloc, selectsites(MSloc, WWTsitenames), maskname=maskname)
    showsave("MS at WWT")
    plotpop("Whooper Swan", WSpop, WSloc, selectsites(WSloc, WWTsitenames), maskname=maskname)
    showsave("WS at WWT")
    plotpop("Bewick's Swan", BSpop, BSloc, selectsites(BSloc, WWTsitenames), maskname=maskname)
    showsave("BS at WWT")

if "WWTcombinedpop":
    for sitename in WWTsitenames:
        plotpop("Swan",
                np.float32([MSpop[MSloc == sitename][0],
                            WSpop[WSloc == sitename][0],
                            BSpop[BSloc == sitename][0]]),
                np.object_(["Mute Swan", "Whooper Swan", "Bewick's Swan"]),
                maskname="at " + sitename)
        showsave("Three Swans at " + sitename)

"""
0 https://www.wwt.org.uk/wetland-centres/
1 http://app.bto.org/websonline/sites/data/sites-data.jsp
2 https://stackoverflow.com/a/18891054
3 https://stackoverflow.com/a/19823837
"""
