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
window = glfw.create_window(1000, 1000, "Mola 2D", None, None)
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

#Coordenadas de cada vértice
points = []   #lista de pontos da mola
x = 0         #coordenada x
y = 0         #coordenada y

#Obtém os pontos da mola por meio da função sin(24*a)/10
for a in np.arange(-186,192,6):
    y = math.radians(a)/24
    x = math.sin(24*a)/10
    c = (x,y)
    points.append(c)  

size = len(points)    #número de vértices da mola

#Prepara espaço para 21 vértices usando 2 coordenadas (x,y) -- vértices da mola
vertices = np.zeros(size, [("position", np.float32, 2)])
vertices['position'] = np.array(points)

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
returning = False  #indicador de retorno à posição central 
direction = 0      #direção do salto

xs = points[0][0]       #x de referência para a escala
ys = points[0][1]       #y de referência para a escala

yr = points[int(size/2)][1]    #y de referência para a rotação (vértice médio da mola)
xr = 0                         #x de referência para a rotação

xt = 0

def key_event(window,key,scancode,action,mods):
    global s_y, direction, xr, xt
    global release, jump, returning

    #Ao pressionar a seta para baixo, é exercida força de compressão na mola
    if key == 264 and action != 0 and jump == False: release = False
    if key == 264 and action == 0: release = True

    #Caso a tecla esteja sendo pressionada e a mola não atingiu a compressão máxima, aplica compressão
    if not release and s_y >= 0.16: s_y -= 0.02
    #Caso a tecla tenha sido solta e a mola apresente o valor mínimo de compressão, indica ocorrência de salto
    if release and s_y <= 0.3: 
        jump = True                          #ativa flag de salto
        if not returning:                 
            direction = rand.choice([-1,1])  #define a direção do salto da mola (1: lado esquerdo / -1: lado direito)
            xr = 0.4 * (-direction)
        else: xr = 0.4 * direction             

glfw.set_key_callback(window,key_event)

"""Exibição da tela"""

glfw.show_window(window)

"""Loop principal"""

angle = 0.0     #ângulo da etapa do salto
sin = 0.0       #seno do ângulo 
cos = 1.0       #cosseno do ângulo
speed = 2.0     #incremento no ângulo a cada iteração

def multiplica_matriz(a,b):
    m_a = a.reshape(4,4)
    m_b = b.reshape(4,4)
    m_c = np.dot(m_a,m_b)
    c = m_c.reshape(1,16)
    return c

while not glfw.window_should_close(window):
    #Altera variáveis para realização do salto
    if jump and s_y == 1.0:
        sin = math.sin(math.radians(angle))
        cos = math.cos(math.radians(angle)) 
        if not returning: angle += speed * direction
        else: angle -= speed * direction 

    #Retorna a mola à sua posição original
    if jump and (angle == 180 + speed or angle == -(180 + speed)):
        jump = False
        returning = not returning 
        angle = 0
        sin = 0.0
        cos = 1.0
        if returning: xt = 2 * xr 
        else: xt = 0 

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
    mat_reference_before_s = np.array([  1.0, 0.0, 0.0, xs, 
                                         0.0, 1.0, 0.0, ys, 
                                         0.0, 0.0, 1.0, 0.0, 
                                         0.0, 0.0, 0.0, 1.0], np.float32)

    mat_reference_after_s = np.array([  1.0, 0.0, 0.0, -xs, 
                                        0.0, 1.0, 0.0, -ys, 
                                        0.0, 0.0, 1.0, 0.0, 
                                        0.0, 0.0, 0.0, 1.0], np.float32)

    #Matrizes para manutenção do ponto de referência (base) da mola
    mat_reference_before_r = np.array([  1.0, 0.0, 0.0, xr, 
                                         0.0, 1.0, 0.0, yr, 
                                         0.0, 0.0, 1.0, 0.0, 
                                         0.0, 0.0, 0.0, 1.0], np.float32)

    mat_reference_after_r = np.array([  1.0, 0.0, 0.0, -xr, 
                                        0.0, 1.0, 0.0, -yr, 
                                        0.0, 0.0, 1.0, 0.0, 
                                        0.0, 0.0, 0.0, 1.0], np.float32)

    #O eixo y corresponde ao único passível de modificação do coeficiente
    #de escala por causa da deformação sofrida (compressão da mola) 
    mat_scale = np.array([  1.0, 0.0, 0.0, 0.0,
                            0.0, s_y, 0.0, 0.0,
                            0.0, 0.0, 1.0, 0.0,
                            0.0, 0.0, 0.0, 1.0], np.float32)

    #Matrizes para manutenção do ponto de referência (base) da mola
    T = np.array([  1.0, 0.0, 0.0, xt, 
                    0.0, 1.0, 0.0, 0.0, 
                    0.0, 0.0, 1.0, 0.0, 
                    0.0, 0.0, 0.0, 1.0], np.float32)
    
    #Matriz de escala com ponto de referência
    S = multiplica_matriz(mat_reference_before_s, mat_scale)
    S = multiplica_matriz(S, mat_reference_after_s)

    #Matriz de rotação com ponto de referência
    R = multiplica_matriz(mat_reference_before_r, mat_rotation)
    R = multiplica_matriz(R, mat_reference_after_r)

    mat_transform = multiplica_matriz(R,S)
    mat_transform = multiplica_matriz(T,mat_transform)

    loc = glGetUniformLocation(program, "mat")
    glUniformMatrix4fv(loc, 1, GL_TRUE, mat_transform)
    
    glDrawArrays(GL_LINE_STRIP, 0, len(vertices))

    glfw.swap_buffers(window)

glfw.terminate()