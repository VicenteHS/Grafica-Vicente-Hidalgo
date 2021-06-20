# coding=utf-8
"""Using 2 different textures in the same Fragment Shader"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
from grafica.assets_path import getAssetPath

from grafica.gpu_shape import GPUShape, SIZE_IN_BYTES


# We extend the functionality of a GPUShape with an additional texture.
class TexGPUShape(GPUShape):
    def __init__(self):
        """VAO, VBO, EBO and texture handlers to GPU memory"""
        super().__init__()
        self.texture2 = None

    def __str__(self):
        return super().__str__() + "  tex=" + str(self.texture2)

    def clear(self):
        """Freeing GPU memory"""

        super().clear()
        if self.texture2 != None:
            glDeleteTextures(1, [self.texture2])

# Shader that handles two textures
class Displacement2D:

    def __init__(self):

        vertex_shader = """
            #version 330

            uniform mat4 transform;

            in vec3 position;
            in vec2 texCoords;

            out vec2 outTexCoords;

            void main()
            {
                gl_Position = transform * vec4(position, 1.0f);
                outTexCoords = texCoords;
            }
            """

        fragment_shader = """
            #version 330

            in vec2 outTexCoords;

            out vec4 outColor;

            uniform sampler2D WaterText;
            uniform sampler2D DisplaceText;
            uniform float time;
            uniform float max;

            void main()
            {
                float T = time * 0.01;
                vec2 TCoords = vec2(outTexCoords.s + T, outTexCoords.t + T);
                vec4 Noise = texture(DisplaceText, TCoords);
                float Displace = Noise.r * max;
                vec2 DisplaceCoords = vec2(outTexCoords.x + sin(Displace), outTexCoords.y + cos(Displace));
                outColor = texture(WaterText, DisplaceCoords);
            }
            """

        # Compiling our shader program
        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + 2d texture coordinates => 3*4 + 2*4 = 20 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        texCoords = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(3 * SIZE_IN_BYTES))
        glEnableVertexAttribArray(texCoords)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, TexGPUShape)

        glBindVertexArray(gpuShape.vao)
        # Binding the first texture
        glActiveTexture(GL_TEXTURE0 + 0)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
        # Binding the second texture
        glActiveTexture(GL_TEXTURE0 + 1)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture2)

        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)



# Creating a multi lighting with a displacement pipeline.
class Displacement3D:

    def __init__(self):
        vertex_shader = """
            #version 330
            
            in vec3 position;
            in vec2 texCoords;
            in vec3 normal;

            out vec3 fragPosition;
            out vec2 fragTexCoords;
            out vec3 fragNormal;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            void main()
            {
                fragPosition = vec3(model * vec4(position, 1.0));
                fragTexCoords = texCoords;
                fragNormal = mat3(transpose(inverse(model))) * normal;  
                
                gl_Position = projection * view * vec4(fragPosition, 1.0);
            }
            """

        fragment_shader = """
            #version 330

            in vec3 fragNormal;
            in vec3 fragPosition;
            in vec2 fragTexCoords;

            out vec4 fragColor;
            // Posiciones de las fuentes de luz
            vec3 lightPos0 = vec3(10f, 5f, 9f); 
            vec3 lightPos1 = vec3(20f, 25f, 7f); 
            vec3 lightPos2 = vec3(40f, 48f, 5f); 
            vec3 lightPos3 = vec3(60f, 55f, 3f);
            vec3 lightPos4 = vec3(75f, 70f, 1f);
            vec3 lightPos5 = vec3(90f, 90f, 0f);

            uniform vec3 viewPosition; 
            uniform vec3 La;
            uniform vec3 Ld;
            uniform vec3 Ls;
            uniform vec3 Ka;
            uniform vec3 Kd;
            uniform vec3 Ks;
            uniform uint shininess;
            uniform float constantAttenuation;
            uniform float linearAttenuation;
            uniform float quadraticAttenuation;

            uniform sampler2D WaterText;
            uniform sampler2D DisplaceText;
            uniform float time;
            uniform float maximo;

            void main()
            {
                vec3 ambient = Ka * La;

                // Here i use the displacement
                float T = time * 0.01;
                vec2 TCoords = vec2(fragTexCoords.s + T, fragTexCoords.t + T);
                vec4 Noise = texture(DisplaceText, TCoords);
                float Displace = Noise.r * maximo;
                vec2 DisplaceCoords = vec2(fragTexCoords.x + sin(Displace), fragTexCoords.y + cos(Displace));


                vec4 fragOriginalColor = texture(WaterText, DisplaceCoords);
                vec3 normalizedNormal = normalize(fragNormal);

                // Vector para sumar la contribucion de cada fuente de luz
                vec3 result = vec3(0.0f, 0.0f, 0.0f);
                
                // Vector que almacena las fuentes de luz
                vec3 lights[6] = vec3[](lightPos0, lightPos1, lightPos2, lightPos3, lightPos4, lightPos5);

                // Se itera por cada fuente de luz para calcular su contribucion
                for (int i = 0; i < 6; i++)
                {
                    // direccion a la fuente de luz de la iteacion actual
                    vec3 toLight = lights[i] - fragPosition;

                    // Lo demas es exactamente igual
                    vec3 lightDir = normalize(toLight);
                    float diff = max(dot(normalizedNormal, lightDir), 0.0);
                    vec3 diffuse = Kd * Ld * diff;
                    
                    // specular
                    vec3 viewDir = normalize(viewPosition - fragPosition);
                    vec3 reflectDir = reflect(-lightDir, normalizedNormal);  
                    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
                    vec3 specular = Ks * Ls * spec;

                    // attenuation
                    float distToLight = length(toLight);
                    float attenuation = constantAttenuation
                        + linearAttenuation * distToLight
                        + quadraticAttenuation * distToLight * distToLight;
                    
                    // Se suma la contribucion calculada en la iteracion actual
                    result += ((diffuse + specular) / attenuation) ;
                }

                // El calculo final es con la suma final
                result = (ambient + result) * fragOriginalColor.rgb;
                fragColor = vec4(result, 1.0);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color + 3d normals => 3*4 + 2*4 + 3*4 = 32 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(color, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
        glEnableVertexAttribArray(normal)

        # Unbinding current vao
        glBindVertexArray(0)

    
    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)

        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)


    # def drawCall(self, gpuShape, mode=GL_TRIANGLES):
    #     assert isinstance(gpuShape, TexGPUShape)

    #     glBindVertexArray(gpuShape.vao)
    #     # Binding the first texture
    #     glActiveTexture(GL_TEXTURE0 + 0)
    #     glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
    #     # Binding the second texture
    #     glActiveTexture(GL_TEXTURE0 + 1)
    #     glBindTexture(GL_TEXTURE_2D, gpuShape.texture2)

    #     glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

    #     # Unbind the current VAO
    #     glBindVertexArray(0)





# Shader that handles two textures
class Displacement3DNoLights:

    def __init__(self):

        vertex_shader = """
            #version 330
            
            in vec3 position;
            in vec2 texCoords;
            in vec3 normal;

            out vec3 fragPosition;
            out vec2 fragTexCoords;
            out vec3 fragNormal;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            void main()
            {
                fragPosition = vec3(model * vec4(position, 1.0));
                fragTexCoords = texCoords;
                fragNormal = mat3(transpose(inverse(model))) * normal;  
                
                gl_Position = projection * view * vec4(fragPosition, 1.0);
            }
            """

        fragment_shader = """
            #version 330

            in vec2 outTexCoords;

            out vec4 outColor;

            uniform sampler2D WaterText;
            uniform sampler2D DisplaceText;
            uniform float time;
            uniform float max;

            void main()
            {
                float T = time * 0.01;
                vec2 TCoords = vec2(outTexCoords.s + T, outTexCoords.t + T);
                vec4 Noise = texture(DisplaceText, TCoords);
                float Displace = Noise.r * max;
                vec2 DisplaceCoords = vec2(outTexCoords.x + sin(Displace), outTexCoords.y + cos(Displace));
                outColor = texture(WaterText, DisplaceCoords);
            }
            """

        # Compiling our shader program
        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + 2d texture coordinates => 3*4 + 2*4 = 20 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        texCoords = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(3 * SIZE_IN_BYTES))
        glEnableVertexAttribArray(texCoords)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, TexGPUShape)

        glBindVertexArray(gpuShape.vao)
        # Binding the first texture
        glActiveTexture(GL_TEXTURE0 + 0)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
        # Binding the second texture
        glActiveTexture(GL_TEXTURE0 + 1)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture2)

        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)



# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.mousePos = (0.0, 0.0)

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

    else:
        print('Unknown key')


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit(1)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Displacemente view", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)


    # A simple shader program with position and texture coordinates as inputs.
    pipeline = Displacement2D()


    # Setting up the clear screen color
    glClearColor(0.25, 0.25, 0.25, 1.0)

    # Creating shapes on GPU memory
    shape = bs.createTextureQuad(1, 1)
    gpuShape = TexGPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    gpuShape.texture = es.textureSimpleSetup(
        getAssetPath("Textura2.PNG"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    gpuShape.texture2 = es.textureSimpleSetup(
        getAssetPath("Textura1.PNG"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)

    currentMousePos = [width/2, height/2]

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        theta = 6 * glfw.get_time()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(pipeline.shaderProgram)
        # Drawing the shapes        
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.uniformScale(2))
        
        # Binding samplers to both texture units
        glUniform1i(glGetUniformLocation(pipeline.shaderProgram, "WaterText"), 0)
        glUniform1i(glGetUniformLocation(pipeline.shaderProgram, "DisplaceText"), 1)

        # Sending the mouse vertical location to our shader
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "time"), theta)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "max"), 0.6)

        pipeline.drawCall(gpuShape)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)
    
    # freeing GPU memory
    gpuShape.clear()

    glfw.terminate()