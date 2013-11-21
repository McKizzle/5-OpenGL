#!/usr/bin/env python

from particles import *
from pylab import *
from particleInitialize import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys, time

# BOB -- GL 2.1, GLX 1.4
# Mr. Effarantix -- GL X.X, GLX X.X

PAUSE = False
FORCE_MODE = False

# This program is a 'driver' for a simple simulation of partilces in a box with
# periodic boundary conditions. Your objective will be to complete the code here
# so that you can 'see' the particles with OpenGL.
SHARED_QUAD = gluNewQuadric()
SLICES = 25
STACKS = 25
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

# Simulation Parameters
dt = 0.1   # Time step taken by the time integration routine. (Also the frame rate)
L = 10.0    # Size of the box.
t = 0      # Initial time

# Useful arrays to draw cubes
box_verts = np.array([
        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
        [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
        ])
box_edgs = np.array([
        [0, 1], [1, 2], [2, 3], [3, 0], 
        [0, 4], [1, 5], [2, 6], [3, 7],
        [4, 5], [5, 6], [6, 7], [7, 4]
        ])
box_faces = np.array([
        [0, 1, 2, 3],
        [1, 5, 6, 2],
        [3, 2, 6, 7],
        [0, 3, 7, 4],
        [1, 5, 4, 0],
        [5, 6, 7, 4]
        ])


# Particle Update Data:
FRAME = 0
FRAME_RATE_MULTIPLIER = 6    # Increase the speed of the frames. (6 == 60fps)
ADD_PARTICLE_INTERVAL = 10   # How often to add a new particle
MAX_PARTICLES = 100          # When to stop adding particles.

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

    # Draw the universe boundries
    glPushMatrix()
    glDisable(GL_LIGHTING)
    glBegin(GL_LINES)
    glColor4f(0.0, 1.0, 0.0, 1.0) # Green
    for i in [0, 1, 3, 5, 9, 8, 11, 4]:
        edge = box_edgs[i] 
        glVertex3fv((L / 2) * box_verts[edge[0]])
        glVertex3fv((L / 2) * box_verts[edge[1]])
    glEnd() 
    glEnable(GL_LIGHTING)
    glPopMatrix()

    # Draw the particles as a set of spheres.  
    if not FORCE_MODE:
        glPushMatrix()
        for i in range(p.N):
            x, y, z, r = p.x[i], p.y[i], p.z[i], p.r[i]
            glPushMatrix() 
            glTranslatef(float(x), float(y), float(z))
            gluSphere(SHARED_QUAD, r, SLICES, STACKS)
            glPopMatrix()    
        glPopMatrix()
    else:
        glColor4f(1.0, 1.0, 0.0, 1.0) # Yellow
        glDisable(GL_LIGHTING)
        for i in range(p.N):
            x, y, z, r = p.x[i], p.y[i], p.z[i], p.r[i]
            glPointSize(r * 5)
            glBegin(GL_POINTS)
            glVertex3d(x, y, z)
            glEnd()

        # Now draw the forces. 
        glColor4f(1.0, 0.0, 0.0, 1.0) # Red
        dr = p.dr.tolist()
        for i in range(1, len(dr)):
            sdr = dr[i]
            for j in range(1, len(sdr)):
                frc = sdr[j]
                if (i != j) and (frc > 0):
                    glLineWidth(frc * 5)
                    glBegin(GL_LINES)
                    p1 = [p.x[i], p.y[i], p.z[i]]
                    p2 = [p.x[j], p.y[j], p.z[j]]
                    glVertex3fv(p1)
                    glVertex3fv(p2)
                    glEnd()
                    glLineWidth(1.0)
        glEnable(GL_LIGHTING)
    
    glutSwapBuffers()

def mouse(button, state, x, y):
    pass

# Force the simulation to update at a constant rate. 
# not properly implemented 
#   FIXME dt is not being properly used
# to upate the simulation relative to time. 
def timer(v):
    integrate(f, p)
    
    global FRAME
    FRAME = FRAME + 1
    if mod(FRAME, ADD_PARTICLE_INTERVAL) == 0 and p.N < MAX_PARTICLES: 
        p.addParticle( 0.25 * randn(), L, 0.25 * randn(), 0, 0, 0, 0.3 * randn() + 1.0)

    glutPostRedisplay()
    if not PAUSE:
        glutTimerFunc(int(dt * 1000 / FRAME_RATE_MULTIPLIER), timer, 1) 

    ## Calculate the connection degree of each sphere. 
    #d = p.distanceMatrix(p.x,p.y,p.z)[0] 
    #dr = d - triu(p.sumOfRadii) - tril(p.sumOfRadii)    # Compute overlap
    #dr[dr>0]=0  # No forces arising in no overlap cases
    #dr = abs(dr) 

    #dr = dr.tolist()
    


def idle():
    glutPostRedisplay()

# Key event handler
#   q: exit
#   w: pan forward
#   a: pan left
#   d: pan right
#   s: pan backwards
#   p: pause simulation
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
        global PAUSE
        PAUSE = True if not PAUSE else False
        glutTimerFunc(10, timer, FRAME)

# Special key event handler.
#   up key: rotate the model about the x axis counterclockwise.
#   down key: rotate the model about the x axis clockwise
#   right key: rotate hte model about the y axis clockwise.
#   left key: rotate the modle about the y axis counterclockwise
#   <F1>: Print help to console
#   <F3>: toggle wireframe
#   <F4>: toggle graph mode
#   <F5>: toggle the universe boundries.
#   <F8>: toogle interaction mode.
#       if interaction mode draw balls as points and edges as acting forces
#   <F9>: print the frame number
def special(k, x, y):
    if k == GLUT_KEY_UP:
        # print "Rotating Down"
        agent_hdng[1] = agent_hdng[1] + 5.0
    elif k == GLUT_KEY_DOWN:
        # print "Rotating Up"
        agent_hdng[1] = agent_hdng[1] - 5.0
    elif k == GLUT_KEY_LEFT:
        # print "Rotating Left"
        agent_hdng[0] = agent_hdng[0] - 5.0
    elif k == GLUT_KEY_RIGHT:
        # print "Rotating Right"
        agent_hdng[0] = agent_hdng[0] + 5.0
    #elif k == GLUT_KEY_F2:
    #    vPort = glGetIntegerv(GL_VIEWPORT)
    #    global persp_enabled
    #    if persp_enabled:
    #        persp_enabled = False
    #        glMatrixMode(GL_PROJECTION)
    #        glLoadIdentity()
    #        gluPerspective(90, vPort[2] / vPort[3], 0.1, 100)     
    #        glMatrixMode(GL_MODELVIEW)
    #    else:
    #        perp_enabled = True
    #        glMatrixMode(GL_PROJECTION)
    #        glLoadIdentity()
    #        glOrtho(0, vPort[2], 0, vPort[3], 0, 100)     
    #        glMatrixMode(GL_MODELVIEW)
    #    print vPort
    elif k == GLUT_KEY_F3:
        wireframe = True
    elif k == GLUT_KEY_F8:
        global FORCE_MODE
        FORCE_MODE = False if FORCE_MODE else True
    elif k == GLUT_KEY_F9:
        print "FRAME: %s" % FRAME 
        # Calculate overlap areas.  
        # Find position differences
        d = p.distanceMatrix(p.x,p.y,p.z)[0] 
        dr = d - triu(p.sumOfRadii) - tril(p.sumOfRadii)    # Compute overlap
        dr[dr>0]=0  # No forces arising in no overlap cases
        dr = abs(dr)
        print dr

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
    glutMouseFunc(mouse)
    
    # Start the timer.
    glutTimerFunc(10, timer, FRAME)

    # Hand off control to event loop
    glutMainLoop()



