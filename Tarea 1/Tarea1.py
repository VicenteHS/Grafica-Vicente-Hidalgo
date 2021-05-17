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
# REVISAR PROBLEMAS CON EL 99!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1

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
        self.elegir = False
        self.error = False
        self.arreglar = False
        self.hint = False
    

controller = Controller()

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller


    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)
    
    elif key == glfw.KEY_H:
        controller.hint = not controller.hint

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
            controller.rightClickOn = True

    elif (action ==glfw.RELEASE):
        if (button == glfw.MOUSE_BUTTON_1):
            controller.leftClickOn = False

        if (button == glfw.MOUSE_BUTTON_2):
            controller.rightClickOn = False






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
    texturePipeline = es.SimpleTextureTransformShaderProgram()
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
    ##########
    # Colores
    Color = [0.6,0.2,0.8]
    Color2 = [0.0,1.0,0.0]
    Color3 = [1.0,1.0,1.0]
    ##########







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

    ##########
    # Instanciacion
    gpusNumbers = createNumbers(Numeros)
    ##########







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

    ##########
    #Instanciacion
    NodoDef = NodoDefinitivo()
    ##########
    







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
    ##########
    #Primero se define el radio
    aux = sg.findNode(NodoDef, "Circulo tr radio")
    Radio = (aux.transform[0][0])/2
    Radiocuad = Radio**2
    ##########







    ##########################################################
    ##########################################################
    ##########################################################
    #CREACION FIGURAS QUE CAMBIARAN AL APRETAR CON EL MOUSE LOS NODOS!!!
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
    
    def createNodoCircleRGBShearing(N,Color):
        shapeCircSelect = bs.createCircleRGB(N,Color[0],Color[1],Color[2])
        gpuCircSelect = es.GPUShape().initBuffers()
        pipeline.setupVAO(gpuCircSelect)
        gpuCircSelect.fillBuffers(shapeCircSelect.vertices, shapeCircSelect.indices, GL_DYNAMIC_DRAW)
        gpuCircSelect.shader = 6

        Circ = sg.SceneGraphNode("Circ tr radio")
        Circ.transform = tr.uniformScale(largo)
        Circ.childs += [gpuCircSelect]

        return Circ
    ##########
    CirculoMorado = createNodoCircleRGB(30, Color)
    CirculoVerde = createNodoCircleRGB(30, Color2)
    CirculoShearing = createNodoCircleRGBShearing(30, Color3)
    ##########




    def createNodoTexture():
        cuadText = bs.createTextureQuad(2, 2)
        gpuNodoText = GPUShape().initBuffers()
        texturePipeline.setupVAO(gpuNodoText)
        gpuNodoText.fillBuffers(cuadText.vertices, cuadText.indices, GL_DYNAMIC_DRAW)
        gpuNodoText.shader = 5
        gpuNodoText.texture = es.textureSimpleSetup(
            getAssetPath("NodoText.png"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
        
        NodoTextura = sg.SceneGraphNode("Nodo Textura")
        NodoTextura.transform = tr.uniformScale(0.4)  #Con 0.4 queda justo como los nodos
        NodoTextura.childs += [gpuNodoText]

        NodoTexturaDesplazado = sg.SceneGraphNode("Nodo Textura Desplazado")
        NodoTexturaDesplazado.transform = tr.translate(largo/2, -largo/2, 0)
        NodoTexturaDesplazado.childs += [NodoTextura]
        return NodoTexturaDesplazado

    



    ##########
    NodoTextura = createNodoTexture()
    ##########

    def createNodoError():
        cuadText = bs.createTextureQuadBig(1,1)
        gpuError = GPUShape().initBuffers()
        texturePipeline.setupVAO(gpuError)
        gpuError.fillBuffers(cuadText.vertices, cuadText.indices, GL_DYNAMIC_DRAW)
        gpuError.shader = 5
        gpuError.texture = es.textureSimpleSetup(
            getAssetPath("Error.png"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
            
        NodoError = sg.SceneGraphNode("Nodo Error")
        NodoError.transform = tr.shearing(0.01,0.01, 0, 0, 0, 0)
        NodoError.childs += [gpuError]

        NodoErrorTrasladado = sg.SceneGraphNode("Nodo Error Trasladado")
        NodoErrorTrasladado.transform = tr.translate(0.0,0.0,0.0)
        NodoErrorTrasladado.childs += [NodoError]

        return NodoErrorTrasladado
    NodoError = createNodoError()    

    











    def mediana(L):
        L.sort()
        mitad = int(len(L)/2)
        return L[mitad]
    
    MedianaValores = mediana(Valores)

    # Encontrar posiciones de nodos.
    PosicionesNodos = []
    IndicesUsados = []
    NodosUsados = []
    Indice = -1
    contadorespecial = -1

    while not glfw.window_should_close(window):
        glfw.poll_events()
        glClear(GL_COLOR_BUFFER_BIT)

        # Getting the mouse location in opengl coordinates
        mousePosX = 2 * (controller.mousePos[0] - width/2) / width
        mousePosY = 2 * (height/2 - controller.mousePos[1]) / height

        



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
                
                # Se presenta el error 
                if controller.error:
                    time.sleep(0.2)
                    sg.findNode(NodoError, "Nodo Error Trasladado").transform = tr.translate(0.0, -2.0, 0)
                    controller.error = False
                
                if controller.elegir:
                    # Se encuentran los valores de los nodos
                    NODO1 = sg.findNode(NodoDef,"Nodo" + str(Indice))
                    NODO1Valores = NODO1.valores
                    NODO2 = sg.findNode(NodoDef,"Nodo" + str(Indice2))
                    NODO2Valores = NODO2.valores

                    # Se afirma que el nodo1 es menor al nodo2
                    if (mousePosX-Xo)**2 + (mousePosY-Yo)**2 <= Radiocuad and mousePosX < Xo and controller.rightClickOn and i == Indice2:
                        if NODO1Valores < NODO2Valores:
                            print("bien hecho")
                            controller.arreglar = True
                            time.sleep(0.2)
                            break
                        if NODO1Valores > NODO2Valores:
                            controller.arreglar = True
                            controller.error = True
                            sg.findNode(NodoError, "Nodo Error Trasladado").transform = tr.translate(0.0, 2.0, 0)
                            time.sleep(0.2)
                            break
                            

                    # Se afirma que el nodo2 es menor al nodo1
                    if (mousePosX-Xo)**2 + (mousePosY-Yo)**2 <= Radiocuad and mousePosX > Xo and controller.rightClickOn and i == Indice2:
                        if NODO1Valores < NODO2Valores:
                            controller.arreglar = True
                            controller.error = True
                            sg.findNode(NodoError, "Nodo Error Trasladado").transform = tr.translate(0.0, 2.0, 0)
                            time.sleep(0.2)
                            break
                        if NODO1Valores > NODO2Valores:
                            print("bien hecho")
                            controller.arreglar = True
                            time.sleep(0.2)
                            break



                # Esto es para formar el arbol
                if (mousePosX-Xo)**2 + (mousePosY-Yo)**2 <= Radiocuad and controller.rightClickOn and i != Indice and controller.marcado and not controller.elegir:
                    Indice2 = i
                    aux.click2 = True
                    controller.elegir = True
                    time.sleep(0.2)
                    break


                # Esto es para despintar el pintado
                if (mousePosX-Xo)**2 + (mousePosY-Yo)**2 <= Radiocuad and controller.rightClickOn and i == Indice and controller.marcado and not controller.elegir:
                    aux.click = False
                    controller.marcado = False
                    Indice = -1
                    time.sleep(0.2)
                    break

                #Esto es para pintar
                if (mousePosX-Xo)**2 + (mousePosY-Yo)**2 <= Radiocuad and controller.rightClickOn and not controller.marcado and not controller.elegir:
                    aux.click = True
                    controller.marcado = True
                    Indice = i
                    time.sleep(0.2)
                    break

                #Esto es para mover
                if (mousePosX-Xo)**2 + (mousePosY-Yo)**2 <= Radiocuad and controller.leftClickOn:
                    controller.agarrado = True
                    break

                #Esto es para activar el hint del valor medio
                if controller.hint:
                    
                    if sg.findNode(NodoDef,"Nodo" + str(i)).valores == MedianaValores:
                        aux.childs = [CirculoShearing]
                        gpusNumbers[index].shader = 4
                        contadorespecial = 25
                if not controller.hint and contadorespecial == 25:
                    if sg.findNode(NodoDef,"Nodo" + str(i)).valores == MedianaValores:
                        aux.childs = [CirculoMorado]
                        gpusNumbers [index].shader = 2
                        contadorespecial = -1
                






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
            aux.childs = [CirculoMorado]
            gpusNumbers [index].shader = 2

        
        if controller.elegir:
            if aux.click2:
                aux.childs = [NodoTextura]
                gpusNumbers[index].shader = 4
        
        if controller.arreglar:
            controller.arreglar = False
            controller.marcado = False
            controller.elegir = False
            sg.findNode(NodoDef,"CNodo" + str(Indice) +"trasladado").click = False
            sg.findNode(NodoDef,"CNodo" + str(Indice2) +"trasladado").click2 = False
            sg.findNode(NodoDef,"CNodo" + str(Indice) +"trasladado").childs = [CirculoMorado]
            gpusNumbers [Indice].shader = 2
            sg.findNode(NodoDef,"CNodo" + str(Indice2) +"trasladado").childs = [CirculoMorado]
            gpusNumbers [Indice2].shader = 2
            Indice = -1
            Indice2 = -1






        ########################################
        ########################################
        ########################################
        
        sg.drawSceneGraphNodeDefinitivo(NodoDef, pipeline, textPipeline,texturePipeline, Color,Color2, Color3,"transform")
        sg.drawSceneGraphNodeDefinitivo(NodoError, pipeline, textPipeline, texturePipeline, Color, Color2, Color3, "transform")
        

        glfw.swap_buffers(window)


        ########################################
        ########################################
        ########################################




    NodoError.clear()
    NodoDef.clear()

    glfw.terminate()