#!python

import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import numpy as np
import random
import Image
import sys


class Texture(object):
    '''This class contains the data structure for Textures used for texture
        mapping and their associated methods.'''
    def __init__(self, filename='blank.png'):
        self.texfile = open(filename)
        im = Image.open(self.texfile)
        ix, iy, image = (im.size[0], im.size[1],
                         im.tostring("raw", "RGB", 0, -1))

        self.id = glGenTextures(1)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.id)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, ix, iy, 0, GL_RGB,
                     GL_UNSIGNED_BYTE, image)

    def init_texture(self):
        '''Makes render-time opengl initialization.'''
        glBindTexture(GL_TEXTURE_2D, self.id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        
class ShinySurface(object):
    '''A class for controlling the shiny moving surface.'''
    def __init__(self, world):
        self.grid_size = 150.0
        self.show_axis = False

        self.world = world
        
        self.disp_list = glGenLists(1)
        glNewList(self.disp_list, GL_COMPILE)
        self.display()
        glEndList()

        self.rho = -80
        self.theta = 0
        
        self.texture = Texture("sky-round.png")
        self.texture.init_texture()
        self.read_shaders("shiny_vert.glsl", "shiny_frag.glsl")

    def display(self):
        '''Specifies the display list to be sent to GPU.'''
        size = 5.0
        du = 2 * size / self.grid_size
        dv = 2 * size / self.grid_size

        glColor(0, 1, 0)
        for u in np.arange(-size, size, du):
            glBegin(GL_TRIANGLE_STRIP)
            for v in np.arange(-size, size, dv):
                glVertex(u, v)
                glVertex(u+du, v)
            glEnd()

        glUseProgram(0)
        glPopMatrix()

        if self.show_axis:
            glColor3f(0, 1, 0)
            glBegin(GL_LINES)
            glVertex3f(-5,0,0)
            glVertex3f(5,0,0)
            glVertex3f(0,-5,0)
            glVertex3f(0,5,0)
            glEnd()

    def render(self):
        t = glutGet(GLUT_ELAPSED_TIME) * -0.001

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glRotatef(self.rho, 1, 0, 0)
        glRotatef(self.theta, 0, 1, 0)

        glUseProgram(self.shader_program)
        glUniform1f(self.t_glsl, t)
        glUniform4f(self.bgcolor_glsl, *self.world.bgcolor)

        glCallList(self.disp_list)

    def read_shaders(self, vert, frag):
        self.shader_program = glCreateProgram()

        self.vert_shader = glCreateShader(GL_VERTEX_SHADER)
        vert_file = open(vert, "r")
        glShaderSource(self.vert_shader, vert_file.read())
        glCompileShader(self.vert_shader)

        self.frag_shader = glCreateShader(GL_FRAGMENT_SHADER)
        frag_file = open(frag, "r")
        glShaderSource(self.frag_shader, frag_file.read())
        glCompileShader(self.frag_shader)
        print glGetShaderInfoLog(self.frag_shader)
        glAttachShader(self.shader_program, self.vert_shader)
        glAttachShader(self.shader_program, self.frag_shader)

        glLinkProgram(self.shader_program)
        glUseProgram(self.shader_program)

        self.sky_glsl = glGetUniformLocation(self.shader_program, "sky")
        self.t_glsl = glGetUniformLocation(self.shader_program, "t")
        self.mode_glsl = glGetUniformLocation(self.shader_program, "mode")
        self.bgcolor_glsl = glGetUniformLocation(self.shader_program, "bgcolor")

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        glUniform1i(self.sky_glsl, 0)

class Tree(object):
    def __init__(self):
        self.scale = 1.0
        self.spread = 3.5
        self.level = 0
        self.theta = 0
        self.phi = 0
        self.pos = np.array([0.01, 0.0, 0.0])
        self.final_pos = self.pos
        self.branch = gluNewQuadric()
        self.branch_width = 0.04
        self.bulb_rad = 0.2
        self.branching_factor = 3
        self.grow_rate = 0.0002
        self.rot_rate = 0.02
        
        gluQuadricNormals(self.branch, GL_SMOOTH)
        
        self.root = Node(self, self)
        self.root.max_children = 6
        self.root.final_pos[2] -=1

        self.disp_list = glGenLists(1)
##        glNewList(self.disp_list, GL_COMPILE)

    def add_child(self):
        self.root.add_child()

    def draw_branch(self, p1, p2, width=None):
        if width == None:
            width = self.branch_width
        draw_cylinder(p1, p2, width, 10, self.branch)
        

    def render(self):
        t = glutGet(GLUT_ELAPSED_TIME) * -self.rot_rate
        glDisable(GL_TEXTURE_2D)
        glNewList(self.disp_list, GL_COMPILE)
        
        glPushMatrix()
        glRotate(t, 0, 1, 0)
        self.root.render()

        glPushMatrix()
        glRotate(-90, 1, 0, 0)
        self.draw_branch(self.pos, self.root.pos, 0.07)
        glPopMatrix()
        glPopMatrix()

        glEndList()
        glCallList(self.disp_list)
        glEnable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        

class Node(object):
    def __init__(self, tree, parent):
        self.tree = tree
        self.parent = parent
        self.t0 = glutGet(GLUT_ELAPSED_TIME)

        self.bulb_rad = self.parent.bulb_rad * 0.81
        self.branch_width = self.parent.branch_width * 0.85

        self.rho = 0
        self.theta = 0
        self.phi = 0
        self.pos = np.copy(self.parent.pos) # x, y, z
        
        self.level = self.parent.level + 1
        self.final_pos = self.calc_pos("bio")
        self.done_growing = False
        self.children = []
        self.max_children = self.tree.branching_factor

    def add_child(self):
        if len(self.children) < self.max_children:
            self.children.append(Node(self.tree, self))
        else:
            random.choice(self.children).add_child()

    def calc_pos(self, mode):
        '''Calculates the position based on the position of the parent.'''
        pos = np.array([0.0, 0.0, 0.0])

        if mode == "bio":
            self.rho = 3.0 * 1.0 / np.power(float(self.level + 1), 2.0 / 3.0)
            self.theta = random.random() * 2.0 * np.pi
            self.phi = random.random() * np.pi / 2.0
            
            if self.level == 1:
                self.phi = 0.0
            if self.level == 2:
                self.phi = np.pi / 4.0
                self.theta = random.random() * 2.0 * np.pi
                
            pos[0] = self.parent.final_pos[0] + self.rho * np.sin(self.phi) * np.sin(self.theta)
            pos[1] = self.parent.final_pos[1] + self.rho * np.sin(self.phi) * np.cos(self.theta)
            pos[2] = self.parent.final_pos[2] + self.rho * np.cos(self.phi)
        
        elif mode == "sphere":
            self.rho = self.tree.scale * np.sqrt(self.level)
            spread = (self.level > 1) * self.tree.spread / self.rho
            self.theta = self.parent.theta + 0.1*(np.abs(self.parent.phi) - 45) * spread*(random.random() - 0.5)
            self.phi = np.clip(self.parent.phi +
                               0.7 * spread*(random.random() - 0.5), -np.pi / 4.0, np.pi / 4.0)

            pos[0] = self.rho * np.sin(self.phi) * np.sin(self.theta)
            pos[1] = self.rho * np.sin(self.phi) * np.cos(self.theta)
            pos[2] = self.rho * np.cos(self.phi)
        return pos

    def grow_branch(self):
        '''Updates the position to reflect how much the branch has grown.'''
        t_pass = glutGet(GLUT_ELAPSED_TIME) - self.t0
        length = self.tree.grow_rate * t_pass
        d = self.final_pos - self.parent.final_pos
        final_length = np.linalg.norm(d)
        u = d / final_length
        if length > final_length:
            length = final_length
        self.pos = self.parent.pos + length * u

    def render(self):
        self.grow_branch()
            
        glPushMatrix()
        glColor(0.0, 0.8, 0.0)
        glRotate(-90, 1, 0, 0)
        for child in self.children:
            self.tree.draw_branch(self.pos, child.pos, width=self.branch_width)
        glTranslate(*self.pos)
        glEnable(GL_LIGHTING)
        
        glMaterialfv(GL_FRONT, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
        glMaterialfv(GL_FRONT, GL_SHININESS, 30.0)
        t = glutGet(GLUT_ELAPSED_TIME) * -0.005
        osc = np.abs((np.sin(t) + 1)/2.0)
        glMaterialfv(GL_FRONT, GL_EMISSION, (0.0, 0.5 * osc, 0.2 * osc, 0.0))
        glutSolidSphere(self.bulb_rad, 10, 10)
        glMaterialfv(GL_FRONT, GL_EMISSION, (0.0, 0.0, 0.0, 0.0))
        glPopMatrix()
        for child in self.children:
            child.render()

class World(object):
    def __init__(self):
        self.bgcolor = (0.839215, 0.94117, 0.94117, 1.0)
        self.topcolor = (0.52156, 0.8, 0.8039, 1.0)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE,1)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT,GL_DIFFUSE)
        
        black = (0,0,0,0)
        glMaterial(GL_FRONT,GL_AMBIENT,black)
        glMaterial(GL_FRONT,GL_SPECULAR,black)
        glLight(GL_LIGHT0, GL_POSITION, (7.0, 2.0, 3.0, 1.0))

        glClearColor(*self.bgcolor)

        glEnable(GL_DEPTH_TEST)
        
        self.shiny = ShinySurface(self)
        self.tree = Tree()

    def render_bg(self):
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        
        glColor(*self.bgcolor)
        glVertex(-10,2, -5)
        glVertex(10,2, -5)

        glColor(*self.topcolor)
        glVertex(10,10, -5)
        glVertex(-10,10, -5)

        glEnd()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)

    def render(self):
        self.render_bg()
        self.shiny.render()
        self.tree.render()

def draw_cylinder(p1, p2, radius, subdiv, quadric):
    '''Draws a cylinder between two vertices.'''
    x1 = p1
    x2 = p2

    v = x2 - x1
    if v[2] == 0:
        v[2] = 0.0001

    norm = np.linalg.norm(v)
    ax = 57.2957795 * np.arccos(v[2] / norm)

    if v[2] < 0.0:
        ax = -ax
    rx = -v[1]*v[2]
    ry = v[0]*v[2]
    glPushMatrix()

    glTranslate(*x1)
    glRotate(ax, rx, ry, 0.0)
    gluQuadricOrientation(quadric, GLU_OUTSIDE)
    gluCylinder(quadric, radius, radius, norm, subdiv, 1)

##    gluQuadricOrientation(quadric, GLU_INSIDE)
##    gluDisk(quadric, 0.0, radius, subdiv, 1)
##    glTranslate(0, 0, norm)
##
##    gluQuadricOrientation(quadric, GLU_OUTSIDE)
##    gluDisk(quadric, 0.0, radius, subdiv, 1)
    glPopMatrix()
