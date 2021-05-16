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
from grafica.gpu_shape import GPUShape, SIZE_IN_BYTES
from grafica.assets_path import getAssetPath
import time

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

class Shape:
    def __init__(self, vertices, indices, textureFileName=None):
        self.vertices = vertices
        self.indices = indices
        self.textureFileName = textureFileName

class Controller:
    def __init__(self):
        self.leftClickOn = False
        self.rightClickOn = False
        self.mousePos = (0.0, 0.0)
        self.agarrado = False
        self.fillPolygon = True
        self.marcado = False
        self.x = 0
        self.y = 0

# class Arbol:
#     def __init__(self):
#         self.raiz = None
#         self.izq = None
#         self.der = None
#         self.coneccion = None
# Arboles = []
    

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
            pass

    elif (action ==glfw.RELEASE):
        if (button == glfw.MOUSE_BUTTON_1):
            controller.leftClickOn = False

        if (button == glfw.MOUSE_BUTTON_2):
            controller.rightClickOn = not controller.rightClickOn






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


    # Letras
    textBitsTexture = tx.generateTextBitsTexture()
    gpuText3DTexture = tx.toOpenGLTexture(textBitsTexture)

    ####################################################################
    ####################################################################
    ####################################################################
    ####################################################################
    ####################################################################
    ####################################################################
    ####################################################################
    # Colores
    Color = [0.6,0.2,0.8]
    Color2 = [0.0,1.0,0.0]

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
            gpuHeader.shader = 2
            gpuHeader.texture = gpuText3DTexture
            gpusNumbers.append(gpuHeader)
        return gpusNumbers

    # Instanciacion
    gpusNumbers = createNumbers(Numeros)

    # Creacion de nodo definitivo
    def NodoDefinitivo():
        #Creacion de circulo gpu
        shapeCirculo = bs.createCircleRGB(30,Color[0],Color[1],Color[2])
        gpuCirculo = es.GPUShape().initBuffers()
        pipeline.setupVAO(gpuCirculo)
        gpuCirculo.fillBuffers(shapeCirculo.vertices, shapeCirculo.indices, GL_DYNAMIC_DRAW)
        gpuCirculo.shader = 1

        # Creacion de un Nodo radio
        Circulo = sg.SceneGraphNode("Circulo tr radio")
        Circulo.transform = tr.uniformScale(1)
        Circulo.childs += [gpuCirculo]

        Nodos = sg.SceneGraphNode("Nodos")
        for i in range(len(Numeros)):
            x = random.uniform(-0.75,0.75)
            y = random.uniform(-0.75,0.75)
            CirculoTrasladado = sg.SceneGraphNode("CNodo" + str(i) +"trasladado")
            CirculoTrasladado.transform = tr.translate(x,y,0)
            CirculoTrasladado.childs += [Circulo]

            NodoEscalado = sg.SceneGraphNode("NodoEscalado")
            NodoEscalado.transform = tr.uniformScale(0.5)
            NodoEscalado.childs += [gpusNumbers[i]]

            NodoTrasladado = sg.SceneGraphNode("Nodo" + str(i) +"trasladado")
            NodoTrasladado.transform = tr.matmul([tr.translate(x,y,0),tr.translate(-0.03, -0.02, 0)])
            NodoTrasladado.childs += [NodoEscalado]

            Nodo = sg.SceneGraphNode("Nodo" + str(i))
            Nodo.childs += [CirculoTrasladado,NodoTrasladado]
            Nodo.valores = Valores[i]

            Nodos.childs +=[Nodo]
        return Nodos



 

    ########################################
    #Instanciacion
    NodoDef = NodoDefinitivo()
    ########################################
    


    # Ajustar tamaño segun el numero de nodos
    if len(Numeros) >= 80:
        largo = 0.09
        CircleNode = sg.findNode(NodoDef, "Circulo tr radio")
        CircleNode.transform = tr.uniformScale(largo)
    elif len(Numeros) >= 60:
        largo = 0.095
        CircleNode = sg.findNode(NodoDef, "Circulo tr radio")
        CircleNode.transform = tr.uniformScale(largo)
    elif len(Numeros) >= 50:
        largo = 0.1
        CircleNode = sg.findNode(NodoDef, "Circulo tr radio")
        CircleNode.transform = tr.uniformScale(largo)
    elif len(Numeros) >= 40:
        largo = 0.12
        CircleNode = sg.findNode(NodoDef, "Circulo tr radio")
        CircleNode.transform = tr.uniformScale(largo)
    elif len(Numeros) >= 20:
        largo = 0.15
        CircleNode = sg.findNode(NodoDef, "Circulo tr radio")
        CircleNode.transform = tr.uniformScale(largo)
    else:
        largo = 0.2
        CircleNode = sg.findNode(NodoDef, "Circulo tr radio")
        CircleNode.transform = tr.uniformScale(largo)



    #Primero se define el radio
    aux = sg.findNode(NodoDef, "Circulo tr radio")
    Radio = (aux.transform[0][0])/2
    Radiocuad = Radio**2
    

    ##########################################################
    #Creacion Circulo seleccionado
    def createNodoCircleRGB(N,Color):
        shapeCircSelect = bs.createCircleRGB(N,Color[0],Color[1],Color[2])
        gpuCircSelect = es.GPUShape().initBuffers()
        pipeline.setupVAO(gpuCircSelect)
        gpuCircSelect.fillBuffers(shapeCircSelect.vertices, shapeCircSelect.indices, GL_DYNAMIC_DRAW)
        gpuCircSelect.shader = 1

        Circ = sg.SceneGraphNode("Circ tr radio")
        Circ.transform = tr.uniformScale(largo)
        Circ.childs += [gpuCircSelect]

        return Circ

    CirculoBlanco = createNodoCircleRGB(30, Color)
    CirculoVerde = createNodoCircleRGB(30, Color2)


    def createColorQuad(Xo,Yo,X1,Y1,Color):

        # Defining locations and colors for each vertex of the shape    
        vertices = [
        #   positions        colors
            Xo, Yo, 0.0,  Color[0], Color[1], Color[2],
            X1, Yo, 0.0,  Color[0], Color[1], Color[2],
            X1, Y1, 0.0, Color[0], Color[1], Color[2],
            Xo ,Y1, 0.0, Color[0], Color[1], Color[2]]

        # Defining connections among vertices
        # We have a triangle every 3 indices specified
        indices = [
            0,1,2,
            2,3,0]

        return Shape(vertices, indices)



    

        

    # Encontrar posiciones de nodos.
    PosicionesNodos = []
    IndicesUsados = []
    NodosUsados = []
    Indice = -1


    for i in range(len(Numeros)):
        index = i
        aux = sg.findNode(NodoDef, "CNodo" + str(i) +"trasladado")
        aux2 = sg.findNode(NodoDef, "Nodo" + str(i) +"trasladado")
        Xo = aux.transform[0][3]
        Yo = aux.transform[1][3]
        tupla = [Xo,Yo]
        PosicionesNodos.append (tupla)










    while not glfw.window_should_close(window):
        glfw.poll_events()
        glClear(GL_COLOR_BUFFER_BIT)

        # Getting the mouse location in opengl coordinates
        mousePosX = 2 * (controller.mousePos[0] - width/2) / width
        mousePosY = 2 * (height/2 - controller.mousePos[1]) / height

        theta = glfw.get_time()
        inicial = time.time()
        final = time.time()


        



        #################################################################################
        #Configurar agarre de nodos
        #Con el radio definido
        #Se cumple ecuacion de circulo (x-x0).... xo es la pos del nodo   aux.transform = tr.translate(mousePosX, mousePosY, 0)

        ########################################
        ########################################
        ########################################


        if not controller.agarrado:
            for i in range(len(Numeros)):
                index = i
                aux = sg.findNode(NodoDef, "CNodo" + str(i) +"trasladado")
                aux2 = sg.findNode(NodoDef, "Nodo" + str(i) +"trasladado")
                Xo = aux.transform[0][3]
                Yo = aux.transform[1][3]

                # if (mousePosX-Xo)**2 + (mousePosY-Yo)**2 <= Radiocuad and not i == Indice and controller.marcado:
                #     aux.click = True
                #     break
                # elif (mousePosX-Xo)**2 + (mousePosY-Yo)**2 > Radiocuad and not i == Indice and controller.marcado:
                #     aux.click = False
                #     break

                if (mousePosX-Xo)**2 + (mousePosY-Yo)**2 <= Radiocuad and controller.leftClickOn and i == Indice and controller.marcado:
                    aux.click = False
                    controller.marcado = False
                    Indice = -1
                    time.sleep(0.5)
                    break

                #Esto es para pintar
                elif (mousePosX-Xo)**2 + (mousePosY-Yo)**2 <= Radiocuad and controller.leftClickOn and not controller.marcado:
                    aux.click = True
                    controller.marcado = True
                    Indice = i
                    time.sleep(0.5)
                    break

                #Esto es para mover
                if (mousePosX-Xo)**2 + (mousePosY-Yo)**2 <= Radiocuad and controller.leftClickOn:
                    controller.agarrado = True
                    break


        # Esto es dps del break de mover
        if controller.agarrado:
            if controller.leftClickOn:
                aux.transform = tr.translate(mousePosX, mousePosY, 0)
                aux2.transform = tr.translate(mousePosX - 0.03, mousePosY - 0.02, 0)
            else:
                controller.agarrado = False


        #Esto es dps del break de pintar
        if aux.click:
            aux.childs = [CirculoVerde]
            gpusNumbers[index].shader = 3
            aux.childs[0].transform = tr.uniformScale(0.25)
        if not aux.click:
            aux.childs = [CirculoBlanco]
            gpusNumbers [index].shader = 2

         






        # if not controller.marcado:
        #     for i in range(len(Numeros)):
        #         index = i
        #         aux = sg.findNode(NodoDef, "CNodo" + str(i) +"trasladado")
        #         aux2 = sg.findNode(NodoDef, "Nodo" + str(i) +"trasladado")
        #         Xo = aux.transform[0][3]
        #         Yo = aux.transform[1][3]
        #         if (mousePosX-Xo)**2 + (mousePosY-Yo)**2 <= Radiocuad and controller.rightClickOn:
        #             aux.click = not aux.click
        #             
        #             break               
        #             # if not (PosicionesNodos[i] in NodosUsados):
        #             #     NodosUsados.append(PosicionesNodos[i])
        #             #     IndicesUsados.append(i)
        #             #     print (NodosUsados)
        #             #     print (IndicesUsados)
        #             # elif (PosicionesNodos[i] in NodosUsados):
        #             #     NodosUsados.remove(PosicionesNodos[i])
        #             #     IndicesUsados.remove(i)
        #             #     print(NodosUsados)
        #             #     print(IndicesUsados)
        #             # if len(NodosUsados) == 2:
        #             #     if (mousePosX-Xo)**2 + (mousePosY-Yo)**2 <= Radiocuad and controller.leftClickOn:
        #             #         pass


        ########################################
        ########################################
        ########################################



        
        
        ########################################
        ########################################
        ########################################
        sg.drawSceneGraphNodeDefinitivo(NodoDef, pipeline, textPipeline, Color,Color2,"transform")
        
        glfw.swap_buffers(window)


        ########################################
        ########################################
        ########################################





    NodoDef.clear()

    glfw.terminate()