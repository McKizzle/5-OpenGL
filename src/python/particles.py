#!/usr/bin/env python

from numpy import * 
from pylab import rand, randn
from particleInitialize import *

# print "Inside of particles.py"

# PARTICLES MODULE:
# This set of classes was developed to model interacting spherical particles in 3
# dimensions. There are presently two types of interaction forces possible. Each
# is a class
#
# GranularMaterialsForce: This is a force that represents elastic forces between
# particles that are overlapping, and a damping, or dissipative force. It does
# not include the often used rotational degrees of freedom. Also note that the
# constraint forces are taken care of with an extra function call.
# 
# LennardJonesForce: This force describes the weak attraction at large distances
# and strong repulsion experienced at close distances by mono-atomic gases.
#
# The equation of motion are integrated by the Verlet method, which is presently
# the only integration scheme supported.
#
# All particle data (position, velocity, acceleration, radii, and distances) are
# stored in the Particles class. 

# 9/23/08 JVJ and Tim Bocek

class GranularMaterialForce:

    def __init__(self, k = 1.5, gamma = .3, g = .25):
        # parameters in force model
        self.__k = k          # Elastic 'bounce'
        self.__gamma = gamma  # Energy dissipation/loss
        self.__g = g          # Gravity
        self.__fcds = 0       # Starting position difference of the floor
        self.__fcdt = 0.1     # Time step 
        self.vibrate_floor = False

    def __call__(self, p):
        # Find position differences
        d, dx, dy, dz = p.distanceMatrix(p.x,p.y,p.z)
        
        # Compute overlap
        dr = d - triu(p.sumOfRadii) - tril(p.sumOfRadii)        

        # No forces arising in no overlap cases
        dr[dr>0]=0

        p.dr = abs(dr) # Store the forces for later use

        # Compute elastic particle/particle forces
        magnitude = -self.__k * dr

        # Velocity differences
        dv, dvx, dvy, dvz = p.distanceMatrix(p.vx,p.vy,p.vz)

        # Damping terms
        vijDotrij = dvx * dx + dvy * dy + dvz * dz
        vijDotrij[dr==0] = 0.

        # Damping is subtracted from force
        magnitude = magnitude - self.__gamma *  vijDotrij / d

        magnitude[d==-1] = 0

        cx, cy, cz = self.floorConstraint(p)

        # Project onto components, sum all forces on each particle
        p.ax =  sum(magnitude * (-dx/d) * p.ratioOfRadii,axis=1) + cx
        p.ay =  sum(magnitude * (-dy/d)* p.ratioOfRadii,axis=1) - self.__g + cy
        p.az =  sum(magnitude * (-dz/d)* p.ratioOfRadii,axis=1) + cz

    def floorConstraint(self,p):
        " "" This is a highly specific function for a floor that responds (elasticity and damping) the same way a particle does. Presently, if constraints are to change, one would have to rewrite the function."" "
        effectiveRadius = 3. # This is how 'hard' the floor is
        if self.vibrate_floor:
            floorDistance = p.y + p.L/2 - p.r + 4 * sin((self.__fcds + (randn()/2)) * 0.5) # a the 'vibration' to the floor
        else:
            floorDistance = p.y + p.L/2 - p.r 

        floorDistance[floorDistance > 0] = 0
        lowerWallForce = -self.__k * floorDistance
        lowerWallDamping = -self.__gamma * p.vy * floorDistance
        lowerWallForce = lowerWallForce - lowerWallDamping
        cx = 0
        cy = lowerWallForce * effectiveRadius / p.r
        cz = 0
        
        # Update the floor postition.
        self.__fcds = self.__fcds + (self.__fcdt * pi / 2)

        return cx, cy, cz

class VerletIntegrator:

    def __init__(self,dt=0.01):
        # Time step
        self.__dt = dt

    def __call__(self,force,p):
        # Position update
        p.x = p.x + p.vx * self.__dt + .5 * p.ax * self.__dt ** 2
        p.y = p.y + p.vy * self.__dt + .5 * p.ay * self.__dt ** 2
        p.z = p.z + p.vz * self.__dt + .5 * p.az * self.__dt ** 2

        # Update periodic BC
        p.pbcUpdate()

        # Store accelerations for averaging that is done 
        ax=p.ax
        ay=p.ay
        az=p.az

        force(p) # Force update with new positions

        # Velocity updates
        p.vx = p.vx + 0.5 * (ax + p.ax) * self.__dt
        p.vy = p.vy + 0.5 * (ay + p.ay) * self.__dt
        p.vz = p.vz + 0.5 * (az + p.az) * self.__dt


class Particles:

    def __init__(self,L,force,periodicX = 1,periodicY=1,periodicZ=1):
        # Container size
        self.L = L
        # Total Number of particles
        self.N = 0
        # type
        self.type = 'float32'
        # Positions
        self.x = array([],dtype=self.type)
        self.y = array([],dtype=self.type)
        self.z = array([],dtype=self.type)
        # Velocities
        self.vx = array([],dtype=self.type)
        self.vy = array([],dtype=self.type)
        self.vz = array([],dtype=self.type)
        # Forces
        self.ax = array([],dtype=self.type)
        self.ay = array([],dtype=self.type)
        self.az = array([],dtype=self.type)
        # Radii
        self.r = array([],dtype=self.type)
        # Periodic on?
        self.periodicX = periodicX 
        self.periodicY = periodicY 
        self.periodicZ = periodicZ 
        # Force function
        self.f = force

        # Force matrix
        self.dr = None

        # Add particle mode settings
        self.add_mode = 'random' # random, step, rstep, binary
        self.min_radius = 1.0
        self.max_radius = 2.0
        self.max_particles = 10
        self.steps = 10
  
        particleInitialize(self,'one', self.L) # initizialize with a single particle
    
    # Resets everything and changes the add mode. 
    def change_add_mode(self, mode):
        # Total number of particles 
        self.N = 0 
        # Positions
        self.x = array([],dtype=self.type)
        self.y = array([],dtype=self.type)
        self.z = array([],dtype=self.type)
        # Velocities
        self.vx = array([],dtype=self.type)
        self.vy = array([],dtype=self.type)
        self.vz = array([],dtype=self.type)
        # Forces
        self.ax = array([],dtype=self.type)
        self.ay = array([],dtype=self.type)
        self.az = array([],dtype=self.type)
        # Radii
        self.r = array([],dtype=self.type)
        # Mode
        self.add_mode = mode
        
        particleInitialize(self, 'one', self.L)
        

    def add(self):
        if self.add_mode == 'random':
            self.addParticle(0.25 * randn(), self.L, 0.25 * randn(), 0, 0, 0, 0.3 * randn() + 1.01)
        elif self.add_mode == 'step':
            rrange = self.max_radius - self.min_radius
            dt_rrange = rrange / self.steps
            curr_step = float(int(self.N / (self.max_particles / self.steps)))
            radius = curr_step * dt_rrange + self.min_radius
            self.addParticle(0.25 * randn(), self.L, 0.25 * randn(), 0, 0, 0, radius)
        elif self.add_mode == 'rstep':
            rrange = self.max_radius - self.min_radius
            dt_rrange = rrange / self.steps
            curr_step = float(int(self.N / (self.max_particles / self.steps)))
            radius = self.max_radius - curr_step * dt_rrange 
            self.addParticle(0.25 * randn(), self.L, 0.25 * randn(), 0, 0, 0, radius)
        elif self.add_mode == 'binary':
            if self.N % 2 == 0:
                self.addParticle(0.25 * randn(), self.L, 0.25 * randn(), 0, 0, 0, float(self.max_radius))
            else:
                self.addParticle(0.25 * randn(), self.L, 0.25 * randn(), 0, 0, 0, float(self.min_radius))
        else:
            print 'Uncaught Mode'
       
    def addParticle(self,x,y,z,vx,vy,vz,r):
        self.x = hstack((self.x,x))
        self.y = hstack((self.y,y))
        self.z = hstack((self.z,z))
        self.vx = hstack((self.vx,vx))
        self.vy = hstack((self.vy,vy))
        self.vz = hstack((self.vz,vz))
        self.r = hstack((self.r,r))
        self.N = self.N+1
        temp = tile(self.r,(self.N,1))
        self.sumOfRadii = temp + temp.T # what does .T do? Transpose the numpy array
        self.ratioOfRadii = temp / temp.T
        self.f(self)

    def pbcUpdate(self):
        " ""Moves paricles across periodic boundary"" "
        if self.periodicX:
            self.x[self.x > self.L/2]  = self.x[self.x > self.L/2]  - self.L
            self.x[self.x < -self.L/2] = self.x[self.x < -self.L/2] + self.L
        if self.periodicY:
            self.y[self.y > self.L/2]  = self.y[self.y > self.L/2]  - self.L
            self.y[self.y < -self.L/2] = self.y[self.y < -self.L/2] + self.L
        if self.periodicZ:
            self.z[self.z > self.L/2]  = self.z[self.z > self.L/2]  - self.L
            self.z[self.z < -self.L/2] = self.z[self.z < -self.L/2] + self.L

    def distanceMatrix(self,x,y,z):
        " ""Computes distances between all particles and places the result in a matrix such that the ij th matrix entry corresponds to the distance between particle i and j"" " 
        xtemp = tile(x,(self.N,1))
        dx = xtemp - xtemp.T
        ytemp = tile(y,(self.N,1))
        dy = ytemp - ytemp.T
        ztemp = tile(z,(self.N,1))
        dz = ztemp - ztemp.T
     
        # Particles 'feel' each other across the periodic boundaries (that explains why they bunch into a box)
        if self.periodicX:
            dx[dx>self.L/2]=dx[dx > self.L/2]-self.L
            dx[dx<-self.L/2]=dx[dx < -self.L/2]+self.L
        if self.periodicY:
            dy[dy>self.L/2]=dy[dy>self.L/2]-self.L
            dy[dy<-self.L/2]=dy[dy<-self.L/2]+self.L
        if self.periodicZ:
            dz[dz>self.L/2]=dz[dz>self.L/2]-self.L
            dz[dz<-self.L/2]=dz[dz<-self.L/2]+self.L

        # Total Distances
        d = sqrt(dx**2+dy**2+dz**2)

        # Mark zero entries with negative 1 to avoid divergences
        d[d==0] = -1

        return d, dx, dy, dz


