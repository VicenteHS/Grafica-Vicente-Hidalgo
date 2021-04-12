# coding=utf-8
"""Drawing 4 shapes with different transformations"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import math

__author__ = "Daniel Calderon"
__license__ = "MIT"


# We will use 32 bits data, so an integer has 4 bytes
# 1 byte = 8 bits
SIZE_IN_BYTES = 4


# A class to store the application control
class Controller:
    fillPolygon = True


# we will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    else:
        print('Unknown key')


#--------------------PRIMER CAMBIO Crear circulos rgb ------------------

class Shape:
    def __init__(self, vertices, indices, textureFileName=None):
        self.vertices = vertices
        self.indices = indices
        self.textureFileName = textureFileName

#Funcion sacada de basic shapes, pero modificada dejando fijo el numero de triangulos
#y tomando como imput el color rgb

def createCircleRGB(r,g,b):

    # First vertex at the center, white color
    vertices = [0, 0, 0, 1.0, 1.0, 1.0]
    indices = []

    dtheta = 2 * math.pi / 50

    for i in range(50):
        theta = i * dtheta

        vertices += [
            # vertex coordinates
            0.5 * math.cos(theta), 0.5 * math.sin(theta), 0,

            # color generates varying between 0 and 1
                  r,       g, b]

        # A triangle is created using the center, this and the next vertex
        indices += [0, i, i+1]

    # The final triangle connects back to the second vertex
    indices += [0, 50, 1]

    return Shape(vertices, indices)


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Displaying multiple shapes - Modern OpenGL", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Creating our shader program and telling OpenGL to use it
    pipeline = es.SimpleTransformShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)



    #--------------------SEGUNDO CAMBIO Creacion de los circulos en gpu---------------------------
    #Tuve que crear tres por los colores rgb
    #Creando el sol
    shapeCircle = createCircleRGB(1,1,0)
    gpuCircle = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuCircle)
    gpuCircle.fillBuffers(shapeCircle.vertices, shapeCircle.indices, GL_STATIC_DRAW)

    #Creando la tierra
    shapeCircle2 = createCircleRGB(0,0,1)
    gpuCircle2 = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuCircle2)
    gpuCircle2.fillBuffers(shapeCircle2.vertices, shapeCircle2.indices, GL_STATIC_DRAW)

    #Creando la luna
    shapeCircle3 = createCircleRGB(1,1,1)
    gpuCircle3 = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuCircle3)
    gpuCircle3.fillBuffers(shapeCircle3.vertices, shapeCircle3.indices, GL_STATIC_DRAW)
    #----------------------------------------------------------------------------------------------------

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Using the time as the theta parameter
        theta = glfw.get_time()



        #-------------------- TERCER PASO CREAR TRANSFORMACIONES----------------------------------------
        #Transformacion para el sol
        circleTransform2 = tr.matmul([
            tr.translate(0, 0, 0),
            tr.rotationZ(2 * theta),
            tr.uniformScale(0.5)
        ])
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, circleTransform2)
        pipeline.drawCall(gpuCircle)

        #Transformacion para la tierra
        circleTransform = tr.matmul([
            tr.translate(0.5*np.cos(theta), 0.5*np.sin(theta), 0),
            tr.rotationZ(2 * theta),
            tr.uniformScale(0.2)
        ])
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, circleTransform)
        pipeline.drawCall(gpuCircle2)

        #Transformacion para la luna
        circleTransform3 = tr.matmul([
            tr.translate(0.1*np.cos(theta), 0.1*np.sin(theta), 0),
            tr.translate(0.5*np.cos(theta), 0.5*np.sin(theta), 0),
            tr.rotationZ(2*theta),
            tr.uniformScale(0.1)
        ])
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, circleTransform3)
        pipeline.drawCall(gpuCircle3)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuCircle.clear()
    
    glfw.terminate()