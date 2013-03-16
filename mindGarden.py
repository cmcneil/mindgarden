#!python
import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import mgworld
import mginterface


print "Beginning Mind Garden"
xRes = int(sys.argv[1])
yRes = int(sys.argv[2])

glutInit()
glutInitWindowSize(xRes, yRes)
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
glutCreateWindow("M I N D  G A R D E N")



world = mgworld.World()
mginterface.init(world)

glutMainLoop()
