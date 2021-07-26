# Codigo reciclado de forma util desde tarea 2c tobogan

# coding=utf-8
"""Showing lighting effects over two textured objects: Flat, Gauraud and Phong"""

import glfw
import copy
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.lighting_shaders as ls
from grafica.assets_path import getAssetPath
import grafica.scene_graph as sg
import grafica.ex_curves as cv
import random

LIGHT_FLAT    = 0
LIGHT_GOURAUD = 1
LIGHT_PHONG   = 2


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = False             #Control for activate red line
        self.lightingModel = LIGHT_PHONG
        self.Camera2 = True
        self.CameraEnd = False
        self.ITR = 0
        self.ITR2 = 0
        self.theta = 0
        self.move = False
        self.R = 5
        self.velocity = 100
        self.Nobstacles = 20


################################################################
################################################################
################################################################
#SHADER MODIFICADO PARA CREAR LINEAS
class CurveShader:

    def __init__(self):

        vertex_shader = """
            #version 130

            uniform mat4 projection;
            uniform mat4 view;
            uniform mat4 model;

            in vec3 position;

            out vec3 newColor;
            void main()
            {
                gl_Position = projection * view * model * vec4(position, 1.0f);
                newColor = vec3(1,0,0);
            }
            """

        fragment_shader = """
            #version 130
            in vec3 newColor;

            out vec4 outColor;
            void main()
            {
                outColor = vec4(newColor, 1.0f);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color specification => 3*4  = 12 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)




# We will use the global controller as communication with the callback function
controller = Controller()


# This function generates a spline of catmul roll that defines the movement and also is a reference for the tobogan
def createLine(N,Lista):
    


    CRcurve = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[0], N)    #C1
    CRcurve2 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[1], N)   #C2
    CRcurve3 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[2], N)   #C3
    CRcurve4 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[3], N)   #C4
    CRcurve5 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[4], N)   #C5
    CRcurve6 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[5], N)   #C6
    CRcurve7 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[6], N)   #C7
    CRcurve8 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[7], N)   #C8
    CRcurve9 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[8], N)   #C9
    CRcurve10 = cv.evalCurve(cv.CatmullRomMatrixL(Lista)[9], N)  #C10

    ver = np.concatenate((CRcurve[0:-1,:],
                          CRcurve2[0:-1,:],
                          CRcurve3[0:-1,:],
                          CRcurve4[0:-1,:],
                          CRcurve5[0:-1,:],
                          CRcurve6[0:-1,:],
                          CRcurve7[0:-1,:],
                          CRcurve8[0:-1,:],
                          CRcurve9[0:-1,:],
                          CRcurve10), axis=0) #numpy array
    

    vertices = ver.reshape(1,np.size(ver)).tolist()[0] #list
    indices = [i for i in range(10*N-9)]


    return bs.Shape(vertices, indices), ver