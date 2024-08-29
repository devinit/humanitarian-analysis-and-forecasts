# Setup ####
list.of.packages <- c("data.table", "rstudioapi")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
lapply(list.of.packages, require, character.only=T)

wd <- dirname(getActiveDocumentContext()$path) 
setwd(wd)
setwd("../")

dat_txt = readLines("input/cash_hub_2021.txt")
dat_txt = paste(dat_txt, collapse="")
dat_txt_lines = strsplit(dat_txt, split=";", fixed=T)[[1]]

header = strsplit(dat_txt_lines[1], split="|", fixed=T)[[1]]
header = sapply(header, trimws)

dat_list = list()
dat_index = 1

for(i in 2:length(dat_txt_lines)){
  row = strsplit(dat_txt_lines[i], split="|", fixed=T)[[1]]
  tmp = data.frame(t(row[2:9]))
  names(tmp) = header
  dat_list[[dat_index]] = tmp
  dat_index = dat_index + 1
}

dat = rbindlist(dat_list)
dat$`Total Cash Expended (CHF)` = as.numeric(gsub(",","",dat$`Total Cash Expended (CHF)`))
dat$`Number of beneficiaries` = as.numeric(dat$`Number of beneficiaries`)

stopifnot({
  sum(dat$`Number of beneficiaries`) ==
    7491136
})

stopifnot({
  round(sum(dat$`Total Cash Expended (CHF)`)) ==
    round(916857127.43)
})
fwrite(dat, "output/cash_hub_2021.csv")