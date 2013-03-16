#!python
'''This file contains the interface handler for Mind Garden.'''
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import gevent
##import openepoc as oe

import time

##import openepoc as oe

world = None
novelty = None
t0 = time.time()

def init(garden):
    global world
    global novelty
    global t0
    world = garden

##    cluster = oe.api.create_cluster('mindgarden', 'envelope')
##    novelty = oe.api.get_novelty_queue(cluster)
    
    glutDisplayFunc(redraw)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyfunc)
    glutIdleFunc(idle)

    t0 = time.time()
    
def redraw():
    global world
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    world.render()
    glutSwapBuffers()

def reshape(x, y):
    aspect = float(x)/float(y)

    glViewport(0, 0, x, y)
 
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(40, aspect, 1, 50)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0,-3,-12)

def keyfunc(key, x, y):
    '''The callback function for keyboard presses.'''
    if key == 27 or key == 'q' or key == 'Q':
##        oe.api.close_epoc()
        exit(0)

def idle():
    global world
    global novelty
    global t0

##    try:
##        ans = novelty.get_nowait()
##        print str(ans) + " " # + str(time.time() - t0) 
##        if ans == -1:
##            world.tree.add_child()
####        elif ans == 1:
####            print "CHANGED " + str(time.time() - t0)
##    except gevent.queue.Empty:
##        gevent.sleep(0)
    if time.time() - t0 > .1:
        world.tree.add_child()
        t0 = time.time()
    else:
        pass
    glutPostRedisplay()
