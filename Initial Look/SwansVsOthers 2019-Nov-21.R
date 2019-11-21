# Script first worked on: 2019-11-20
# By: Charles S Turvey

# Clear and setup
rm(list=ls())
library(tidyr)
library(dplyr)
library(lubridate)
library(ggplot2)

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
# Some more thought should be put into whether these numbers should actually all be used.
MuteSwanPop = select(MuteSwan, starts_with("Pop"))
MuteSwanPop = lapply(MuteSwanPop, function(x) as.numeric(gsub("[^0-9]", "", x)))
MuteSwanPop = mutate(as.data.frame(MuteSwanPop), Site=MuteSwan$Site)
CanadaGoosePop = select(CanadaGoose, starts_with("Pop"))
CanadaGoosePop = lapply(CanadaGoosePop, function(x) as.numeric(gsub("[^0-9]", "", x)))
CanadaGoosePop = mutate(as.data.frame(CanadaGoosePop), Site=CanadaGoose$Site)
MallardPop = select(Mallard, starts_with("Pop"))
MallardPop = lapply(MallardPop, function(x) as.numeric(gsub("[^0-9]", "", x)))
MallardPop = mutate(as.data.frame(MallardPop), Site=Mallard$Site)

# Save Rdata files for later
setwd("D://Users//Charles Turvey//Documents//Course Materials//Year 4//SOES6071 Independent Research Project//SWANS//Initial Look")
save(MuteSwan, file="MuteSwanRaw.Rdata")
save(CanadaGoose, file="CanadaGooseRaw.Rdata")
save(Mallard, file="MallardRaw.Rdata")
save(MuteSwanPop, file="MuteSwanPop.Rdata")
save(CanadaGoosePop, file="CanadaGoosePop.Rdata")
save(MallardPop, file="MallardPop.Rdata")
