''' 
	Isabella Jorissen
	HW No. 4: Bezier Curves
	3.14.15
	Math 385
'''

import sys
import numpy
from geometry import point, vector, EPSILON, ORIGIN
from random import random
from math import sin, cos, acos, pi, sqrt, factorial

from OpenGL.GLUT import *
from OpenGL.GL import *

width = 500
height = 500
ctl_pts = None
m_pts = None
k_degree = 2
radius = 5.0
pointSize = 14
iproj = None
org = point(0.0,0.0,0.0)

smoothness = 10

def init():
	global ctl_pts, m_pts

	#set the control points for a triangle
	c0 = point((radius-1),0,0)
	c1 = point((1-radius),0,0)
	c2 = point(0,(radius-1),0)
	ctl_pts = [c0, c1, c2]

	#subdivide into three curves m = [] = array of midpoints 
	m0 = c0.plus(c1.minus(c0).scale(.5))
	m1 = c1.plus(c2.minus(c1).scale(.5))
	m2 = c2.plus(c0.minus(c2).scale(.5))
	m_pts = [m0,m1,m2]


#this function determines whether or not a click event occurs on top of a control point
def intersectCtrlPt(ctw):
	for i in range(len(ctl_pts)):
		diff = ctw.minus(ctl_pts[i])
		if diff.norm() < ((pointSize*2*radius)/width):
			return [True, i, diff]
	return False
	

def bernsteinPolys(u):
	bps = []
	#the Bernstein polynomials defined for k = 2:
	for i in range(k_degree + 1):
		polyi = factorial(k_degree) / (factorial(i) * factorial(k_degree-i)) 
		polyi *= pow(u, i)
		polyi *= pow((1-u), (k_degree-i))
		bps.append(polyi)
	return bps

#a (sadly) non-recursive algorithm to approximate a bezier curve 
#note: didn't use point.combo(scalar, other) because it doesn't work correctly
def deCasteljau(pts, u):
	dcsum = org
	bps = bernsteinPolys(u)
	for i in range(k_degree + 1):
		ctrdir = org.minus(pts[i])
		ctrdir = ctrdir.scale(bps[i])
		termi = org.plus(ctrdir)

		dcdir = org.minus(termi)
		dcsum = dcsum.plus(dcdir)
	return dcsum

def display():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()

	#draw the control points and midpoints
	glPointSize(pointSize)
	glBegin(GL_POINTS)
	for i in range(len(ctl_pts)):
		glColor(.4, .6, .8)
		ctl_pts[i].glVertex3()
		glColor(.8, .8, .2)
		m_pts[i].glVertex3()
	glEnd()


	#connect the control points with a line (bounding triangle)
	glBegin(GL_LINE_LOOP)
	for i in range(len(ctl_pts)):
		glColor(.8, .6, .4)
		ctl_pts[i].glVertex3()
	glEnd()

	dcasta = []
	dcastb = []
	dcastc = []

	for i in range(smoothness):
		u = i*1.0/(smoothness - 1.0)

		#define the three curves and their control points
		ctl_pta = [m_pts[0], ctl_pts[1], m_pts[1]]
		ctl_ptb = [m_pts[1], ctl_pts[2], m_pts[2]]
		ctl_ptc = [m_pts[2], ctl_pts[0], m_pts[0]] 

		#perform approximation alg on each one
		dcasta.append(deCasteljau(ctl_pta, u))
		dcastb.append(deCasteljau(ctl_ptb, u))
		dcastc.append(deCasteljau(ctl_ptc, u))

	glPointSize(pointSize/2)
	#draw the points from the results
	glBegin(GL_POINTS)
	for vert in dcasta:
		glColor(.5, .5, .5)
		vert.glVertex3()
	for vert in dcastb:
		glColor(.9, .2, .8)
		vert.glVertex3()
	for vert in dcastc:
		glColor(.4, .8, .4)
		vert.glVertex3()
	glEnd()

	#connect all of the points
	glBegin(GL_LINE_LOOP)
	for vert in dcasta:
		glColor(.5, .5, .5)
		vert.glVertex3()
	for vert in dcastb:
		glColor(.9, .2, .8)
		vert.glVertex3()
	for vert in dcastc:
		glColor(.4, .8, .4)
		vert.glVertex3()
	glEnd()


	glFlush()

def screenToWorldCoords(x, y):
	xnew = (2.0*x/width) - 1.0
	ynew = 1.0 - (2.0*y/height)
	ctw = [xnew, ynew, 0.0, 0.0]

	for i in range(len(iproj)):
		ctw[i] = iproj[i][i]*ctw[i]

	return point(ctw[0], ctw[1], ctw[2])

def mouseDrag(x, y):
	global ctl_pts, m_pts
	ctwpt = screenToWorldCoords(x, y)
	res = intersectCtrlPt(ctwpt)
	if res:
		i = res[1]
		diff = res[2]
		ctl_pts[i] = ctl_pts[i].plus(diff)
		#recalculate midpoints
		m0 = ctl_pts[0].plus(ctl_pts[1].minus(ctl_pts[0]).scale(.5))
		m1 = ctl_pts[1].plus(ctl_pts[2].minus(ctl_pts[1]).scale(.5))
		m2 = ctl_pts[2].plus(ctl_pts[0].minus(ctl_pts[2]).scale(.5))
		m_pts = [m0,m1,m2]
		glutPostRedisplay()


def mouseProcess(btn, state, x, y):
	ctwpt = screenToWorldCoords(x, y)
	# print (str(intersectCtrlPt(ctwpt)))
	# if btn == GLUT_LEFT_BUTTON:
	# 	if state is not GLUT_DOWN:
	# 		print ('right click (x, y): ' + str(x) + " " + str(y))
	# 		print ('proj coord click (x, y): ' + str(ctwpt.components()))


def myKeyFunc(key, x, y):
	""" Handle a "normal" keypress. """
	# Handle ESC key.
	if key == b'\033':  
	# "\033" is the Escape key
			sys.exit(1)

def resize(w, h):
	""" Register a window resize by changing the viewport.  """
	global width, height, scale, iproj
	glViewport(0, 0, w, h)
	width = w
	height = h
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	r = radius
	if w > h:
			glOrtho(-w/h*r, w/h*r, -r, r, -r, r)
			scale = 2.0 * r / h 
	else:
			glOrtho(-r, r, -h/w * r, h/w * r, -r, r)
			scale = 2.0 * r / w 

	#calculate and set the inverse projection matrix
	#proj is a diagonal matrix so it's inverse is easy to compute; ijth element -> 1/ij
	proj = glGetDoublev(GL_PROJECTION_MATRIX)
	iproj = proj
	for i in range(len(proj)):
		iproj[i][i] = 1/proj[i][i]


def main(argc, argv):
	global smoothness
	if argc is 2:
		smoothness = int(argv[1])
	glutInit(argv)
	glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH)
	glutInitWindowPosition(0, 20)
	glutInitWindowSize(width, height)
	glutCreateWindow( 'bezier - Press ESC to quit' )
	init()

	# Register interaction callbacks.
	glutKeyboardFunc(myKeyFunc)
	glutMouseFunc(mouseProcess)
	glutMotionFunc(mouseDrag)
	glutReshapeFunc(resize)
	glutDisplayFunc(display)
	glutMainLoop()

	return 0


if __name__ == '__main__': main(len(sys.argv),sys.argv)