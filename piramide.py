"""
### Primeiro, vamos importar as bibliotecas necessárias.
"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np

"""### Inicializando janela"""

glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE);
window = glfw.create_window(700, 700, "Piramide", None, None)
glfw.make_context_current(window)

"""### GLSL (OpenGL Shading Language)

Aqui veremos nosso primeiro código GLSL.

É uma linguagem de shading de alto nível baseada na linguagem de programação C.

Nós estamos escrevendo código GLSL como se "strings" de uma variável (mas podemos ler de arquivos texto). Esse código, depois, terá que ser compilado e linkado ao nosso programa. 

Iremos aprender GLSL conforme a necessidade do curso. Usarmos uma versão do GLSL mais antiga, compatível com muitos dispositivos.

### GLSL para Vertex Shader

No Pipeline programável, podemos interagir com Vertex Shaders.

No código abaixo, estamos fazendo o seguinte:

* Definindo uma variável chamada position do tipo vec2.
* Definindo uma variável chamada mat_transformation do tipo mat4 (matriz 4x4). Use ela como matriz de transformação, resultante de uma sequências de outras transformações (e.g. rotação + translação)
* Usamos vec2, pois nosso programa (na CPU) irá enviar apenas duas coordenadas para plotar um ponto. Podemos mandar três coordenadas (vec3) e até mesmo quatro coordenadas (vec4).
* void main() é o ponto de entrada do nosso programa (função principal)
* gl_Position é uma variável especial do GLSL. Variáveis que começam com 'gl_' são desse tipo. Nesse caso, determina a posição de um vértice. Observe que todo vértice tem 4 coordenadas, por isso nós combinamos nossa variável vec2 com uma variável vec4. Além disso, nós modificamos nosso vetor com base em uma matriz de transformação, conforme estudado na Aula05.
"""

vertex_code = """
        attribute vec3 position;
        uniform mat4 mat_transformation;
        void main(){
            gl_Position = mat_transformation * vec4(position,1.0);
        }
        """

"""### GLSL para Fragment Shader

No Pipeline programável, podemos interagir com Fragment Shaders.

No código abaixo, estamos fazendo o seguinte:

* void main() é o ponto de entrada do nosso programa (função principal)
* gl_FragColor é uma variável especial do GLSL. Variáveis que começam com 'gl_' são desse tipo. Nesse caso, determina a cor de um fragmento. Nesse caso é um ponto, mas poderia ser outro objeto (ponto, linha, triangulos, etc).

### Possibilitando modificar a cor.

Nos exemplos anteriores, a variável gl_FragColor estava definida de forma fixa (com cor R=0, G=0, B=0).

Agora, nós vamos criar uma variável do tipo "uniform", de quatro posições (vec4), para receber o dado de cor do nosso programa rodando em CPU.
"""

fragment_code = """
        uniform vec4 color;
        void main(){
            gl_FragColor = color;
        }
        """

"""### Requisitando slot para a GPU para nossos programas Vertex e Fragment Shaders"""

# Request a program and shader slots from GPU
program  = glCreateProgram()
vertex   = glCreateShader(GL_VERTEX_SHADER)
fragment = glCreateShader(GL_FRAGMENT_SHADER)

"""### Associando nosso código-fonte aos slots solicitados"""

# Set shaders source
glShaderSource(vertex, vertex_code)
glShaderSource(fragment, fragment_code)

"""### Compilando o Vertex Shader

Se há algum erro em nosso programa Vertex Shader, nosso app para por aqui.
"""

# Compile shaders
glCompileShader(vertex)
if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(vertex).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Vertex Shader")

"""### Compilando o Fragment Shader

Se há algum erro em nosso programa Fragment Shader, nosso app para por aqui.
"""

glCompileShader(fragment)
if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(fragment).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Fragment Shader")

"""### Associando os programas compilado ao programa principal"""

# Attach shader objects to the program
glAttachShader(program, vertex)
glAttachShader(program, fragment)

"""### Linkagem do programa"""

# Build program
glLinkProgram(program)
if not glGetProgramiv(program, GL_LINK_STATUS):
    print(glGetProgramInfoLog(program))
    raise RuntimeError('Linking error')
    
# Make program the default program
glUseProgram(program)

"""### Preparando dados para enviar a GPU

Nesse momento, nós compilamos nossos Vertex e Program Shaders para que a GPU possa processá-los.

Por outro lado, as informações de vértices geralmente estão na CPU e devem ser transmitidas para a GPU.
"""

# preparando espaço para 16 vértices usando 3 coordenadas (x,y,z)
vertices = np.zeros(16, [("position", np.float32, 3)])

"""### Modelando um Cubo

Existem diferentes formas de modelar um cubo. Nós usaremos uma estratégia baseada no Quadrado com TRIANGLE_STRIP, conforme vimos na Aula04.Ex05. Assim, um quadrado é modelado usando dois triângulos e precisamos de apenas quatro vértices para isso (devido ao TRIANGLE_STRIP).
"""

# preenchendo as coordenadas de cada vértice
vertices['position'] = [
    (-0.5,-0.5,+0.5),(+0.5,-0.5,+0.5),(-0.5,-0.5,-0.5),(+0.5,-0.5,-0.5),    #base quadrada
    (-0.5,-0.5,-0.5),(+0.5,-0.5,-0.5),(0,+0.5,0),                           #triângulo 1  
    (+0.5,-0.5,+0.5),(+0.5,-0.5,-0.5),(0,+0.5,0),                           #triângulo 2  
    (-0.5,-0.5,-0.5),(-0.5,-0.5,+0.5),(0,+0.5,0),                           #triângulo 3      
    (-0.5,-0.5,0.5),(+0.5,-0.5,+0.5),(0,+0.5,0)                             #triângulo 4             
]

"""### Para enviar nossos dados da CPU para a GPU, precisamos requisitar um slot."""

# Request a buffer slot from GPU
buffer = glGenBuffers(1)
# Make this buffer the default one
glBindBuffer(GL_ARRAY_BUFFER, buffer)

"""### Abaixo, nós enviamos todo o conteúdo da variável vertices.

Veja os parâmetros da função glBufferData [https://www.khronos.org/registry/OpenGL-Refpages/gl4/html/glBufferData.xhtml]
"""

# Upload data
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)
glBindBuffer(GL_ARRAY_BUFFER, buffer)

"""### Associando variáveis do programa GLSL (Vertex Shaders) com nossos dados

Primeiro, definimos o byte inicial e o offset dos dados.
"""

# Bind the position attribute
# --------------------------------------
stride = vertices.strides[0]
offset = ctypes.c_void_p(0)

"""Em seguida, soliciamos à GPU a localização da variável "position" (que guarda coordenadas dos nossos vértices). Nós definimos essa variável no Vertex Shader."""

loc = glGetAttribLocation(program, "position")
glEnableVertexAttribArray(loc)

"""A partir da localização anterior, nós indicamos à GPU onde está o conteúdo (via posições stride/offset) para a variável position (aqui identificada na posição loc).

Outros parâmetros:

* Definimos que possui duas coordenadas
* Que cada coordenada é do tipo float (GL_FLOAT)
* Que não se deve normalizar a coordenada (False)

Mais detalhes: https://www.khronos.org/registry/OpenGL-Refpages/gl4/html/glVertexAttribPointer.xhtml
"""

glVertexAttribPointer(loc, 3, GL_FLOAT, False, stride, offset)

"""###  Vamos pegar a localização da variável color (uniform) do Fragment Shader para que possamos alterá-la em nosso laço da janela!"""

loc_color = glGetUniformLocation(program, "color")

"""### Capturando eventos de teclado e modificando variáveis para a matriz de transformação"""

d = 0.0       # rotação
t = 0.0       # translação
s = 1.0       # escala

def key_event(window,key,scancode,action,mods):
    global d, s, t

    if key == 263: d -= 0.01        # seta para a esquerda (rotação)
    elif key == 262: d += 0.01      # seta para a direita  (rotação)
    elif key == 265: s += 0.01      # seta para cima (escala)
    elif key == 264: s -= 0.01      # seta para baixo (escala)
    elif key == 65: t -= 0.01       # a (translação)
    elif key == 83: t += 0.01       # s (translação)
    
glfw.set_key_callback(window,key_event)

"""### Nesse momento, nós exibimos a janela!"""

glfw.show_window(window)

"""### Loop principal da janela.
Enquanto a janela não for fechada, esse laço será executado. É neste espaço que trabalhamos com algumas interações com a OpenGL.


Usaremos o GL_TRIANGLE_STRIP e modelaremos uma face do Cubo por vez, por questões didáticas. Iremos colorir cada face do Cubo com uma cor diferente.
"""

import math
glEnable(GL_DEPTH_TEST) ### importante para 3D

def multiplica_matriz(a,b):
    m_a = a.reshape(4,4)
    m_b = b.reshape(4,4)
    m_c = np.dot(m_a,m_b)
    c = m_c.reshape(1,16)
    return c

while not glfw.window_should_close(window):

    glfw.poll_events() 
    
    ### rotação da pirâmide                  
    cos_d = math.cos(d)
    sin_d = math.sin(d)
    
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glClearColor(1.0, 1.0, 1.0, 1.0)
    
    mat_rotation_z = np.array([     cos_d, -sin_d, 0.0, 0.0, 
                                    sin_d,  cos_d, 0.0, 0.0, 
                                    0.0,      0.0, 1.0, 0.0, 
                                    0.0,      0.0, 0.0, 1.0], np.float32)
    
    mat_rotation_x = np.array([     1.0,   0.0,    0.0, 0.0, 
                                    0.0, cos_d, -sin_d, 0.0, 
                                    0.0, sin_d,  cos_d, 0.0, 
                                    0.0,   0.0,    0.0, 1.0], np.float32)
    
    mat_rotation_y = np.array([     cos_d,  0.0, sin_d, 0.0, 
                                    0.0,    1.0,   0.0, 0.0, 
                                    -sin_d, 0.0, cos_d, 0.0, 
                                    0.0,    0.0,   0.0, 1.0], np.float32)

    mat_translation = np.array([    1.0, 0.0, 0.0, t, 
                                    0.0, 1.0, 0.0, t, 
                                    0.0, 0.0, 1.0, t, 
                                    0.0, 0.0, 0.0, 1.0], np.float32)

    mat_scale = np.array([          s,   0.0, 0.0, 0.0,
                                    0.0, s,   0.0, 0.0, 
                                    0.0, 0.0, s,   0.0,
                                    0.0, 0.0, 0.0, 1.0], np.float32)
    
    mat_transform = multiplica_matriz(mat_rotation_z,mat_rotation_x)
    mat_transform = multiplica_matriz(mat_rotation_y,mat_transform)
    mat_transform = multiplica_matriz(mat_translation,mat_transform)
    mat_transform = multiplica_matriz(mat_scale,mat_transform)

    loc = glGetUniformLocation(program, "mat_transformation")
    glUniformMatrix4fv(loc, 1, GL_TRUE, mat_transform)

    #glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
   
    
    glUniform4f(loc_color, 1, 0, 0, 1.0)    ### vermelho
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

    glUniform4f(loc_color, 0, 1, 0, 1.0)    ### verde
    glDrawArrays(GL_TRIANGLE_STRIP, 4, 3)

    glUniform4f(loc_color, 0, 0, 1, 1.0)    ### azul
    glDrawArrays(GL_TRIANGLE_STRIP, 7, 3)

    glUniform4f(loc_color, 1, 1, 0, 1.0)    ### amarelo
    glDrawArrays(GL_TRIANGLE_STRIP, 10, 3)

    glUniform4f(loc_color, 1, 0.5, 0, 1.0)  ### laranja
    glDrawArrays(GL_TRIANGLE_STRIP, 13, 3)
    
    glfw.swap_buffers(window)

glfw.terminate()