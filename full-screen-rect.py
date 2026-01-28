"""
File: full-screen-rect.py
Author: Chuncheng Zhang
Date: 2026-01-28
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Render full screen rect to the screen.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2026-01-28 ------------------------
# Requirements and constants
import glfw

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from util.easy_imports import *
from util.glfw_window import GLFWWindow

# Setup triangle points
# 方形顶点数据：4个顶点，每个包含位置(3) + 颜色(4)
vertices = np.array([
    # 位置(x,y,z)     颜色(r,g,b,a)
    -1,  1, 0, 1, 0, 0, 0.5,  # 0: 左上
    1,  1, 0, 0, 1, 0, 0.5,  # 1: 右上
    1, -1, 0, 0, 0, 1, 0.5,  # 2: 右下
    -1, -1, 0, 1, 1, 0, 0.5,  # 3: 左下
], dtype=np.float32)

# 加上索引缓冲 (IBO/EBO)
indices = np.array([
    0, 1, 2,  # 第一个三角形
    2, 3, 0,  # 第二个三角形
], dtype=np.uint32)

shader_script = {
    'vert': open('./shader/triangle/a.vert').read(),
    'frag': open('./shader/triangle/a.frag').read()
}

# %% ---- 2026-01-28 ------------------------
# Function and class


def compile_square():
    # 创建VAO、VBO、EBO
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)

    glBindVertexArray(vao)

    # 绑定顶点数据
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # 绑定索引数据
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                 indices.nbytes, indices, GL_STATIC_DRAW)

    # 设置顶点属性（stride仍然是28字节）
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 7 * 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE,
                          7 * 4, ctypes.c_void_p(3*4))
    glEnableVertexAttribArray(1)

    # 注意：EBO要保持在VAO绑定状态下
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)  # 这会保存EBO绑定

    # 编译着色器
    shader = compileProgram(
        compileShader(shader_script['vert'], GL_VERTEX_SHADER),
        compileShader(shader_script['frag'], GL_FRAGMENT_SHADER),
    )

    return shader, vao, len(indices)  # 返回索引数量


def key_callback(window, key, scancode, action, mods):
    '''
    Key press callback.
    '''

    # Only be interested in PRESS event.
    if not action == glfw.PRESS:
        return

    print(key, chr(key), scancode, action, mods)

    # Close the window if ESC is pressed.
    if key == glfw.KEY_ESCAPE:
        print("ESC is pressed, bye bye.")
        glfw.set_window_should_close(window, True)

    return


def main_render():
    glUseProgram(shader)
    glBindVertexArray(vao)
    # glDrawArrays(GL_TRIANGLES, 0, 3)
    glDrawElements(GL_TRIANGLES, index_count, GL_UNSIGNED_INT, None)
    glBindVertexArray(0)

    t = glfw.get_time()

    wnd.draw_text("Hello Modern OpenGL!",
                  math.sin(t), math.cos(t), 1.0, color=(1.0, 0.5, 0.2))
    wnd.draw_text("中文测试", -0.5, 0.5, 1.0, color=(0.2, 0.8, 1.0))
    wnd.draw_text("中文测试", 0, 0, 1.0, color=(1.0, 1.0, 1.0))

    wnd.draw_rect(0.7, 0.0, 0.2, 0.3, 0.5)

    return


# %% ---- 2026-01-28 ------------------------
# Play ground
wnd = GLFWWindow()
wnd.load_font('resource/font/MTCORSVA.TTF')
wnd.init_window()

shader, vao, index_count = compile_square()

glfw.set_key_callback(wnd.window, key_callback)

wnd.render_loop(main_render)

wnd.cleanup()

# %% ---- 2026-01-28 ------------------------
# Pending


# %% ---- 2026-01-28 ------------------------
# Pending
