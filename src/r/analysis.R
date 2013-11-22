rm(list=ls())

source('src/r/helpers.R')
source('src/r/load_data.R')

vib.range <- function(df) {
  vib <- which(df$isVibrating == 'True')
  vib <- range(vib)
  return(vib)
}

cols.to.ignore <- c("state", "mode", "isVibrating")

# generate time series plots for the degree of the balls.
#row.names(random_degree)
random_deg_quarts   <- calc.quartiles(random_degree, cols.to.ignore)
step_deg_quarts     <- calc.quartiles(step_degree, cols.to.ignore)
rstep_deg_quarts    <- calc.quartiles(rstep_degree, cols.to.ignore)
binary_deg_quarts   <- calc.quartiles(binary_degree, cols.to.ignore)

plot.quartiles(random_deg_quarts, smoothing=F, vib.range=vib.range(random_degree))
plot.quartiles(step_deg_quarts, smoothing=F, vib.range=vib.range(step_degree))
plot.quartiles(rstep_deg_quarts, smoothing=F, vib.range=vib.range(rstep_degree))
plot.quartiles(binary_deg_quarts, smoothing=F, vib.range=vib.range(binary_degree))

# x <- c(200, 300, 300, 200)
# rng <- range(random_deg_quarts)
# y <- c(0, 0, rng[2], rng[2])
# 
# polygon(y~x, col='green')

