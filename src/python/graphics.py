from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Drawing functions
def draw_spheres(x, y, z, r, N):
    glPushMatrix()
    for i in range(N):
        glPushMatrix()
        glTranslatef(float(x), float(y), float(z))
        gluSphere(SHARED_QUAD, r, STACKS, SLICES)
        glPopMatrix() 
    glPopMatrix()

class Painter:
    def __init__(self):
        self.__quadratic = gluNewQuadric()
        self.__sphere_stacks = 25
        self.__sphere_slices = 25
        self.__glContext = None

    """
    x 1D array of x values
    y 1D array of y values
    z 1D array of z values
    r 1D array of radius values
    N the length of x, y, z, and r
    """
    def spheres(self, x, y, z, r, N):
        self.__glContext.glPushMatrix()
        for i in range(N):
            self.__glContext.glPushMatrix()
            gself.__glContext.lTranslatef(float(x), float(y), float(z))
            #gluSphere(self.__quadratic, r, self.__sphere_stacks, self.__sphere_slices)
            self.__glContext.glPopMatrix() 
        self.__glContext.glPopMatrix()


