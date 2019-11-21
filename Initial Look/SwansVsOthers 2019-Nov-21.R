# Script first worked on: 2019-11-20
# By: Charles S Turvey

# Clear and setup
rm(list=ls())
library(tidyr)
library(dplyr)
library(lubridate)
library(ggplot2)
library(reshape2)

# Get the data scraped off the site by the python script
setwd("D://Users//Charles Turvey//Documents//Course Materials//Year 4//SOES6071 Independent Research Project//SWANS")
MuteSwan = read.csv("WeBS Data Scraper//BirdCSVs//Mute Swan.csv")
CanadaGoose = read.csv("WeBS Data Scraper//BirdCSVs//Canada Goose.csv")
Mallard = read.csv("WeBS Data Scraper//BirdCSVs//Mallard.csv")
glimpse(MuteSwan)
glimpse(CanadaGoose)
glimpse(Mallard)

# Rename the column headers sensibly (ALWAYS CHECK THE GLIMPSE FIRST)
yearstrings = sprintf("%02i", (98:118) %% 100)
header = c("Site",
           paste("Pop", yearstrings[1:20], ".", yearstrings[2:21], sep=""),
           "MonthOfMax18",
           "Mean5yrMoving",
           "Mean5yr13.14.17.18",
           "WebPageNo",
           "RoughAccessTime")
names(MuteSwan) = header
names(CanadaGoose) = header
names(Mallard) = header

# Check that there aren't any spurious numbers in the supplementary notes
apply(select(MuteSwan, starts_with("Pop")), 2, function(x) grep("[0-9]+[^0-9.,]+[0-9]", x))
apply(select(CanadaGoose, starts_with("Pop")), 2, function(x) grep("[0-9]+[^0-9.,]+[0-9]", x))
apply(select(Mallard, starts_with("Pop")), 2, function(x) grep("[0-9]+[^0-9.,]+[0-9]", x))

# Strip out all the non-number characters (brackets on incomplete counts removed, supplementary notes removed)
# TODO: Some more thought should be put into whether these numbers should actually all be used.
MuteSwanPop = select(MuteSwan, starts_with("Pop"))
MuteSwanPop = lapply(MuteSwanPop, function(x) as.numeric(gsub("[^0-9]", "", x)))
MuteSwanPop = mutate(as.data.frame(MuteSwanPop), Site=MuteSwan$Site)
MuteSwanPop = select(MuteSwanPop, c(Site, starts_with("Pop")))
CanadaGoosePop = select(CanadaGoose, starts_with("Pop"))
CanadaGoosePop = lapply(CanadaGoosePop, function(x) as.numeric(gsub("[^0-9]", "", x)))
CanadaGoosePop = mutate(as.data.frame(CanadaGoosePop), Site=CanadaGoose$Site)
CanadaGoosePop = select(CanadaGoosePop, c(Site, starts_with("Pop")))
MallardPop = select(Mallard, starts_with("Pop"))
MallardPop = lapply(MallardPop, function(x) as.numeric(gsub("[^0-9]", "", x)))
MallardPop = mutate(as.data.frame(MallardPop), Site=Mallard$Site)
MallardPop = select(MallardPop, c(Site, starts_with("Pop")))

# See what sites are shared by swans and the others
MS.CG.SharedSites = intersect(MuteSwanPop$Site, CanadaGoosePop$Site)
MS.M.SharedSites = intersect(MuteSwanPop$Site, MallardPop$Site)

# But the number of rows returned seems to indicate a lot of duplicate site names
dim(filter(MuteSwanPop, Site %in% MS.M.SharedSites))
dim(filter(MallardPop, Site %in% MS.M.SharedSites))
duplicateSites = MallardPop$Site[duplicated(MallardPop$Site) | rev(duplicated(rev(MallardPop$Site)))]
# But the duplicates have individual sets of data.
# TODO: read into the docs on why this is.
glimpse(MallardPop[MallardPop$Site == duplicateSites[10],])
MallardPop$Site[grep(duplicateSites[100], MallardPop$Site)]

# Get differential population data
header = c(sprintf("Diff%02i", (99:117) %% 100))
MuteSwanPopDiff = select(MuteSwanPop, c(-Site, -contains("98"))) - select(MuteSwanPop, c(-Site, -contains("18")))
names(MuteSwanPopDiff) = header
MuteSwanPopDiff = mutate(MuteSwanPopDiff, Site=MuteSwanPop$Site)
MuteSwanPopDiff = select(MuteSwanPopDiff, c(Site, starts_with("Diff")))
CanadaGoosePopDiff = select(CanadaGoosePop, c(-Site, -contains("98"))) - select(CanadaGoosePop, c(-Site, -contains("18")))
names(CanadaGoosePopDiff) = header
CanadaGoosePopDiff = mutate(CanadaGoosePopDiff, Site=CanadaGoosePop$Site)
CanadaGoosePopDiff = select(CanadaGoosePopDiff, c(Site, starts_with("Diff")))
MallardPopDiff = select(MallardPop, c(-Site, -contains("98"))) - select(MallardPop, c(-Site, -contains("18")))
names(MallardPopDiff) = header
MallardPopDiff = mutate(MallardPopDiff, Site=MallardPop$Site)
MallardPopDiff = select(MallardPopDiff, c(Site, starts_with("Diff")))

# Ignoring the duplicates problem, get rows of differential data according to list of shared sites
MS.CG.FlatMuteSwanPopDiff = melt(MuteSwanPopDiff[match(MS.CG.SharedSites, MuteSwanPopDiff$Site), ], id="Site")
MS.CG.FlatCanadaGoosePopDiff = melt(CanadaGoosePopDiff[match(MS.CG.SharedSites, CanadaGoosePopDiff$Site), ], id="Site")
plot(MS.CG.FlatMuteSwanPopDiff$value, MS.CG.FlatCanadaGoosePopDiff$value,
     xlab="Change in Max Mute Swan Population [#/yr]", ylab="Change in Max Canada Goose Population [#/yr]",
     col=rgb(20, 10, 20, 15, maxColorValue=40), pch=20)
# This plot appears to show a lot of 0 in a big +
# Try zooming in
focus = (abs(MS.CG.FlatCanadaGoosePopDiff$value) < 10000) & (abs(MS.CG.FlatMuteSwanPopDiff$value) < 2000)
plot(MS.CG.FlatMuteSwanPopDiff$value[focus], MS.CG.FlatCanadaGoosePopDiff$value[focus],
     xlab="Change in Max Mute Swan Population [#/yr]", ylab="Change in Max Canada Goose Population [#/yr]",
     col=rgb(20, 10, 20, 15, maxColorValue=40), pch=20)
# Some sanity checking
plot(lm(MS.CG.FlatCanadaGoosePopDiff$value ~ MS.CG.FlatMuteSwanPopDiff$value))
max(select(MuteSwanPop, starts_with("Pop")), na.rm=T)
max(select(MuteSwanPopDiff, starts_with("Diff")), na.rm=T)
max(select(CanadaGoosePop, starts_with("Pop")), na.rm=T)
max(select(CanadaGoosePopDiff, starts_with("Diff")), na.rm=T)
# And now for Mallard
MS.M.FlatMuteSwanPopDiff = melt(MuteSwanPopDiff[match(MS.M.SharedSites, MuteSwanPopDiff$Site), ], id="Site")
MS.M.FlatMallardPopDiff = melt(MallardPopDiff[match(MS.M.SharedSites, MallardPopDiff$Site), ], id="Site")
plot(MS.M.FlatMuteSwanPopDiff$value, MS.M.FlatMallardPopDiff$value,
     xlab="Change in Max Mute Swan Population [#/yr]", ylab="Change in Max Mallard Population [#/yr]",
     col=rgb(10, 20, 20, 15, maxColorValue=40), pch=20)
# Try zooming in
focus = (abs(MS.M.FlatMallardPopDiff$value) < 10000) & (abs(MS.M.FlatMuteSwanPopDiff$value) < 2000)
plot(MS.M.FlatMuteSwanPopDiff$value[focus], MS.M.FlatMallardPopDiff$value[focus],
     xlab="Change in Max Mute Swan Population [#/yr]", ylab="Change in Max Mallard Population [#/yr]",
     col=rgb(10, 20, 20, 15, maxColorValue=40), pch=20)
# Some sanity checking
plot(lm(MS.M.FlatMallardPopDiff$value ~ MS.M.FlatMuteSwanPopDiff$value))
max(select(MallardPop, starts_with("Pop")), na.rm=T)
max(select(MallardPopDiff, starts_with("Diff")), na.rm=T)

# Save Rdata files for later
setwd("D://Users//Charles Turvey//Documents//Course Materials//Year 4//SOES6071 Independent Research Project//SWANS//Initial Look")
save(MuteSwan, file="MuteSwanRaw.Rdata")
save(CanadaGoose, file="CanadaGooseRaw.Rdata")
save(Mallard, file="MallardRaw.Rdata")
save(MuteSwanPop, file="MuteSwanPop.Rdata")
save(CanadaGoosePop, file="CanadaGoosePop.Rdata")
save(MallardPop, file="MallardPop.Rdata")
save(MuteSwanPopDiff, file="MuteSwanPopDiff.Rdata")
save(CanadaGoosePopDiff, file="CanadaGoosePopDiff.Rdata")
save(MallardPopDiff, file="MallardPopDiff.Rdata")
