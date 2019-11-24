# Script First Worked on: 2019-11-23
# By: Charles S Turvey

import csv
import matplotlib.pyplot as plt
import numpy as np
import re

muteswanfile = open("../WeBS Data Scraper/BirdCSVs/Mute Swan.csv")
birdfile = open("../WeBS Data Scraper/BirdCSVs/Canada Goose.csv")
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

muteswanheader = np.object_(muteswantable[0])
muteswandata = np.object_(muteswantable[1:-1])
muteswanloc = muteswandata[:, 0]
print("\n" + str(muteswanheader), "\n")

birdheader = np.object_(birdtable[0])
birddata = np.object_(birdtable[1:-1])
birdloc = birddata[:, 0]
print("\n" + str(birdheader), "\n")

muteswanpop = muteswandata[:, 1:-5]
print(muteswanpop.shape)
birdpop = birddata[:, 1:-5]

# Function that finds all the strings containing non-numeric characters, vectorised for use on the data
nonnumericmatcher = np.vectorize(lambda x: bool(re.compile("[^0-9]").search(x)))


# Function that deals with the non-numeric strings
def charstripper(x):
    # Converts incomplete counts (start with "(") and nans (start with "nan") to None
    if re.match(r"\(|nan", x):
        return None
    # And strips the supplementary info off of those counts that have it
    return int("".join(re.match("[0-9,]+", x)[0].split(",")))


# Vectorised for use on the data
charstripper = np.vectorize(charstripper)

# Strip out all the incomplete counts, nans, supplementary notes
nonnumericmask = nonnumericmatcher(muteswanpop)
muteswanpop[nonnumericmask] = charstripper(muteswanpop[nonnumericmask])
muteswanpop[~nonnumericmask] = np.int32(muteswanpop[~nonnumericmask])
nonnumericmask = nonnumericmatcher(birdpop)
birdpop[nonnumericmask] = charstripper(birdpop[nonnumericmask])
birdpop[~nonnumericmask] = np.int32(birdpop[~nonnumericmask])

xlab = ["{:02d}-{:02d}".format(i, i + 1) for i in np.arange(98, 118) % 100]
for i, site in enumerate(muteswanloc[:10]):
    print(list(muteswanpop[i, :]))
    plt.plot(xlab, list(muteswanpop[i, :]))
plt.legend(muteswanloc)
plt.show()

for i, site in enumerate(birdloc[:10]):
    print(list(birdpop[i, :]))
    plt.plot(xlab, list(birdpop[i, :]))
plt.legend(birdloc)
plt.show()


