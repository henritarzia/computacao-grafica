"""
# Trabalho 1 - SCC0250
Aluno: Henrique Tadashi Tarzia - 10692210

Prof. Ricardo Marcondes Marcacini
"""

"""Bibliotecas"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import random as rand
import math

"""Janela"""

glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE);
window = glfw.create_window(800, 800, "Mola 2D", None, None)
glfw.make_context_current(window)

"""Vertex Shader"""

vertex_code = """
        attribute vec2 position;
        uniform mat4 mat;
        void main(){
            gl_Position = mat * vec4(position,0.0,1.0);
        }
        """

"""Fragment Shader"""

fragment_code = """
        void main(){
            gl_FragColor = vec4(0.0,0.0,0.0,1.0);
        }
        """

"""Requisição e compilação"""

#Requisita slot para a GPU para os programas Vertex e Fragment Shaders
program  = glCreateProgram()
vertex   = glCreateShader(GL_VERTEX_SHADER)
fragment = glCreateShader(GL_FRAGMENT_SHADER)

#Associa o código-fonte aos slots solicitados
glShaderSource(vertex, vertex_code)
glShaderSource(fragment, fragment_code)

#Compila vertex shader
glCompileShader(vertex)
if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(vertex).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Vertex Shader")

#Compila fragment shader
glCompileShader(fragment)
if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
    error = glGetShaderInfoLog(fragment).decode()
    print(error)
    raise RuntimeError("Erro de compilacao do Fragment Shader")

#Associa objetos ao programa principal
glAttachShader(program, vertex)
glAttachShader(program, fragment)

#Constrói programa
glLinkProgram(program)
if not glGetProgramiv(program, GL_LINK_STATUS):
    print(glGetProgramInfoLog(program))
    raise RuntimeError('Linking error')

#Define o programa como padrão
glUseProgram(program)

"""Definição e associação dos dados"""

#Inicializa gerador de números aleatórios
rand.seed(a=None, version=2)

#Prepara espaço para 21 vértices usando 2 coordenadas (x,y) -- vértices da mola
vertices = np.zeros(21, [("position", np.float32, 2)])

#Calcula as coordenadas de cada vértice

inc_x = 0.0         #posição central da mola no eixo x 
inc_y = -0.6        #posição do vértice inicial da mola no eixo y
dist_x = 0.08       #distância do vértice em relação ao centro da mola na coordernada x
dist_y = 0.012      #valor do vértice em relação ao eixo y
side = 1            #variável auxiliar para identificação do valor da coordenada x em vértices ímpares

x = 0
y = 0

for i in np.arange(21):
    if i % 2 == 0: 
        x = inc_x
    else: 
        x = inc_x + (side * dist_x)
        side *= -1

    #define coordernadas do vértice
    y = i * dist_y + inc_y
    vertices['position'][i] = [x,y]     

xf = vertices['position'][0][0]     #armazena a coordenada x do vértice inicial
yf = vertices['position'][0][1]     #armazena a coordenada y do vértice inicial
size_y = vertices['position'][20][1] - vertices['position'][0][1]

#Requisita um slot de buffer da GPU
buffer = glGenBuffers(1)

#Define esse buffer como padrão 
glBindBuffer(GL_ARRAY_BUFFER, buffer)

#Efetua upload do dos dados
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)
glBindBuffer(GL_ARRAY_BUFFER, buffer)

#Define byte inicial e offset dos dados
stride = vertices.strides[0]
offset = ctypes.c_void_p(0)

#Solicita as coordenadas dos vértices e definir a variável associada no Vertex Shader 
loc = glGetAttribLocation(program, "position")
glEnableVertexAttribArray(loc)

#Indica à GPU onde está o conteúdo para a variável position
glVertexAttribPointer(loc, 2, GL_FLOAT, False, stride, offset)

"""Captura dos eventos do teclado e modificação das variáveis para a matriz de transformação"""

s_y = 1.0          #escala para deformação
release = True     #indicador de aplicação de compressão (False) ou descompressão (True) 
jump = False       #indicador de salto 
direction = 0      #direção do salto

def key_event(window,key,scancode,action,mods):
    global s_y, release, jump, direction

    #Ao pressionar a seta para baixo, é exercida força de compressão na mola
    if key == 264 and action != 0 and jump == False: release = False
    if key == 264 and action == 0: release = True

    #Caso a tecla esteja sendo pressionada e a mola não atingiu a compressão máxima, aplica compressão
    if not release and s_y >= 0.16: s_y -= 0.02
    #Caso a tecla tenha sido solta e a mola apresente o valor mínimo de compressão, indica ocorrência de salto
    if release and s_y <= 0.3: 
        jump = True                      #ativa flag de salto
        direction = rand.choice([-1,1])  #define a direção do salto da mola (1: lado esquerdo / -1: lado direito)

glfw.set_key_callback(window,key_event)

"""Exibição da tela"""

glfw.show_window(window)

"""Loop principal"""

t_x = 0.0       #deslocamento no eixo x
t_y = 0.0       #deslocamento no eixo y
angle = 0.0     #ângulo da etapa do salto
frame = 0       #contador da animação de salto
pos = 0         #posição da mola

sin = 0.0       #seno do ângulo 
cos = 1.0       #cosseno do ângulo

def multiplica_matriz(a,b):
    m_a = a.reshape(4,4)
    m_b = b.reshape(4,4)
    m_c = np.dot(m_a,m_b)
    c = m_c.reshape(1,16)
    return c

while not glfw.window_should_close(window):
    #Altera variáveis para realização do salto
    if jump and s_y == 1.0:
        #cálculo da posição
        pos = int(frame/10) + 1
        #cálculo do deslocamento
        t_x = -direction * pos * 0.15
        t_y = 0.4
        #cálculo do ângulo atual
        angle = direction * 45 * pos
        cos = math.cos( math.radians(angle) )
        sin = math.sin( math.radians(angle) )
        #incremento do contador
        frame += 1

    #Correção da coordenada y na posição final do movimento
    if pos == 4: t_y = size_y

    #Retorna a mola à sua posição original
    if jump and frame == 40:
        jump = False
        direction = 0
        pos = 0
        frame = 0
        cos = 1.0
        sin = 0.0 
        t_x = 0.0
        t_y = 0.0

    glfw.poll_events() 

    glClear(GL_COLOR_BUFFER_BIT) 
    glClearColor(1.0, 1.0, 1.0, 1.0)

    if release and s_y < 1.0: s_y += 0.02
    
    #Matriz para rotação durante salto
    mat_rotation = np.array([  cos, -sin, 0.0, 0.0, 
                               sin,  cos, 0.0, 0.0, 
                               0.0,  0.0, 1.0, 0.0, 
                               0.0,  0.0, 0.0, 1.0], np.float32)
    
    #Matrizes para manutenção do ponto de referência (base) da mola
    mat_reference_before = np.array([  1.0, 0.0, 0.0, xf, 
                                       0.0, 1.0, 0.0, yf, 
                                       0.0, 0.0, 1.0, 0.0, 
                                       0.0, 0.0, 0.0, 1.0], np.float32)

    mat_reference_after = np.array([  1.0, 0.0, 0.0, -xf, 
                                      0.0, 1.0, 0.0, -yf, 
                                      0.0, 0.0, 1.0, 0.0, 
                                      0.0, 0.0, 0.0, 1.0], np.float32)

    #O eixo y corresponde ao único passível de modificação do coeficiente
    #de escala por causa da deformação sofrida (compressão da mola) 
    mat_scale = np.array([  1.0, 0.0, 0.0, 0.0,
                            0.0, s_y, 0.0, 0.0,
                            0.0, 0.0, 1.0, 0.0,
                            0.0, 0.0, 0.0, 1.0], np.float32)

    #Matriz de translação
    T = np.array([  1.0, 0.0, 0.0, t_x, 
                    0.0, 1.0, 0.0, t_y, 
                    0.0, 0.0, 1.0, 0.0, 
                    0.0, 0.0, 0.0, 1.0], np.float32)
    
    #Matriz de escala com ponto de referência
    S = multiplica_matriz(mat_reference_before, mat_scale)
    S = multiplica_matriz(S, mat_reference_after)

    #Matriz de rotação com ponto de referência
    R = multiplica_matriz(mat_reference_before, mat_rotation)
    R = multiplica_matriz(R, mat_reference_after)

    mat_transform = multiplica_matriz(R,S)
    mat_transform = multiplica_matriz(T,mat_transform)

    loc = glGetUniformLocation(program, "mat")
    glUniformMatrix4fv(loc, 1, GL_TRUE, mat_transform)
    
    glDrawArrays(GL_LINE_STRIP, 0, len(vertices))

    glfw.swap_buffers(window)

glfw.terminate()