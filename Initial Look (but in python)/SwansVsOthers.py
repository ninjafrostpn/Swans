# Script First Worked on: 2019-11-23
# By: Charles S Turvey

import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import re
import scipy.stats as sps

# Array of which plots to plot
# TODO: Seriously, find a better way of doing this
plotids = [3, 10]
# Name of the bird to plot against Mute Swans
birdname = "Canada Goose"

muteswanfile = open("../WeBS Data Scraper/BirdCSVs/Mute Swan.csv")
birdfile = open("../WeBS Data Scraper/BirdCSVs/{}.csv".format(birdname))
muteswanreader = csv.reader(muteswanfile)
birdreader = csv.reader(birdfile)
muteswantable = [row for row in muteswanreader]
if muteswantable[-1][0] != "END":
    ohgoonthen = input("END row not found ({} may be malformed), continue?\n"
                       " - Enter for yes, continue\n"
                       " - n then Enter for no, abort\n"
                       ">>> ".format(muteswanfile.name))
    if ohgoonthen == "n":
        quit()
birdtable = [row for row in birdreader]
if birdtable[-1][0] != "END":
    ohgoonthen = input("END row not found ({} may be malformed), continue?\n"
                       " - Enter for yes, continue\n"
                       " - n then Enter for no, abort\n"
                       ">>> ".format(birdfile.name))
    if ohgoonthen == "n":
        quit()

# Extract column headers (and prints them, to make sure they're what you expect)
muteswanheader = np.object_(muteswantable[0])
print("\n" + str(muteswanheader), "\n")
birdheader = np.object_(birdtable[0])
print("\n" + str(birdheader), "\n")
# Extract body of the data table, to be indexed by [row, column] (here removes headers and "END" row)
muteswandata = np.object_(muteswantable[1:-1])
birddata = np.object_(birdtable[1:-1])
# Extract data of location column
muteswanloc = muteswandata[:, 0]
birdloc = birddata[:, 0]
# Extract population data, to be indexed by [site, year]
muteswanpop = muteswandata[:, 1:-5]
birdpop = birddata[:, 1:-5]

# Function that finds all the strings containing non-numeric characters, vectorised for use on the data
nonnumericmatcher = np.vectorize(lambda x: bool(re.compile("[^0-9]").search(x)))
# Function that deals with the non-numeric strings
def charstripper(x):
    # Converts incomplete counts (start with "(") and nans (start with "nan") to a nan value
    if re.match(r"\(|nan", x):
        # nan is used because one can perform any arithmetic operation on it and still get nan {from source 1}
        # This is useful later, as points containing nan are not plotted by pyplot
        return np.nan
    # And strips the supplementary info off of those counts that have it
    return float("".join(re.match("[0-9,]+", x)[0].split(",")))
# Vectorised for use on the data
charstripper = np.vectorize(charstripper)

# Strip out all the incomplete counts and supplementary notes in both sets of data
nonnumericmask = nonnumericmatcher(muteswanpop)
muteswanpop[nonnumericmask] = charstripper(muteswanpop[nonnumericmask])
muteswanpop = np.float32(muteswanpop)
nonnumericmask = nonnumericmatcher(birdpop)
birdpop[nonnumericmask] = charstripper(birdpop[nonnumericmask])
birdpop = np.float32(birdpop)
# Remove all rows which are entirely nan in the data of each set
# N.B. this means that the row numbers no longer match up with those of "muteswandata" or "birddata"
muteswanpopnanrowmask = np.all(np.isnan(muteswanpop), axis=1)
muteswanpop = muteswanpop[~muteswanpopnanrowmask]
muteswanloc = muteswanloc[~muteswanpopnanrowmask]
birdpopnanrowmask = np.all(np.isnan(birdpop), axis=1)
birdpop = birdpop[~birdpopnanrowmask]
birdloc = birdloc[~birdpopnanrowmask]

# Year labels for the x-axis
xlab = ["{:02d}-{:02d}".format(i % 100, (i + 1) % 100) for i in np.arange(78, 118)]

if 0 in plotids:
    # Plot the top 10 sites (by 5-yr average up to 2017/18) as Swan numbers over the last 40yr
    for i in range(10):
        plt.plot(xlab, muteswanpop[i], ".-")
    plt.legend(muteswanloc)
    plt.xticks(rotation="vertical")
    plt.suptitle("Top 10 sites' Mute Swan numbers over the last 40yr")
    plt.title("(Ranked according to 13/14 - 17/18 population average)")
    plt.ylabel("Maximum Recorded Mute Swan Population in Recording Period")
    plt.xlabel("Recording Period")
    plt.show()

    # Alternative rubbishy 3D plot for the top 20
    fig = plt.figure()
    ax = fig.add_subplot(121, projection='3d')
    for i in range(20):
        ax.plot(np.repeat(i, muteswanpop.shape[1]),
                np.arange(muteswanpop.shape[1]),
                muteswanpop[i])
    ax.set_xticks(np.arange(20))
    ax.set_yticks(np.arange(muteswanpop.shape[1]))
    ax.set_ylabel("\n\n\n\nWeBS Year")
    ax.set_xticklabels(" " * 20)
    ax.set_yticklabels(xlab, rotation="vertical")
    ax.set_zlabel("Mute Swan Population")
    fig.legend(muteswanloc, loc="right")
    plt.show()

if 1 in plotids:
    # Plot the top 10 sites (by 5-yr average up to 2017/18) as [Whatever other bird] numbers over the last 40yr
    for i in range(10):
        plt.plot(xlab, birdpop[i, :], ".-")
    plt.legend(birdloc)
    plt.xticks(rotation="vertical")
    plt.suptitle("Top 10 sites' {} numbers over the last 40yr".format(birdname))
    plt.title("(Ranked according to 13/14 - 17/18 population average)")
    plt.ylabel("Maximum Recorded {} Population in Recording Period".format(birdname))
    plt.xlabel("Recording Period")
    plt.show()

    # Alternative rubbishy 3D plot for the top 20
    fig = plt.figure()
    ax = fig.add_subplot(121, projection='3d')
    for i in range(20):
        ax.plot(np.repeat(i, birdpop.shape[1]),
                np.arange(birdpop.shape[1]),
                birdpop[i])
    ax.set_xticks(np.arange(20))
    ax.set_yticks(np.arange(birdpop.shape[1]))
    ax.set_ylabel("\n\n\n\nWeBS Year")
    ax.set_xticklabels(" " * 20)
    ax.set_yticklabels(xlab, rotation="vertical")
    ax.set_zlabel("{} Population".format(birdname))
    fig.legend(birdloc, loc="right")
    plt.show()

# Show which sites are duplicated. TODO: deal with which to use somehow?
# Seems to be ones which are duplicated on the sites list,
# and they do show up on the pages given by the penultimate column in the data extracted
uniquemuteswanloc, uniquemuteswanlocinstno = np.unique(muteswanloc, return_counts=True)
print(uniquemuteswanloc[uniquemuteswanlocinstno > 1])
uniquebirdloc, uniquebirdlocinstno = np.unique(birdloc, return_counts=True)
print(uniquebirdloc[uniquebirdlocinstno > 1])
# Get the alphabetised set of sites shared by Mute Swans and the other bird
sharedloc = sorted(set(muteswanloc).intersection(set(birdloc)))
# Get ordered row numbers corresponding to the above list of shared sites {from source 0}
muteswanlocsortedmask = np.argsort(muteswanloc)
muteswanlocsharedmask = muteswanlocsortedmask[np.searchsorted(muteswanloc[muteswanlocsortedmask], sharedloc)]
birdlocsortedmask = np.argsort(birdloc)
birdlocsharedmask = birdlocsortedmask[np.searchsorted(birdloc[birdlocsortedmask], sharedloc)]

if 2 in plotids:
    # Plot [other bird] population over swan population (doesn't plot where data is missing for one)
    # Maybe shows that when one is high, the other seems to be low
    plt.plot(muteswanpop[muteswanlocsharedmask].flatten(),
             birdpop[birdlocsharedmask].flatten(),
             ".")
    plt.suptitle("{} Numbers vs Mute Swan Numbers".format(birdname))
    plt.title("(Data for all Sites and Recording Periods for which both were available)")
    plt.xlabel("Maximum Recorded Mute Swan Population at Site in Recording Period")
    plt.ylabel("Maximum Recorded {} Population at Site in Recording Period".format(birdname))
    plt.show()

# Compute year-to-year differences in population where possible
muteswandiff = muteswanpop[:, 1:] - muteswanpop[:, :-1]
birddiff = birdpop[:, 1:] - birdpop[:, :-1]

notnanmask = ~(np.isnan(muteswandiff[muteswanlocsharedmask]) | np.isnan(birddiff[birdlocsharedmask]))
trenddata = [*sps.linregress(muteswandiff[muteswanlocsharedmask][notnanmask].flatten(),
                             birddiff[birdlocsharedmask][notnanmask].flatten())]
if trenddata[3] >= 0.05:
    trenddata[0] = 0
print(trenddata)

if 3 in plotids:
    # Plot [other bird] population changes over mute swan population changes
    # Same cross pattern as seen when carried out in R; maybe shows uncorrelated data
    plt.plot(muteswandiff[muteswanlocsharedmask].flatten(),
             birddiff[birdlocsharedmask].flatten(),
             ".")
    plt.suptitle("Change in {} Numbers vs Change in Mute Swan Numbers".format(birdname))
    plt.title("(Data for all Sites and Pairs of Temporally Adjacent Recording Periods for which both were available)")
    plt.xlabel("Difference in Maximum Recorded Mute Swan Population\nat Site from one Recording Period to the next")
    plt.ylabel("Difference in Maximum Recorded {} Population\n"
               "at Site from one Recording Period to the next".format(birdname))
    trendx = np.arange(int(np.nanmin(muteswandiff[muteswanlocsharedmask])),
                       np.nanmax(muteswandiff[muteswanlocsharedmask]))
    plt.plot(trendx, (trenddata[0] * trendx) + trenddata[1], "--")
    plt.show()

# Plot [other bird] population changes over mute swan population changes occurring up to 5yr ago
# Still pretty similar shape
if 4 in plotids:
    # Create a bunch of stacked plots {see Source 2}
    fig = plt.figure()
    fig.suptitle("Change in {} Numbers vs Change in Mute Swan Numbers".format(birdname))
    fig.subplots_adjust(hspace=0)
    for i in range(1, 6):
        ax = fig.add_subplot(5, 1, i, ylim=(np.nanmin(birddiff[birdlocsharedmask]),
                                            np.nanmax(birddiff[birdlocsharedmask])))
        ax.plot(muteswandiff[muteswanlocsharedmask][:, :-i].flatten(),
                birddiff[birdlocsharedmask][:, i:].flatten(),
                ".")
        if i == 1:
            ax.set_title("(Data for all Sites and Pairs of Temporally Adjacent Recording Periods"
                         " for which both were available)")
        if i == 3:
            ax.set_ylabel("Difference in Maximum Recorded {} Population\n"
                          "at Site from one Recording Period to the next,\n"
                          "taken ___yr after the corresponding change in Mute Swan numbers\n\n3".format(birdname))
        else:
            ax.set_ylabel(i)
        if i == 5:
            ax.set_xlabel("Difference in Maximum Recorded Mute Swan Population"
                          "\nat Site from one Recording Period to the next")
    plt.show()

# Plot [other bird] population changes over mute swan population changes,
# but only for the top 10 sites in terms of average mute swan numbers
# !!nanmean averages over years with available data, so n is different for different site means!!
muteswanpoprowmean = np.nanmean(muteswanpop, axis=1)
muteswanpoptop10mask = np.argsort(muteswanpoprowmean[muteswanlocsharedmask])[-10:]
print(muteswanpoprowmean[muteswanlocsharedmask][muteswanpoptop10mask],
      muteswanloc[muteswanlocsharedmask][muteswanpoptop10mask], sep="\n")
# Same cross pattern as seen when carried out in R; maybe shows uncorrelated data
if 5 in plotids:
    plt.plot(muteswandiff[muteswanlocsharedmask][muteswanpoptop10mask].flatten(),
             birddiff[birdlocsharedmask][muteswanpoptop10mask].flatten(),
             ".")
    plt.show()

if 6 in plotids:
    for i in muteswanpoptop10mask:
        muteswanpopmax = np.nanmax(muteswanpop[muteswanlocsharedmask][i]) * 1.1
        birdpopmax = np.nanmax(birdpop[birdlocsharedmask][i]) * 1.1
        plt.title(birdloc[birdlocsharedmask][i])
        plt.subplot(1, 2, 1)
        plt.ylim(0, max(muteswanpopmax, birdpopmax))
        plt.plot(xlab, muteswanpop[muteswanlocsharedmask][i], "b.-")
        plt.plot(xlab, birdpop[birdlocsharedmask][i], "r.-")
        plt.legend(["Mute Swan", "{}".format(birdname)])
        plt.xticks(rotation="vertical")
        plt.subplot(1, 2, 2)
        plt.xlim(0, muteswanpopmax)
        plt.ylim(0, birdpopmax)
        plt.plot(muteswanpop[muteswanlocsharedmask][i],
                 birdpop[birdlocsharedmask][i], "g.")
        plt.show()


# Attempt removal of autocorrelation by first difference method (as per email of 25-11-2019)
muteswandiff1stdiff = muteswandiff[:, 1:] - muteswandiff[:, :-1]
birddiff1stdiff = birddiff[:, 1:] - birddiff[:, :-1]
if 7 in plotids:
    plt.plot(muteswandiff1stdiff[muteswanlocsharedmask].flatten(),
             birddiff1stdiff[birdlocsharedmask].flatten(),
             ".")
    plt.show()

# Also by link relatives method {found after search, in source 3}
muteswandifflinkrel = muteswandiff[:, 1:] / muteswandiff[:, :-1]
birddifflinkrel = birddiff[:, 1:] / birddiff[:, :-1]
if 8 in plotids:
    plt.plot(muteswandifflinkrel[muteswanlocsharedmask].flatten(),
             birddifflinkrel[birdlocsharedmask].flatten(),
             ".")
    plt.show()

# Take a look at the profile of values in the data
# Shows up the very very large number of zeroes
if 9 in plotids:
    plt.subplot(2, 1, 1)
    plt.hist([muteswanpop.flatten(), birdpop.flatten()], 50)
    plt.legend(["Mute Swan", birdname])
    plt.xlabel("Population")
    plt.ylabel("Frequency")
    plt.subplot(2, 1, 2)
    plt.hist([muteswandiff.flatten(), birddiff.flatten()], 50)
    plt.xlabel("Change in Population")
    plt.ylabel("Frequency")
    plt.show()

# Try comparing the 40yr trends in increase and decrease (if they exist)
years = np.arange(muteswanpop.shape[1])


def trendgetter(sitedata):
    notnanmask = ~np.isnan(sitedata)  # {Article on missing data in source 4}
    n = np.sum(notnanmask)
    if n != 0:
        m, c, r, p, err = sps.linregress(years[notnanmask], sitedata[notnanmask])
        return m, p, r ** 2, n
    return np.nan, np.nan, np.nan, np.nan


# Get trend data for both datasets
muteswantrenddata = np.float64([trendgetter(sitedata)for sitedata
                                in muteswanpop[muteswanlocsharedmask]])
birdtrenddata = np.float64([trendgetter(sitedata)for sitedata
                            in birdpop[birdlocsharedmask]])
# Set gradients to 0 for all non-significant gradients
# TODO: Ensure that bonferroni shouldn't be used here
# TODO: Figure out whether to do anything with the trends based on 3 or fewer points
muteswantrenddata[muteswantrenddata[:, 1] >= 0.05][:, 0] = 0
birdtrenddata[birdtrenddata[:, 1] >= 0.05][:, 0] = 0
# Determine in which pairs both gradients are significant or fits are good
# TODO: Figure out what R² counts as a good fit, or indeed if should filter by that
significantmask = (muteswantrenddata[:, 1] < 0.05) & (birdtrenddata[:, 1] < 0.05)
goodfitmask = (muteswantrenddata[:, 2] > 0.5) & (birdtrenddata[:, 2] > 0.5)
print(np.nansum(significantmask), np.nansum(goodfitmask),
      np.nansum(significantmask & goodfitmask))
trenddata = [*sps.linregress(muteswantrenddata[goodfitmask][:, 0],
                             birdtrenddata[goodfitmask][:, 0])]
if trenddata[3] >= 0.05:
    trenddata[0] = 0
print(trenddata)
if 10 in plotids:
    plt.plot(muteswantrenddata[goodfitmask][:, 0],
             birdtrenddata[goodfitmask][:, 0], ".")
    trendx = np.arange(int(np.min(muteswantrenddata[goodfitmask][:, 0])),
                       np.max(muteswantrenddata[goodfitmask][:, 0]))
    plt.plot(trendx, (trenddata[0] * trendx) + trenddata[1], "--")
    plt.show()


"""
0 https://stackoverflow.com/a/8251668
1 https://www.oreilly.com/learning/handling-missing-data
2 https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure.add_subplot
3 https://www.svds.com/avoiding-common-mistakes-with-time-series/
4 https://towardsdatascience.com/how-to-handle-missing-data-8646b18db0d4
"""
