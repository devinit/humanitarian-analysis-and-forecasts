# Setup ####
list.of.packages <- c("data.table", "ggplot2", "scales", "rstudioapi")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
lapply(list.of.packages, require, character.only=T)

wd <- dirname(getActiveDocumentContext()$path) 
setwd(wd)
setwd("../")

# Load ####
dat = fread("input/regression_input.csv")

# Regression analysis ####
fit = lm(
  received~
    requirement+
    last_year_received+
    prioritised+
    cagr+
    longrungrowth,
  data=dat
)
summary(fit)

# Create hypothetical 2023 data
# In real analysis we will need to update requirements
# and CAGR/ Long Run Growth.
new_dat = subset(dat, year == 2022)
new_dat$last_year_received = new_dat$received
new_dat$received = NULL
new_dat$year = 2023

# Forecast based on fit model and new data
confidence = predict.lm(fit, newdata = new_dat, interval = "confidence")
new_dat$received_fit = confidence[,1]
new_dat$received_lwr = confidence[,2]
new_dat$received_upr = confidence[,3]

fwrite(new_dat, "output/humanitarian_forecast.csv")

# Quick chart
new_dat$received = new_dat$received_fit
all_dat = rbind(
  dat,
  new_dat,
  fill=T
)
sectors = c("Education","Protection","Water Sanitation Hygiene")
ggplot(subset(all_dat, sector %in% sectors), aes(x=year, y=received, group=sector, color=sector)) +
  geom_line()
