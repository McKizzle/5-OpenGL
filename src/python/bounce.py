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

# Agent Parameters
agent_pos  = [0.0, 0.0, -20.0] # The position of the viewer as (x, y, z)
agent_hdng = [0.0, 0.0] # The orientation of the viewer as (yaw, pitch)

# OpenGL Parameters
persp_enabled = True;

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
    glViewport(0, 0, width, height)
    glClearColor(0.0 ,0.0, 0.0, 1.0) # Clear to black 
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION) # if persp_enabled else glMatrixMode(GL_MODELVIEW)
    glLoadIdentity() 
    if persp_enabled:
        gluPerspective(90, width / height, 0.1, 100)

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
    glTranslatef(agent_pos[0], agent_pos[1], agent_pos[2])
    glRotatef(agent_hdng[0], 0.0, 1.0, 0.0)
    glRotatef(agent_hdng[1], 1.0, 0.0, 0.0)

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

# Key event handler
#   q: exit
#   w: pan forward
#   a: pan left
#   d: pan right
#   s: pan backwards
def key(k, x, y):
    if ord(k) == 27:
        exit()
    elif k == 'w': 
        agent_pos[2] = agent_pos[2] + 0.25
    elif k == 's': 
        agent_pos[2] = agent_pos[2] - 0.25
    elif k == 'a': 
        agent_pos[0] = agent_pos[0] - 0.25
    elif k == 'd': 
        agent_pos[0] = agent_pos[0] + 0.25
    elif k == 'q':
        agent_pos[1] = agent_pos[1] + 0.25
    elif k == 'e':
        agent_pos[1] = agent_pos[1] - 0.25
    elif k == 'p':
        a = 1

# Special key event handler.
#   up key: rotate the model about the x axis counterclockwise.
#   down key: rotate the model about the x axis clockwise
#   right key: rotate hte model about the y axis clockwise.
#   left key: rotate the modle about the y axis counterclockwise
#   <F1>: Print help to console
#   <F2>: toggle perspective
#   <F3>: toggle wireframe
#   <F4>: toggle graph mode
#   <F5>: toggle the universe boundries.
def special(k, x, y):
    if k == GLUT_KEY_UP:
        print "Rotating Down"
        agent_hdng[1] = agent_hdng[1] - 5.0
    elif k == GLUT_KEY_DOWN:
        print "Rotating Up"
        agent_hdng[1] = agent_hdng[1] + 5.0
    elif k == GLUT_KEY_LEFT:
        print "Rotating Left"
        agent_hdng[0] = agent_hdng[0] + 5.0
    elif k == GLUT_KEY_RIGHT:
        print "Rotating Right"
        agent_hdng[0] = agent_hdng[0] - 5.0
    elif k == GLUT_KEY_F2:
        persp_enabled = False if persp_enabled else True 
        print persp_enabled

def reshape(width, height):
    # keep the aspect ratio for the viewport
    scrn_ratio = float(SCRN_HEIGHT) / float(SCRN_WIDTH)

    if(width >= height):
        glViewport(0, 0, int(height / scrn_ratio), int(height))
    else:
        glViewport(0, 0, width, int(scrn_ratio * width))
    

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
    glutReshapeFunc(reshape)
    glutKeyboardFunc(key)
    glutSpecialFunc(special)

    # Hand off control to event loop
    glutMainLoop()


