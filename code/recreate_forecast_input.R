# Setup ####
list.of.packages <- c("data.table", "rstudioapi")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
lapply(list.of.packages, require, character.only=T)

wd <- dirname(getActiveDocumentContext()$path) 
setwd(wd)
setwd("../")

# Define CAGR
cagr = function(year_vector, value_vector, base_year, base_value){
  return(
    ((value_vector / base_value) ^ (1 / (year_vector - base_year))) - 1
  )
}

# Load and merge data
funding_w = fread("input/humanitarian_funding_wide.csv", header=T)
funding = melt(funding_w,
               id.vars="sector",
               variable.name="year",
               value.name="received")

requirements_w = fread("input/humanitarian_requirements_wide.csv", header=T)
requirements = melt(requirements_w,
               id.vars="sector",
               variable.name="year",
               value.name="requirement")

dat = merge(funding, requirements)
dat$year = as.numeric(as.character(dat$year))

# Calculate longrungrowth
lrg = dat[,.(
  all_gho_funding=sum(received, na.rm=T)
  ), by=.(year)]

lrg_base = lrg[which.min(lrg$year),]

lrg$longrungrowth = cagr(
  lrg$year, 
  lrg$all_gho_funding,
  lrg_base$year,
  lrg_base$all_gho_funding
)

# Normalize received and requirement, calculate cagr
dat$received_norm = 0
dat$requirement_norm = 0
dat$cagr = 0
for(unique_sector in unique(dat$sector)){
  sector_dat = dat[which(sector == unique_sector),]
  received_sector_dat = sector_dat[which(!is.na(received))]
  received_base_year = min(received_sector_dat$year)
  received_base_value = received_sector_dat$received[which.min(received_sector_dat$year)]
  dat[which(sector == unique_sector),]$received_norm = dat[which(sector == unique_sector),]$received / received_base_value
  dat[which(sector == unique_sector),]$cagr = cagr(
    dat[which(sector == unique_sector),]$year,
    dat[which(sector == unique_sector),]$received,
    received_base_year,
    received_base_value
    )
  requirement_sector_dat = sector_dat[which(!is.na(requirement))]
  requirement_base_value = requirement_sector_dat$requirement[which.min(requirement_sector_dat$year)]
  dat[which(sector == unique_sector),]$requirement_norm = dat[which(sector == unique_sector),]$requirement / requirement_base_value
}
  
# Prioritized
priorities = data.table(
  sector=c("Health", "Protection - Gender-Based Violence"),
  year=c(2020, 2021),
  prioritised=c(1, 1)
)
dat = merge(dat, priorities, by=c("sector", "year"), all.x=T)
dat$prioritised[which(is.na(dat$prioritised))] = 0

# Merge lrg
dat = merge(dat, lrg, by="year", all.x=T)

# Calculate last_year
dat = dat[order(dat$sector, dat$year)]
dat[,"last_year_received_norm":=shift(received_norm),by=.(sector)]

# Recreate regression
fit = lm(
  received_norm~
    requirement_norm+
    last_year_received_norm+
    prioritised+
    cagr+
    longrungrowth,
  data=dat
)
summary(fit)