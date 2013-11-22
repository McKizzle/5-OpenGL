#!/usr/bin/env python

from particles import *
from pylab import *
from particleInitialize import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from collections import defaultdict
import sys, time
import csv
import datetime

# BOB -- GL 2.1, GLX 1.4
# Mr. Effarantix -- GL X.X, GLX X.X

# Files to write to
RECORD = False
RECORD_TO_FILE = False
MODE = 1 # Corresponds to keys 0 to disable
CSV_DEG_FILE = ""
CSV_HEIGHT_FILE = ""
CSV_BALLS_FILE = ""
DATE = str(datetime.date.today()) + "_NEW_"

PAUSE = False
FORCE_MODE = False
DISP_VEL = False

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
agent_pos  = [0.0, 0.0, 0.0] # The position of the viewer as (x, y, z)
agent_hdng = [0.0, 0.0] # The orientation of the viewer as (yaw, pitch)

# OpenGL Parameters
persp_enabled = True;

# Simulation Parameters
dt = 0.1   # Time step taken by the time integration routine. (Also the frame rate)
L = 15.0    # Size of the box.
t = 0      # Initial time

# Agent Parameters
agent_pos  = [0.0, 0.0, -L * 2] # The position of the viewer as (x, y, z)
agent_hdng = [0.0, 0.0] # The orientation of the viewer as (yaw, pitch)

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
FRAME_RATE_MULTIPLIER = 6   # Increase the speed of the frames. (6 == 60fps)
SAMPLE = 0                  # Sample counter
SAMPLE_INTERVAL = 20        # Sample the system once every 20 frames
SAMPLE_BEGIN_VIBRATION = 200 # Start vibrating at             200
SAMPLE_END_VIBRATION = 300   # Stop vibrating at              300
MAX_SAMPLES = 400            # The maximum number of samples: 400
ADD_PARTICLE_INTERVAL = 10  # How often to add a new particle
MAX_PARTICLES = 200         # When to stop adding particles: 200

# Instantiate the forces function between particles
f = GranularMaterialForce()
f.__fcdt = dt # step taken by floor motion
# Create some particles and a box
p = Particles(L,f,periodicY=0) # keeps the simulator from crashing.
p.add_mode = 'binary'
p.max_particles = MAX_PARTICLES
#particleInitialize(p,'one',L)
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
        for i in range(0, len(dr)):
            sdr = dr[i]
            for j in range(0, len(sdr)):
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

    # Draw the velocities
    if DISP_VEL:
        glColor4f(1.0, 1.0, 1.0, 1.0)  
        glDisable(GL_LIGHTING)
        glBegin(GL_LINES)
        for i in range(p.N):
            xyz1 = np.array([p.x[i], p.y[i], p.z[i]])
            vxyz = np.array([p.vx[i], p.vy[i], p.vz[i]])
            xyz2 = xyz1 + vxyz
            glVertex3fv(xyz1)
            glVertex3fv(xyz2)
        glEnd()
        glEnable(GL_LIGHTING)

    
    glutSwapBuffers()

def mouse(button, state, x, y):
    pass

# Force the simulation to update at a constant rate. 
def timer(v):
    integrate(f, p)

    #print "Particles: %d" % p.N
    
    global FRAME
    FRAME = FRAME + 1
    if mod(FRAME, ADD_PARTICLE_INTERVAL) == 0 and p.N < MAX_PARTICLES: 
        #p.addParticle( 0.25 * randn(), L, 0.25 * randn(), 0, 0, 0, 0.3 * randn() + 1.0)
        p.add() 
    
    # Sampeling interval 
    global SAMPLE
    global RECORD
    global MODE
    if (FRAME % SAMPLE_INTERVAL == 0) and RECORD and SAMPLE < MAX_SAMPLES:
        # Calcuate the  degree of each sphere. 
        dr = p.dr.tolist() 
        deg = [0] * p.max_particles
        for i in range(0, len(dr)):
            sdr = dr[i]
            for j in range(0, len(sdr)):
                frc = sdr[j]
                if (i != j) and (frc > 0):
                    deg[i] = deg[i] + 1

        # Determine the mode.
        if p.N < MAX_PARTICLES:
            state = 'seeding'
            mode = p.add_mode
            vibrating = f.vibrate_floor
        else:
            state = 'seeded'
            mode = p.add_mode
            vibrating = f.vibrate_floor
        
        pz = p.z.tolist()
        for i in range(len(pz), p.max_particles):
            pz.append(0)

        pz.append(state)
        deg.append(state)
        pz.append(mode)
        deg.append(mode)
        pz.append(vibrating)
        deg.append(vibrating) 
        append_csv(CSV_DEG_FILE, deg)
        append_csv(CSV_HEIGHT_FILE, pz)

        if SAMPLE == SAMPLE_BEGIN_VIBRATION:
            f.vibrate_floor = True
        if SAMPLE == SAMPLE_END_VIBRATION:
            f.vibrate_floor = False

        SAMPLE = SAMPLE + 1
    elif SAMPLE == MAX_SAMPLES and RECORD:
        RECORD = False
        # write ball radii to a file
        colnames = range(0, p.max_particles - 1)
        pr = p.r
        #print CSV_BALLS_FILE
        new_csv(CSV_BALLS_FILE, colnames)
        append_csv(CSV_BALLS_FILE, pr)
    elif not RECORD and SAMPLE == MAX_SAMPLES and MODE <= 3 and MODE > 0:
        MODE = MODE + 1
        print "MODE: %d" % MODE
        RECORD = True
        SAMPLE = 0
        key(str(MODE), 0, 0)

    glutPostRedisplay()
    if not PAUSE:
        glutTimerFunc(int(dt * 1000 / FRAME_RATE_MULTIPLIER), timer, 1)
    

def idle():
    glutPostRedisplay()

# Key event handler
#   q: exit
#   w: pan forward
#   a: pan left
#   d: pan right
#   s: pan backwards
#   p: pause simulation
#   = or +: speed up the simulation
#   - or _: slow down the simulation
def key(k, x, y):
    global FRAME_RATE_MULTIPLIER
    global PAUSE
    global f
    global RECORD
    global CSV_DEG_FILE
    global CSV_HEIGHT_FILE
    global CSV_BALLS_FILE
    global DISP_VEL
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
        PAUSE = True if not PAUSE else False
        glutTimerFunc(10, timer, FRAME)
    elif k == '=' or k == '+':
        FRAME_RATE_MULTIPLIER = FRAME_RATE_MULTIPLIER + 1
        print "Frame Rate: %s" % FRAME_RATE_MULTIPLIER
    elif k == '-' or k == '_':
        if FRAME_RATE_MULTIPLIER > 1:
            FRAME_RATE_MULTIPLIER = FRAME_RATE_MULTIPLIER - 1
        print "Frame Rate: %s" % FRAME_RATE_MULTIPLIER
    elif k == 'v': # enable disable floor vibration
        f.vibrate_floor = True if not f.vibrate_floor else False
    elif k == 'V': # enable disable velocities
        print "Display velocities: %s" % DISP_VEL
        DISP_VEL = True if not DISP_VEL else False
    elif k == '1':
        print "Random Seeding"
        RECORD = True
        csv_file = '../../data/random' 
        CSV_DEG_FILE = csv_file + '_deg_' + DATE + '.csv'
        CSV_HEIGHT_FILE = csv_file + '_heights_' + DATE + '.csv'
        CSV_BALLS_FILE = csv_file + '_balls_' + DATE + '.csv'
        p.change_add_mode('random')

        colnames = range(0, p.max_particles)
        colnames.append('state')
        colnames.append('mode')
        colnames.append('isVibrating')
        new_csv(CSV_HEIGHT_FILE, colnames)
        new_csv(CSV_DEG_FILE, colnames)
    elif k == '2':
        print "Step Seeding"
        RECORD = True
        csv_file = '../../data/step' 
        CSV_DEG_FILE = csv_file + '_deg_' + DATE + '.csv'
        CSV_HEIGHT_FILE = csv_file + '_heights_' + DATE + '.csv'
        CSV_BALLS_FILE = csv_file + '_balls_' + DATE + '.csv'
        p.change_add_mode('step')

        colnames = range(0, p.max_particles)
        colnames.append('state')
        colnames.append('mode')
        colnames.append('isVibrating')
        new_csv(CSV_HEIGHT_FILE, colnames)
        new_csv(CSV_DEG_FILE, colnames)
    elif k == '3':
        print "Reverse Step Seeding"
        RECORD = True
        csv_file = '../../data/rstep' 
        CSV_DEG_FILE = csv_file + '_deg_' + DATE + '.csv'
        CSV_HEIGHT_FILE = csv_file + '_heights_' + DATE + '.csv'
        CSV_BALLS_FILE = csv_file + '_balls_' + DATE + '.csv'
        p.change_add_mode('rstep')

        colnames = range(0, p.max_particles)
        colnames.append('state')
        colnames.append('mode')
        colnames.append('isVibrating')
        new_csv(CSV_HEIGHT_FILE, colnames)
        new_csv(CSV_DEG_FILE, colnames)
    elif k == '4':
        print "Binary Seeding"
        RECORD = True
        csv_file = '../../data/binary' 
        CSV_DEG_FILE = csv_file + '_deg_' + DATE + '.csv'
        CSV_HEIGHT_FILE = csv_file + '_heights_' + DATE + '.csv'
        CSV_BALLS_FILE = csv_file + '_balls_' + DATE + '.csv'
        p.change_add_mode('binary')
        
        colnames = range(0, p.max_particles)
        colnames.append('state')
        colnames.append('mode')
        colnames.append('isVibrating')
        new_csv(CSV_HEIGHT_FILE, colnames)
        new_csv(CSV_DEG_FILE, colnames)


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

def new_csv(path, colnames):
    if RECORD_TO_FILE:
        csvfile = open(path, 'wb')
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(colnames)

def append_csv(path, row):
    if RECORD_TO_FILE:
        csvfile = open(path, 'a')
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(row)

   
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




