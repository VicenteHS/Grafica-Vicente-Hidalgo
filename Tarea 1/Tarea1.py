import csv
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
import grafica.scene_graph as sg
import random
import grafica.text_renderer as tx

########################################################################
# Obtener lista con los valores puestos en el csv

with open('input.csv','r') as file:
    file = csv.reader(file)

    for line in file:
        Numeros = line

print(Numeros)

########################################################################
# Controlador

SIZE_IN_BYTES = 4

class Controller:
    def __init__(self):
        self.leftClickOn = False
        self.mousePos = (0.0, 0.0)

        self.fillPolygon = True
    

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

####################################################################
# Definicion de mouse

# Aca se define la posicion del mouse
def cursor_pos_callback(window, x, y):
    global controller
    controller.mousePos = (x,y)

# Aca se definen los botones del mouse
def mouse_button_callback(window, button, action, mods):

    global controller
    
    """
    glfw.MOUSE_BUTTON_1: left click
    glfw.MOUSE_BUTTON_2: right click
    """

    if (action == glfw.PRESS or action == glfw.REPEAT):
        if (button == glfw.MOUSE_BUTTON_1):
            controller.leftClickOn = True
            print("por definir")

        if (button == glfw.MOUSE_BUTTON_2):
            print(glfw.get_cursor_pos(window))

    elif (action ==glfw.RELEASE):
        if (button == glfw.MOUSE_BUTTON_1):
            controller.leftClickOn = False






####################################################################
# Codigo principal

if __name__ == "__main__":
    ####################################################################
    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 900
    height = 900

    window = glfw.create_window(width, height, "ert", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)
    ###################################################################
    #pipelines
    texturePipeline = es.SimpleTextureShaderProgram()
    textPipeline = tx.TextureTextRendererShaderProgram()
    pipeline = es.SimpleTransformShaderProgram()

    ####################################################################
    # Teclado a glfw
    glfw.set_key_callback(window, on_key)
    # Mouse a glfw.
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    ####################################################################
    # Eleccion de pipeline
    
    
    ####################################################################
    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glClearColor(0.3, 0.3, 0.3, 1.0)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    #glfw.swap_interval(0)

    ####################################################################
    #Creacion de figuras

    #Letras
    # Creating texture with all characters
    textBitsTexture = tx.generateTextBitsTexture()
    # Moving texture to GPU memory
    gpuText3DTexture = tx.toOpenGLTexture(textBitsTexture)



    def createCirculos(pipeline):

        # Creacion figura gpu de circulo
        shapeCirculo = bs.createCircleRGB(30,0.7,0.4,0.2)
        gpuCirculo = es.GPUShape().initBuffers()
        pipeline.setupVAO(gpuCirculo)
        gpuCirculo.fillBuffers(shapeCirculo.vertices, shapeCirculo.indices, GL_STATIC_DRAW)

        # Creacion de un Nodo
        Circulo = sg.SceneGraphNode("Circulo")
        Circulo.transform = tr.uniformScale(0.15)
        Circulo.childs += [gpuCirculo]

        # Creacion de todos los nodos de Numeros
        Circulos = sg.SceneGraphNode("Circulos")
        
        for i in range(len(Numeros)):
            x = random.uniform(-0.75,0.75)
            y = random.uniform(-0.75,0.75)
            newNode = sg.SceneGraphNode("Nodo" + str(i) +"trasladado")
            newNode.transform = tr.translate(x,y,0)
            newNode.childs += [Circulo]

            Circulos.childs += [newNode]

        return Circulos


        
    def createNumbers(Numeros):
        gpusNumbers = []
        for i in range(len(Numeros)):
            headerText = str(Numeros[i])
            headerCharSize = 0.1
            headerCenterX = headerCharSize * len(headerText) / 2
            headerShape = tx.textToShape(headerText, headerCharSize, headerCharSize)
            gpuHeader = es.GPUShape().initBuffers()
            textPipeline.setupVAO(gpuHeader)
            gpuHeader.fillBuffers(headerShape.vertices, headerShape.indices, GL_STATIC_DRAW)
            gpuHeader.texture = gpuText3DTexture
            gpusNumbers.append(gpuHeader)
        return gpusNumbers

    # def createNumbers(Numeros):
    #     Numeros = sg.SceneGraphNode("Numeros")

    #     for i in range(len(Numeros)):
    #         x = random.uniform(-0.75,0.75)
    #         y = random.uniform(-0.75,0.75)

    #         headerText = str(Numeros[i])
    #         headerCharSize = 0.1
    #         headerCenterX = headerCharSize * len(headerText) / 2
    #         headerShape = tx.textToShape(headerText, headerCharSize, headerCharSize)
    #         gpuHeader = es.GPUShape().initBuffers()
    #         textPipeline.setupVAO(gpuHeader)
    #         gpuHeader.fillBuffers(headerShape.vertices, headerShape.indices, GL_STATIC_DRAW)
    #         gpuHeader.texture = gpuText3DTexture
            
    #         Numeros.childs += [gpuHeader]
    #         Numeros.transform = tr.translate(x, y, 0)



    gpusNumbers = createNumbers(Numeros)
    Circulos = createCirculos(pipeline)











    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(textPipeline.shaderProgram)
        # for i in range (len(gpusNumbers)):
        #     glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), 1,1,1,0)
        #     glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 0.5,0.5,0.5,1)
        #     glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.identity())
        #     textPipeline.drawCall(gpusNumbers[i])


        glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), 1,1,1,0)
        glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 0.5,0.5,0.5,1)
        glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.identity())
        textPipeline.drawCall(gpusNumbers[9])



        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(Circulos, pipeline,"transform")

        glfw.swap_buffers(window)

    Circulos.clear()

    glfw.terminate()