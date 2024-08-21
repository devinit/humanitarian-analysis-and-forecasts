# Setup ####
list.of.packages <- c("data.table", "ggplot2", "scales", "rstudioapi")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
lapply(list.of.packages, require, character.only=T)

wd <- dirname(getActiveDocumentContext()$path) 
setwd(wd)
setwd("../")

# Analysis ####

# \copy (select year, recipient_name, recipient_iso3_code, region_name, sum(usd_disbursement_deflated) from crs_current where usd_disbursement_deflated > 0 and sector_code in (720, 730, 740) group by year, recipient_name, recipient_iso3_code, region_name) to 'input/protracted_crises_crs.csv' csv header;
# Load data created by above psql
dat = fread('input/protracted_crises_crs.csv')

# Calculate per-country minimum.maximum years for later use
dat.years = dat[,.(min.year=min(year), max.year=max(year)), by=(recipient_name)]

# Expand grid so dataset has value for every country/year combination
codes = unique(dat[,c("recipient_name", "recipient_iso3_code", "region_name")])
dat_grid = expand.grid(
  year = min(dat$year):max(dat$year),
  recipient_iso3_code = unique(dat$recipient_iso3_code)
)
dat = merge(dat, dat_grid, all=T)
dat[,c("recipient_name", "region_name")] = NULL
dat = merge(dat, codes, by="recipient_iso3_code", all.x=T)

# Remove regional aggregates and NAs
dat = subset(dat, !endsWith(recipient_iso3_code, "_X"))
dat$sum[which(is.na(dat$sum))] = 0

# Remove rows which were outside of the min/max range of original data
for(i in 1:nrow(dat.years)){
  row = dat.years[i,]
  recip = row$recipient_name
  min.year = row$min.year
  max.year = row$max.year
  dat = subset(
    dat,
    recipient_name != recip |
      (year >= min.year & year <= max.year)
  )
}

# Calculate lagged value
dat = dat[order(dat$recipient_name, dat$year)]
dat[,"sum_t1":=shift(sum),by=.(recipient_name)]

# Regression
fit = lm(sum~sum_t1, data=dat)
summary(fit)

# Turn lagged value into boolean
dat$this_year_greater_than_last = dat$sum > dat$sum_t1
mean(dat$this_year_greater_than_last, na.rm=T)

# Aggregate regional
regional_protracted = dat[,.(
  prob=mean(this_year_greater_than_last, na.rm=T),
  sum=sum(sum, na.rm=T)
), by=.(region_name)]
regional_protracted = regional_protracted[order(-regional_protracted$prob),]
regional_protracted$region_name = factor(
  regional_protracted$region_name, levels=regional_protracted$region_name
)
fwrite(regional_protracted, "output/protracted_by_region.csv")

# Aggregate country
country_protracted = dat[,.(
  prob=mean(this_year_greater_than_last, na.rm=T),
  sum=sum(sum, na.rm=T)
), by=.(recipient_name)]
country_protracted = country_protracted[order(-country_protracted$prob),]
country_protracted$recipient_name = factor(
  country_protracted$recipient_name, levels=unique(country_protracted$recipient_name)
)
fwrite(country_protracted, "output/protracted_by_country.csv")

# Visualize ####

reds = c(
  "#e84439", "#f8c1b2", "#f0826d", "#bc2629", "#8f1b13", "#fce3dc", "#fbd7cb", "#f6b0a0", "#ec6250", "#dc372d", "#cd2b2a", "#a21e25", "#6b120a"
)
oranges = c(
  "#eb642b", "#f6bb9d", "#f18e5e", "#d85b31", "#973915", "#fde5d4", "#fcdbbf", "#facbad", "#f3a47c", "#ee7644", "#cb5730", "#ac4622", "#7a2e05"
)
yellows = c(
  "#f49b21", "#fccc8e", "#f9b865", "#e48a00", "#a85d00", "#feedd4", "#fee7c1", "#fedcab", "#fac47e", "#f7a838", "#df8000", "#ba6b15", "#7d4712"
)
pinks = c(
  "#c2135b", "#e4819b", "#d64278", "#ad1257", "#7e1850", "#f9cdd0", "#f6b8c1", "#f3a5b6", "#e05c86", "#d12568", "#9f1459", "#8d0e56", "#65093d"
)
purples = c(
  "#893f90", "#c189bb", "#a45ea1", "#7b3b89", "#551f65", "#ebcfe5", "#deb5d6", "#cb98c4", "#af73ae", "#994d98", "#732c85", "#632572", "#42184c"
)
blues = c(
  "#0089cc", "#88bae5", "#5da3d9", "#0071b1", "#0c457b", "#d3e0f4", "#bcd4f0", "#a3c7eb", "#77adde", "#4397d3", "#105fa3", "#00538e", "#0a3a64"
)
greens = c(
  "#109e68", "#92cba9", "#5ab88a", "#1e8259", "#16513a", "#c5e1cb", "#b1d8bb", "#a2d1b0", "#74bf93", "#3b8c61", "#00694a", "#005b3e", "#07482e"
)
greys = c(
  "#6a6569", "#a9a6aa", "#847e84", "#555053", "#443e42", "#d9d4da", "#cac5cb", "#b3b0b7", "#b9b5bb", "#5a545a", "#736e73", "#4e484c", "#302b2e"
)

di_style = theme_bw() +
  theme(
    panel.border = element_blank()
    ,panel.grid.major.x = element_blank()
    ,panel.grid.minor.x = element_blank()
    ,panel.grid.major.y = element_line(colour = greys[2])
    ,panel.grid.minor.y = element_blank()
    ,panel.background = element_blank()
    # ,plot.background = element_blank()
    ,axis.line.x = element_line(colour = "black")
    ,axis.line.y = element_blank()
    ,axis.ticks = element_blank()
    ,legend.position = "bottom"
  )

rotate_x_text_45 = theme(
  axis.text.x = element_text(angle = 45, vjust = 1, hjust=1)
)
rotate_y_text_45 = theme(
  axis.text.y = element_text(angle = 45, vjust = 1, hjust=1)
)

# Chart regional
p1 = ggplot(regional_protracted, aes(x=region_name, y=prob)) +
  geom_bar(stat="identity", fill=reds[1]) +
  scale_y_continuous(
    label=percent, 
    expand = c(0, 0),
    limits = c(0, max(regional_protracted$prob) * 1.05)
  ) +
  di_style +
  rotate_x_text_45 +
  labs(x="", y="", title=
         paste0(
           "Probability of humanitarian assistance being greater than\nthe previous year's value (n=",
           format(nrow(dat), big.mark=","),
           ")"
         )
       )
p1
ggsave(filename="output/region_bar_chart.png", plot=p1, height=7, width=14)

# Chart country
limit = 15
p2 = ggplot(country_protracted[1:limit], aes(x=recipient_name, y=prob)) +
  geom_bar(stat="identity", fill=reds[1]) +
  scale_y_continuous(
    label=percent, 
    expand = c(0, 0),
    limits = c(0, max(country_protracted[1:limit]$prob) * 1.05)
  ) +
  di_style +
  rotate_x_text_45 +
  labs(x="", y="", title=
         paste0(
           "Probability of humanitarian assistance being greater than\nthe previous year's value (n=",
           format(
             nrow(subset(dat, recipient_name %in% country_protracted[1:limit]$recipient_name)),
             big.mark=","),
           ")"
         )
  )
p2
ggsave(filename="output/country_bar_chart.png", plot=p2, height=7, width=14)

