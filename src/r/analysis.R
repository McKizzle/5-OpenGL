source('src/r/helpers.R')

date = "_2013-11-22"

# load the data. 
random_degree = read.csv(file=paste('data/random_deg', date, '.csv',sep=""),
                         header=T, quote='"', row.names = NULL)
random_balls = read.csv(file=paste('data/random_balls', date, '.csv', sep=""), header=T, quote='"', 
                         row.names = NULL)
random_heights = read.csv(file=paste('data/random_heights', date, '.csv', sep=""), header=T, quote='"', 
                         row.names = NULL)



