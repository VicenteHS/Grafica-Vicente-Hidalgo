# coding=utf-8
"""Textures and transformations in 2D"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grafica.gpu_shape import GPUShape, SIZE_IN_BYTES
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
from PIL import Image

__author__ = "Daniel Calderon"
__license__ = "MIT"

#Hable con Nelson Marambio sobre como hice el programa, y comente la idea
#de como se realizaria con el otro metodo de la lluvia separada. Igual el me dijo
#que lo dejarian pasar porque es la misma idea.




# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True

###################################################################################################
        # El controlador con el sprite 2 de fondo.
        self.actual_sprite = 1
        self.actual_sprite2 = 1
        self.x = 0.0
#        self.y = 0.0
        self.derecha = True
###################################################################################################


# global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

#############################################################################################
    # BASICAMENTE LO MISMO, PERO EL CONTROLLER.DERECHA DIRA HACIA DONDE MIRA EL CABALLERO
    elif key == glfw.KEY_RIGHT:
        controller.actual_sprite = (controller.actual_sprite + 1)%10
        controller.derecha = True
        controller.x = controller.x + 0.2
        
    
    elif key == glfw.KEY_LEFT:
        controller.actual_sprite = (controller.actual_sprite - 1)%10
        controller.derecha = False
        controller.x = controller.x - 0.2
        
#############################################################################################

    else:
        print('Unknown key')


if __name__ == "__main__":
    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "knight raininig!", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # A simple shader program with position and texture coordinates as inputs.
    pipeline = es.SimpleTextureTransformShaderProgram()
    
    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.25, 0.25, 0.25, 1.0)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

######################################################################################################


    # Creando el fondo con LLUVIA
    gpus2 = []
    thisFilePath = os.path.abspath(__file__)
    thisFolderPath = os.path.dirname(thisFilePath)
    spritesDirectory = os.path.join(thisFolderPath, "Sprites")
    spritePath2 = os.path.join(spritesDirectory, "fondo lluvia 9.png")

    texture = es.textureSimpleSetup(
            spritePath2, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

    for i in range(22):
        gpuFondo = GPUShape().initBuffers()
        pipeline.setupVAO(gpuFondo)

        shapeFondo = bs.createTextureQuad(i/22,(i + 1)/22,0,1)

        gpuFondo.texture = texture

        gpuFondo.fillBuffers(shapeFondo.vertices, shapeFondo.indices, GL_STATIC_DRAW)

        gpus2.append(gpuFondo)
    

    # CREANDO EL CABALLERO
    gpus = []

    # Definimos donde se encuentra la textura
    spritePath = os.path.join(spritesDirectory, "sprites.png")

    texture = es.textureSimpleSetup(
            spritePath, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

    # Creamos una gpushape por cada frame de textura
    for i in range(10):
        gpuKnight = GPUShape().initBuffers()
        pipeline.setupVAO(gpuKnight)

        shapeKnight = bs.createTextureQuad(i/10,(i + 1)/10,0,1)

        gpuKnight.texture = texture

        gpuKnight.fillBuffers(shapeKnight.vertices, shapeKnight.indices, GL_STATIC_DRAW)

        gpus.append(gpuKnight)

    ############################## ACA ESTA LO EXTRA ###################################################
    #ESTO ES UNA IDEA DE COMO SERIA CON LA LLUVIA, QUE BASICAMENTE ES COPIAR LO DEL FONDO, PERO SEPARANDO LA LLUVIA.
#    spritePath3 = os.path.join(spritesDirectory, "lluvia2.png")
#    texture = es.textureSimpleSetup(
#            spritePath3, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
#    gpuLluvia = GPUShape().initBuffers()
#    pipeline.setupVAO(gpuLluvia)
#    shapeLluvia = bs.createTextureQuad(0,1,0,1)
#    gpuLluvia.texture = texture
#    gpuLluvia.fillBuffers(shapeLluvia.vertices, shape.Lluvia.indices, GL_STATIC_DRAW)
#########################################Extra##################################################    

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # CAMBIANDO EL FONDO PARA QUE LLUEVA
        tiempo = glfw.get_time()
        t = int(tiempo*1)
        controller.actual_sprite2 = (controller.actual_sprite2 +t)%10

        #ADMINISTRANDO TRANSFORMACION DE FONDO. CON ESTO CORRO ENTRE LOS DOS FONDOS PARA VOLVERLO INFINITO

        movimiento = -controller.x
        if controller.x > 2:
            controller.x = 0
            movimiento = -2
        if controller.x <0:
            controller.x = 2
            movimiento = 2


##############################################################################################################################

        # FONDO 1
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
            tr.translate(movimiento, 0, 0),
            tr.uniformScale(2.0)
        ]))

        pipeline.drawCall(gpus2[controller.actual_sprite2])

        #FONDO 2 (AL LADO)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
            tr.translate(movimiento,0,0),
            tr.translate(2, 0, 0),
            tr.uniformScale(2.0)
        ]))
        pipeline.drawCall(gpus2[controller.actual_sprite2])
        ###################################################################
        ###################################################################
        ###################################################################
        ########################Aca Esta lo Extra##########################
        #mov vertical
#       vertical = -controller.y
#       if controller.y > 2:
#           controller.y = 0
#           movimiento = -2
#       if controller.y <0:
#           controller.y = 2
#           movimiento = 2
#
#
#        #Lluvia 1
#        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
#            tr.translate(0, vertical, 0),
#            tr.uniformScale(1.0)
#        ]))
#
#        pipeline.drawCall(gpus2[controller.actual_sprite2])
        #Lluvia 2
#        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
#            tr.translate(0, vertical, 0),
#            tr.translate(0, 2, 0),
#            tr.uniformScale(1.0)
#        ]))

#        pipeline.drawCall(gpus2[controller.actual_sprite2])
#        Lo unico que faltaria seria el controlador de tiempo, pero es el mismo que uso para el fondo con lluvia :)
        #############################EXTRA#################################
        ###################################################################
        ###################################################################
        ###################################################################

        # CABALLERO
        if controller.derecha:
            cambio = tr.scale(1, 1, 1)
        else:
            cambio = tr.scale(-1, 1, 1)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
            tr.translate(0, -0.6, 0),
            cambio,
            tr.uniformScale(0.85)
        ]))

        pipeline.drawCall(gpus[controller.actual_sprite])
        
        
##############################################################################################################################

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuKnight.clear()
    gpuFondo.clear()
#    gpuLluvia.clear()

    glfw.terminate()
