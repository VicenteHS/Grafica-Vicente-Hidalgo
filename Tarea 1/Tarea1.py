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
#usar una textura transparente para reconocer cada uno de los nodos

with open('input.csv','r') as file:
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
        self.agarrado = False
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

    window = glfw.create_window(width, height, "Arbol Binario", None, None)

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
    ####################################################################
    ####################################################################
    ####################################################################
    ####################################################################
    ####################################################################
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
        Circulo = sg.SceneGraphNode("Circulo tr radio")
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


    ########################################
    #Instanciacion de circulos y numeros
    Color = [0.12,0.16,0.91]
    Circulos = createCirculos(pipeline,Color[0],Color[1],Color[2])
    ########################################

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
    
    def NodoNumbers():
        gpusNumbers = createNumbers(Numeros)
        NodoNumbers = sg.SceneGraphNode("NodoNumbers")
        for i in range(len(gpusNumbers)):

            #asegurar la misma traslacion que los circulos, por ende hay que cambiar la de los circ nada mas.
            ##################################################################
            AuxCirculo = sg.findNode(Circulos, "Nodo" + str(i) +"trasladado")
            traslacion = AuxCirculo.transform           #igualar al circulo
            traslacion2 = tr.translate(-0.03, -0.02, 0) #Ajustar
            escalamiento = tr.scale(0.8, 1, 1)
            transformacion = tr.matmul([traslacion2,traslacion,escalamiento,tr.uniformScale(0.5)])
            ##################################################################

            newNode = sg.SceneGraphNode("Nodo" + str(i) +"trasladado")
            newNode.transform = transformacion
            newNode.childs += [gpusNumbers[i]]

            NodoNumbers.childs += [newNode]
        return NodoNumbers

    ########################################
    #Instanciacion numeros
    NodoNumbers = NodoNumbers()
    ########################################


    # Ajustar tamaño segun el numero de nodos
    if len(Numeros) >= 80:
        CircleNode = sg.findNode(Circulos, "Circulo tr radio")
        CircleNode.transform = tr.uniformScale(0.083)
    elif len(Numeros) >= 60:
        CircleNode = sg.findNode(Circulos, "Circulo tr radio")
        CircleNode.transform = tr.uniformScale(0.095)
    elif len(Numeros) >= 50:
        CircleNode = sg.findNode(Circulos, "Circulo tr radio")
        CircleNode.transform = tr.uniformScale(0.1)
    elif len(Numeros) >= 40:
        CircleNode = sg.findNode(Circulos, "Circulo tr radio")
        CircleNode.transform = tr.uniformScale(0.12)
    elif len(Numeros) >= 20:
        CircleNode = sg.findNode(Circulos, "Circulo tr radio")
        CircleNode.transform = tr.uniformScale(0.15)



    #Primero se define el radio
    aux = sg.findNode(Circulos, "Circulo tr radio")
    Radio = (aux.transform[0][0])/2
    Radiocuad = Radio**2
    



    while not glfw.window_should_close(window):
        glfw.poll_events()
        glClear(GL_COLOR_BUFFER_BIT)

        

        # Getting the mouse location in opengl coordinates
        mousePosX = 2 * (controller.mousePos[0] - width/2) / width
        mousePosY = 2 * (height/2 - controller.mousePos[1]) / height


        #################################################################################
        #Configurar agarre de nodos
        #Con el radio definido
        #Se cumple ecuacion de circulo (x-x0).... xo es la pos del nodo   aux.transform = tr.translate(mousePosX, mousePosY, 0)


        if not controller.agarrado:
            for i in range(len(Numeros)):
                aux = sg.findNode(Circulos, "Nodo" + str(i) +"trasladado")
                Xo = aux.transform[0][3]
                Yo = aux.transform[1][3]
                if (mousePosX-Xo)**2 + (mousePosY-Yo)**2 <= Radiocuad and controller.leftClickOn:
                    controller.agarrado = True
                    #index = i
                    break
        

        if controller.agarrado:
            if controller.leftClickOn:
                aux.transform = tr.translate(mousePosX, mousePosY, 0)
            else:
                controller.agarrado = False
                    

        
        



        ########################################
        ########################################
        ########################################
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(Circulos, pipeline,"transform")

        glUseProgram(textPipeline.shaderProgram)
        sg.drawSceneGraphNodeTEXT(NodoNumbers, textPipeline, Color, "transform")

        glfw.swap_buffers(window)
        ########################################
        ########################################
        ########################################

    Circulos.clear()
    NodoNumbers.clear()

    glfw.terminate()