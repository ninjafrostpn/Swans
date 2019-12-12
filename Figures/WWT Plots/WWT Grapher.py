# Script First Worked on: 2019-12-04
# By: Charles S Turvey

import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Which plots to plot and whether to display or save them
whichplots = ["top10pop", "WWTpop", "WWTcombinedpop"]
showfigures = False
savefigures = True


def showsave(filename):
    if savefigures:
        plt.savefig("{}.png".format(filename), dpi=200)
    if showfigures:
        plt.show()
    else:
        plt.clf()


# Labels for the WeBS years
yearlabels = ["{:02d}/{:02d}".format(i % 100, (i + 1) % 100) for i in range(1935, 2021)]

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
def getbirddata(birdname, popthreshold=None):
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
    # Strip out all timeseries with an average of less than popthreshold, as per 2019-12-10 email
    if popthreshold is not None:
        popthresholdmask = ~(np.nanmean(birdpop, axis=1) < popthreshold)
        return birdtable.loc[popthresholdmask], birdloc[popthresholdmask], birdpop[popthresholdmask]
    return birdtable, birdloc, birdpop


def getmultibirddata(*birdnames, popthreshold=None):
    birdnames = np.object_(birdnames)
    birdtables = []
    birdlocs = []
    birdpops = []
    for birdname in birdnames:
        birdtable, birdloc, birdpop = getbirddata(birdname, popthreshold)
        birdtables.append(birdtable)
        birdlocs.append(birdloc)
        birdpops.append(birdpop)
    birdlocs = np.object_(birdlocs)
    birdpops = np.object_(birdpops)
    return birdnames, birdtables, birdlocs, birdpops


def plotpop(birdname, birdpop, birdloc, sitemask=None, maskname=""):
    if sitemask is None:
        sitemask = [True] * len(birdloc)
    # Resize the visible figure to fit the screen, then resize the figure object to match
    # (The second line may not work on all systems. See other answers around {source  3})
    mng = plt.get_current_fig_manager().window
    mng.state("zoomed")
    plt.gcf().set_size_inches(mng.winfo_width() / 100, mng.winfo_height() / 100)
    # Plot grid lines
    plt.hlines(10 ** np.arange(0, 6), 0, 85, "#BBBBBB", "--")
    # Plot each site as a new trace
    print(sitemask)
    for row in birdpop[sitemask]:
        # The rows are flattened due to issues with masks adding superfluous dimensions etc
        plt.plot(row.flatten(), ".-")
    # Add a title
    plt.title("{} Populations over the years {}".format(birdname, maskname))
    # The y scale is logarithmic until below 1, at which point it's linear to allow 0s to be plotted
    plt.yscale("symlog", linthreshy=1)
    # Define the bounds of the figure
    plt.xlim(0, 85)
    plt.ylim(0, 100000)
    # Labels every 5 years for 83 years on the x axis
    plt.xticks(range(0, 86, 5), yearlabels[::5])
    # Label the y axis with actual numbers, with space-separated thousands {source 2}
    plt.yticks([0, *(10 ** np.arange(0, 6))],
               ["{:,}".format(i).replace(",", " ") for i in [0, *(10 ** np.arange(0, 6))]])
    # Label the axes
    plt.xlabel("WeBS Sampling Year")
    plt.ylabel("Max {} Population Recorded in Period".format(birdname))
    # Add the figure legend
    plt.legend(birdloc[sitemask], fontsize=7)


# Find indices in fromsites of sites matching each of those in choosesites, where possible
# (Indices in order corresponding to choosesites only if all choosesites are in fromsites;
#  will omit indices of missing sites, messing up order.
#  This is better than the alternative, which is allowing searchsorted to return the alphabetically nearest named site.
#  I was warned this might happen, and knew it would come to bite me, yet ignored it anyway.)
def selectsites(fromsites, choosesites, inorder=True):
    # If not required to be in order, just returns a boolean mask
    if inorder:
        # Strips out sites that are not in fromsites {reminded how to list comprehend by source 5}
        choosesites = [site for site in choosesites if site in fromsites]
        # Find the indices of the remaining sites in fromsites
        sortedmask = np.argsort(fromsites)
        return sortedmask[np.searchsorted(fromsites[sortedmask], choosesites)]
    return np.isin(fromsites, choosesites)


# Import the data for the three main swanses
swannames = ["Mute Swan", "Whooper Swan", "Bewick's Swan"]
swannames, swantables, swanlocs, swanpops = getmultibirddata(*swannames, popthreshold=10)


# Import the data for some geeses
# White-fronted geese are on the red list
# Canada Geese and Egyptian Geese are introduced
goosenames = ["Greylag Goose", "Pink-footed Goose", "Brent Goose", "Barnacle Goose", "Taiga-Tundra Bean Goose",
              "White-fronted Goose",
              "Canada Goose", "Egyptian Goose"]
goosenames, goosetables, gooselocs, goosepops = getmultibirddata(*goosenames, popthreshold=10)

# Import the data for some duckses
# Pochard and Scaup are also on the red list
# The Scoters and Long-tailed Ducks are on the red list
# Tufted ducks are on the green list
# Shelduck are not exactly ducks... but also not exactly geese
# Mandarin ducks and Ruddy ducks are introduced
ducknames = ["Mallard", "Eider (except Shetland)", "Goldeneye", "Wigeon", "Shoveler", "Gadwall", "Smew", "Pintail",
             "Pochard", "Scaup", "Velvet Scoter", "Common Scoter", "Long-tailed Duck",
             "Tufted Duck",
             "Shelduck",
             "Mandarin Duck", "Ruddy Duck"]
ducknames, ducktables, ducklocs, duckpops = getmultibirddata(*ducknames, popthreshold=10)


# Plot the top 10 sites' population as they come off the database
# (Or as near to 10 as are available, if too few location records exist)
if "top10pop" in whichplots:
    for k in range(len(swannames)):
        plotpop(swannames[k], swanpops[k], swanlocs[k],
                range(min(10, len(swanlocs[k]))),
                maskname="at the 10 sites with highest recent 5-year average population")
        showsave("Top 10 {} Sites".format(swannames[k]))
    for k in range(len(goosenames)):
        plotpop(goosenames[k], goosepops[k], gooselocs[k],
                range(min(10, len(gooselocs[k]))),
                maskname="at the 10 sites with highest recent 5-year average population")
        showsave("Top 10 {} Sites".format(goosenames[k]))
    for k in range(len(ducknames)):
        plotpop(ducknames[k], duckpops[k], ducklocs[k],
                range(min(10, len(ducklocs[k]))),
                maskname="at the 10 sites with highest recent 5-year average population")
        showsave("Top 10 {} Sites".format(ducknames[k]))

# Plot swan populations across all sites with WWT centres
if "WWTpop" in whichplots:
    for k in range(len(swannames)):
        plotpop(swannames[k], swanpops[k], swanlocs[k],
                selectsites(swanlocs[k], WWTsitenames), maskname="at sites with WWT centres")
        showsave("WWT site " + swannames[k])
    for k in range(len(goosenames)):
        plotpop(goosenames[k], goosepops[k], gooselocs[k],
                selectsites(gooselocs[k], WWTsitenames), maskname="at sites with WWT centres")
        showsave("WWT site " + goosenames[k])
    for k in range(len(ducknames)):
        plotpop(ducknames[k], duckpops[k], ducklocs[k],
                selectsites(ducklocs[k], WWTsitenames), maskname="at sites with WWT centres")
        showsave("WWT site " + ducknames[k])

# Plot the population of all swan species at each site with a WWT centre
if "WWTcombinedpop"in whichplots:
    for sitename in WWTsitenames:
        plotpop("Swan",
                np.object_([swanpops[k][swanlocs[k] == sitename] for k in range(len(swannames))]),
                swannames, maskname="at " + sitename)
        showsave("Swan Species at " + sitename)
        plotpop("Goose",
                np.object_([goosepops[k][gooselocs[k] == sitename] for k in range(len(goosenames))]),
                goosenames, maskname="at " + sitename)
        showsave("Goose Species at " + sitename)
        plotpop("Duck",
                np.object_([duckpops[k][ducklocs[k] == sitename] for k in range(len(ducknames))]),
                ducknames, maskname="at " + sitename)
        showsave("Duck Species at " + sitename)

"""
0 https://www.wwt.org.uk/wetland-centres/
1 http://app.bto.org/websonline/sites/data/sites-data.jsp
2 https://stackoverflow.com/a/18891054
3 https://stackoverflow.com/a/19823837
4 https://www.rspb.org.uk/birds-and-wildlife/wildlife-guides/bird-a-z/ducks-geese-and-swans/
5 https://stackoverflow.com/a/41467237
"""
