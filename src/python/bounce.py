from particles import *
from pylab import *
from particleInitialize import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys, time

# BOB -- GL 2.1, GLX 1.4
# Mr. Effarantix -- GL X.X, GLX X.X -- TBA

# This program is a 'driver' for a simple simulation of partilces in a box with
# periodic boundary conditions. Your objective will be to complete the code here
# so that you can 'see' the particles with OpenGL.
SHARED_QUAD = gluNewQuadric()
SCRN_WIDTH = 800.0
SCRN_HEIGHT = 640.0

# Lighting Parameters
LGT_AMB = [0.5, 0.5, 0.5, 1.0]
LGT_DIFF = [1.0, 1.0, 1.0, 1.0]
LGT_POS = [20, 20, 20]


tStart = t0 = time.time()

dt = 0.1   # Time step taken by the time integration routine.
L = 10.0    # Size of the box.
t = 0      # Initial time

# Particle update data:
COUNT = 100                  # Number of time steps computed
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

def init(width, height): 
    print "Initializing the OpenGL scene."
    glClearColor(0.0 ,0.0, 0.0, 1.0) # Clear to black 
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity() 
    gluPerspective(90, width / height, 0.1, 100) # First apply perspective
    glMatrixMode(GL_MODELVIEW)

    glLightfv(GL_LIGHT1, GL_AMBIENT, LGT_AMB)  
    glLightfv(GL_LIGHT1, GL_DIFFUSE, LGT_DIFF)
    glLightfv(GL_LIGHT1, GL_POSITION, LGT_POS)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT1)
    

def draw():
    # First clear the screen. 
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -20.0)

    # Draw the particles as a set of spheres. 
    glPushMatrix()
    for i in range(p.N):
        glPushMatrix()
        x, y, z, r = p.x[i], p.y[i], p.z[i], p.r[i]
        glTranslatef(float(x), float(y), float(z))
        gluSphere(SHARED_QUAD, r, SLICES, STACKS)
        glPopMatrix()    
    glPopMatrix() 

    glutSwapBuffers()
    

def idle():
    global COUNT
    for i in range(UPDATE_FRAMES):
        integrate(f,p) # Move the system forward in time
        COUNT = COUNT + 1 
        if mod(COUNT,ADD_PARTICLE_INTERVAL) == 0:
            # Syntax is addParticle(x,y,z,vx,vy,vz,radius)
            # Note y is into page.
            p.addParticle(.25*randn(),L,.25*randn(),0,0,0,.3*randn()+1.0)
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
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(int(SCRN_WIDTH), int(SCRN_HEIGHT))
    sim_win = glutCreateWindow('Particle Bounce Extreme')

    # Initialize -- What do I initilize here? Is this for freeglut or something else? 
    #print "Initializing the Particles";
    init(int(SCRN_WIDTH), int(SCRN_HEIGHT))

    glutDisplayFunc(draw)
    glutIdleFunc(idle)
    # glutReshapeFunc(reshape)
    # glutKeyboardFunc(key)
    # glutVisibilityFunc(visible)

    # Hand off control to event loop
    glutMainLoop()


