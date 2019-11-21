# Script first worked on: 2019-11-20
# By: Charles S Turvey

rm(list=ls())

library(tidyr)
library(dplyr)
library(lubridate)
library(ggplot2)

setwd("D://Users//Charles Turvey//Documents//Course Materials//Year 4//SOES6071 Independent Research Project//SWANS")
CanadaGoose = read.csv("WeBS Data Scraper//BirdCSVs//Canada Goose.csv")
