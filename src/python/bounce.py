#!/usr/bin/python
from particles import *
from pylab import *
from particleInitialize import *
from OpenGL.GL import *
from OpenGL.GLUT import *
import sys, time


# This program is a 'driver' for a simple simulation of partilces in a box with
# periodic boundary conditions. Your objective will be to complete the code here
# so that you can 'see' the particles with OpenGL.

print "Inside of bounce.py"

tStart = t0 = time.time()

dt = 0.1   # Time step taken by the time integration routine.
L = 10.    # Size of the box.
t = 0      # Initial time

# Particle update data:
COUNT = 1                    # Number of time steps computed
UPDATE_FRAMES = 2            # How often to redraw screen
ADD_PARTICLE_INTERVAL = 10   # How often to add a new particle

# How resolved are the spheres?
STACKS = 25
SLICES = 25

# Instantiate the forces function between particles
f = GranularMaterialForce()
# Create some particles and a box
p = Particles(L,f,periodicY=0)
particleInitialize(p,'one',L)
# Instantiate Integrator
integrate = VerletIntegrator(dt)

def init():
    pass

def draw():
    pass

def idle():
    global COUNT
    for i in range(UPDATE_FRAMES):
       integrate(f,p) # Move the system forward in time
       COUNT = COUNT + 1 
       if mod(COUNT,ADD_PARTICLE_INTERVAL) == 0:
           # Syntax is addParticle(x,y,z,vx,vy,vz,radius)
           # Note y is into page.
           p.addParticle(.25*randn(),L,.25*randn(),0,0,0,.3*randn()+1.)
           f(p)  # Update forces
    glutPostRedisplay()
        
def key(k, x, y):
    pass

def special(k, x, y):
    pass

def reshape(width, height):
    pass

def visible(vis):
    pass
   
if __name__ == '__main__':

    # Open a window
    print "Initializing GLUT";
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(400,400)
    glutCreateWindow('Particle Bounce Extreme')
    glClearColor(0.,0.,0.,1.)
    glutMainLoop();

    # Initialize
    print "Initializing the Particles";
    init()

    # Hand off control to event loop
    glutMainLoop()


