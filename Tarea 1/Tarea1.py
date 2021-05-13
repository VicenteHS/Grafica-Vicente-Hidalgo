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

with open('input3.csv','r') as file:
    file = csv.reader(file)

    for line in file:
        Num = line
Numeros = []
for i in range (len (Num)):
    aux = Num[i].strip()
    Numeros.append(aux)
Valores = []
for i in range (len (Numeros)):
    Valores.append(int(Numeros[i]))


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
    # Cosas varias
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    #glfw.swap_interval(0)

    # Letras
    # Creating texture with all characters
    textBitsTexture = tx.generateTextBitsTexture()
    # Moving texture to GPU memory
    gpuText3DTexture = tx.toOpenGLTexture(textBitsTexture)

    ####################################################################

    # Creacion de grafo de escena de circulo.
    def createCirculos(pipeline,r,g,b):
        #0.42,0.96,0.91 <- color de prueba
        # Creacion figura gpu de circulo
        shapeCirculo = bs.createCircleRGB(30,r,g,b)
        gpuCirculo = es.GPUShape().initBuffers()
        pipeline.setupVAO(gpuCirculo)
        gpuCirculo.fillBuffers(shapeCirculo.vertices, shapeCirculo.indices, GL_DYNAMIC_DRAW)

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


    # Creacion de lista con los numeros convertidos a gpuShape   
    def createNumbers(Numeros):
        gpusNumbers = []
        for i in range(len(Numeros)):
            headerText = str(Numeros[i])
            headerCharSize = 0.08
            headerCenterX = headerCharSize * len(headerText) / 2
            headerShape = tx.textToShape(headerText, headerCharSize, headerCharSize)
            gpuHeader = es.GPUShape().initBuffers()
            textPipeline.setupVAO(gpuHeader)
            gpuHeader.fillBuffers(headerShape.vertices, headerShape.indices, GL_DYNAMIC_DRAW)
            gpuHeader.texture = gpuText3DTexture
            gpusNumbers.append(gpuHeader)
        return gpusNumbers


    ########################################
    #Instanciacion de circulos y numeros
    Color = [0.12,0.16,0.91]                            #Buscar cambiarlo al controlador
    gpusNumbers = createNumbers(Numeros)
    Circulos = createCirculos(pipeline,Color[0],Color[1],Color[2])
    ########################################





    while not glfw.window_should_close(window):
        glfw.poll_events()
        glClear(GL_COLOR_BUFFER_BIT)

        # Ajustar tamaño segun el numero de nodos
        if len(Numeros) >= 75:
            CircleNode = sg.findNode(Circulos, "Circulo")
            CircleNode.transform = tr.uniformScale(0.083)
        elif len(Numeros) >= 50:
            CircleNode = sg.findNode(Circulos, "Circulo")
            CircleNode.transform = tr.uniformScale(0.1)
        elif len(Numeros) >= 25:
            CircleNode = sg.findNode(Circulos, "Circulo")
            CircleNode.transform = tr.uniformScale(0.15)


        # Muestra de Circulos
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(Circulos, pipeline,"transform")



        # Trabajo la muestra de numeros
        glUseProgram(textPipeline.shaderProgram)
        for i in range (len(gpusNumbers)):
            AuxCirculo = sg.findNode(Circulos, "Nodo" + str(i) +"trasladado")
            traslacion = AuxCirculo.transform           #igualar al circulo
            traslacion2 = tr.translate(-0.03, -0.02, 0) #Ajustar
            escalamiento = tr.scale(0.8, 1, 1)
            transformacion = tr.matmul([traslacion2,traslacion,escalamiento,tr.uniformScale(0.5)])
            glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), 0,0,0,1)
            glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), Color[0],Color[1],Color[2],1)
            glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE, transformacion)
            textPipeline.drawCall(gpusNumbers[i])



        

        glfw.swap_buffers(window)

    Circulos.clear()
    for i in range (len(gpusNumbers)):
        gpusNumbers[i].clear()

    glfw.terminate()