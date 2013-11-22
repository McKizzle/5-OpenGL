# Load the data
date = "_2013-11-22"

# load the data. 
random_degree = read.csv(file=paste('data/random_deg', date, '.csv',sep=""),
                         header=T, quote='"', row.names = NULL)
random_balls = read.csv(file=paste('data/random_balls', date, '.csv', sep=""), header=T, quote='"', 
                         row.names = NULL)
random_heights = read.csv(file=paste('data/random_heights', date, '.csv', sep=""), header=T, quote='"', 
                         row.names = NULL)
# Load Step
step_degree = read.csv(file=paste('data/step_deg', date, '.csv',sep=""),
                         header=T, quote='"', row.names = NULL)
step_balls = read.csv(file=paste('data/step_balls', date, '.csv',sep=""),
                         header=T, quote='"', row.names = NULL)
step_heights = read.csv(file=paste('data/step_heights', date, '.csv',sep=""),
                         header=T, quote='"', row.names = NULL)

# Load RStep
rstep_degree = read.csv(file=paste('data/rstep_deg', date, '.csv',sep=""),
                         header=T, quote='"', row.names = NULL)
rstep_balls = read.csv(file=paste('data/rstep_balls', date, '.csv',sep=""),
                         header=T, quote='"', row.names = NULL)
rstep_heights = read.csv(file=paste('data/rstep_heights', date, '.csv',sep=""),
                         header=T, quote='"', row.names = NULL)

# Load Binary
binary_degree = read.csv(file=paste('data/binary_deg', date, '.csv',sep=""),
                         header=T, quote='"', row.names = NULL)
binary_balls = read.csv(file=paste('data/binary_balls', date, '.csv',sep=""),
                         header=T, quote='"', row.names = NULL)
binary_heights = read.csv(file=paste('data/binary_heights', date, '.csv',sep=""),
                         header=T, quote='"', row.names = NULL)
