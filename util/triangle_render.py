"""
File: triangle_render.py
Author: Chuncheng Zhang
Date: 2025-10-16
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Render the triangle.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2025-10-16 ------------------------
# Requirements and constants
from .easy_imports import *

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GL.shaders import ShaderCompilationError

# %%
# 顶点着色器
vertex_shader_source = open(
    './shader/triangle/projection.vert', encoding='utf-8').read()
# 片段着色器
fragment_shader_source = open(
    './shader/triangle/projection.frag', encoding='utf-8').read()

# %% ---- 2025-10-16 ------------------------
# Function and class


class TriangleShader:
    def __init__(self):
        pass

    def init_shader(self, width, height):
        self.width = width
        self.height = height

        # 设置投影矩阵
        self.projection = np.array([
            [2.0/self.width, 0.0, 0.0, 0.0],
            [0.0, 2.0/self.height, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [-1.0, -1.0, 0.0, 1.0]
        ], dtype=np.float32)

        # Compile shaders
        try:
            vertex_shader = compileShader(
                vertex_shader_source, GL_VERTEX_SHADER)
            fragment_shader = compileShader(
                fragment_shader_source, GL_FRAGMENT_SHADER)
            self.shader_program = compileProgram(
                vertex_shader, fragment_shader)
        except ShaderCompilationError as err:
            raise err

        # 生成 VAO、VBO
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        # 预分配缓冲区大小（6个顶点 * 4个float * 100个纹理）
        glBufferData(GL_ARRAY_BUFFER, 6 * 4 * 100 *
                     sizeof(GLfloat), None, GL_DYNAMIC_DRAW)

        # 设置顶点属性指针
        # 位置属性
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE,
                              4 * sizeof(GLfloat), ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE,
                              4 * sizeof(GLfloat), ctypes.c_void_p(2 * sizeof(GLfloat)))
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        glUseProgram(self.shader_program)
        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "projection"),
                           1, GL_FALSE, self.projection)


class TriangleRender(TriangleShader):
    def __init__(self):
        super().__init__()

    def render_triangle(self, x1, y1, x2, y2, x3, y3, color=(1.0, 1.0, 1.0, 1.0), nPos=(0, 0, 1, 0, 0, 1)):
        glUseProgram(self.shader_program)
        glUniform4f(glGetUniformLocation(self.shader_program,
                    'uColor'), color[0], color[1], color[2], color[3])

        glActiveTexture(GL_TEXTURE0)
        glBindVertexArray(self.vao)

        vertices_array = np.array(
            [x1, y1, nPos[0], nPos[1], x2, y2, nPos[2], nPos[3], x3, y3, nPos[4], nPos[5]], dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0,
                        vertices_array.nbytes, vertices_array)

        glDrawArrays(GL_TRIANGLES, 0, 3)

        glBindVertexArray(0)
        pass

# %% ---- 2025-10-16 ------------------------
# Play ground


# %% ---- 2025-10-16 ------------------------
# Pending


# %% ---- 2025-10-16 ------------------------
# Pending
