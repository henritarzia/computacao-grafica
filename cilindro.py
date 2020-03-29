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
window = glfw.create_window(700, 700, "Cilindro", None, None)
glfw.make_context_current(window)

"""
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

### Modelando um Cilindro
"""

import math

PI = 3.141592
r = 0.3                                 # raio
h = 0.7                                 # altura
num_sectors = 30                        # qtd de sectors (longitude)
num_stacks = 30                         # qtd de stacks (latitude)

# grid sectos vs stacks (longitude vs latitude)
sector_step = (PI*2)/num_sectors        # variar de 0 até 2π
stack_step = h/num_stacks               # variar de 0 até h

# Entrada: angulo, raio e altura
# Saida: coordenadas no cilindro
def F(t,r,h):
    x = r*math.cos(t)
    y = r*math.sin(t)
    z = h
    return (x,y,z)

# vamos gerar um conjunto de vertices representantes poligonos
# para a superficie do cilindro.
# cada poligono eh representado por dois triangulos
vertices_list = []
for i in range(0,num_sectors):      # para cada sector (longitude)
    for j in range(0,num_stacks):   # para cada stack (latitude)
        
        u = i * sector_step         # angulo setor
        v = j * stack_step          # altura stack
        
        un = 0 # angulo do proximo sector
        if i+1 == num_sectors: un = PI*2
        else: un = (i+1) * sector_step
            
        vn = 0 # altura do proximo stack
        if j+1 == num_stacks: vn = h
        else: vn = (j+1) * stack_step
        
        # verticies do poligono
        p0 = F(u,r,v)
        p1 = F(u,r,vn)
        p2 = F(un,r,v)
        p3 = F(un,r,vn)
        
        # triangulo 1 (primeira parte do poligono)
        vertices_list.append(p0)
        vertices_list.append(p2)
        vertices_list.append(p1)
        
        # triangulo 2 (segunda e ultima parte do poligono)
        vertices_list.append(p3)
        vertices_list.append(p1)
        vertices_list.append(p2)

vertices_side = len(vertices_list)

# tampas do cilindro
vertices_cover = 30  
cover_sup = []
cover_inf = []

#tampa inferior
counter = 0
angle = 0.0
for counter in range(vertices_cover):
    angle += 2*PI / vertices_cover 
    x = math.cos(angle) * r
    y = math.sin(angle) * r
    ci = (x,y,0.0)
    vertices_list.append(ci)

#tampa superior
counter = 0
angle = 0.0   
for counter in range(vertices_cover): 
    angle += 2*PI / vertices_cover 
    x = math.cos(angle) * r
    y = math.sin(angle) * r
    cs = (x,y,h)
    vertices_list.append(cs)

vertices_cilindro = len(vertices_list)
vertices = np.zeros(vertices_cilindro, [("position", np.float32, 3)])
vertices['position'] = np.array(vertices_list)

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


Usaremos o GL_TRIANGLE para modelar os triângulos (que formarão outros polígonos) da superfície do nosso cilindro.
"""

import math
import random as rand
d = 0.0
glEnable(GL_DEPTH_TEST) ### importante para 3D

def multiplica_matriz(a,b):
    m_a = a.reshape(4,4)
    m_b = b.reshape(4,4)
    m_c = np.dot(m_a,m_b)
    c = m_c.reshape(1,16)
    return c

while not glfw.window_should_close(window):

    glfw.poll_events() 
    
    ### apenas para visualizarmos a cilindro rotacionando
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
    for triangle in range(0,vertices_side,3):
       rand.seed(triangle)
       R = rand.random()
       G = rand.random()
       B = rand.random()        
       glUniform4f(loc_color, R, G, B, 1.0)
       
       glDrawArrays(GL_TRIANGLES, triangle, 3)     

    #tampa inferior
    glUniform4f(loc_color, 1, 0, 0, 1.0)
    glDrawArrays(GL_TRIANGLE_FAN, vertices_side, vertices_cover) 

   
    #tampa superior
    glUniform4f(loc_color, 0, 0, 1, 1.0)
    glDrawArrays(GL_TRIANGLE_FAN, vertices_side + vertices_cover,vertices_cover) 
    
    glfw.swap_buffers(window)

glfw.terminate()