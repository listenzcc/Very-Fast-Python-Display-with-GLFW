"""
File: fixed-large-triangle.py
Author: Chuncheng Zhang
Date: 2025-10-13
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Drawing the fixed large triangle.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2025-10-13 ------------------------
# Requirements and constants
import glfw

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from util.easy_imports import *
from util.glfw_window import GLFWWindow

# %%
# Setup triangle points
vertices = np.array([
    # x, y, z, r, g, b, a
    0.0, 0.5, 0.0, 1.0, 0.0, 0.0, 0.5,  # A
    0.5, -0.5, 0.0, 0.0, 1.0, 0.0, 0.5,  # B
    -0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 0.5,  # C
], dtype=np.float32)

shader_script = {
    'vert': open('./shader/triangle/a.vert').read(),
    'frag': open('./shader/triangle/a.frag').read()
}

# %% ---- 2025-10-13 ------------------------
# Function and class


def compile(vertices=vertices):
    # Create VAO and VBO
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    # Bind to array buffer
    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Setup vertex attr (x, y, z)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 7 * 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # Setup colors attr (r, g, b, a)
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE,
                          7 * 4, ctypes.c_void_p(3*4))
    glEnableVertexAttribArray(1)

    # Unbind
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    # Compile shader
    shader = compileProgram(
        compileShader(shader_script['vert'], GL_VERTEX_SHADER),
        compileShader(shader_script['frag'], GL_FRAGMENT_SHADER),
    )

    return shader, vao


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
    glDrawArrays(GL_TRIANGLES, 0, 3)
    glBindVertexArray(0)

    t = glfw.get_time()

    wnd.draw_text("Hello Modern OpenGL!",
                  math.sin(t), math.cos(t), 1.0, color=(1.0, 0.5, 0.2))
    wnd.draw_text("中文测试", -0.5, 0.5, 1.0, color=(0.2, 0.8, 1.0))
    wnd.draw_text("中文测试", 0, 0, 1.0, color=(1.0, 1.0, 1.0))

    wnd.draw_rect(0, 0.0, 0.2, 0.3, 0.5)

    return


# %% ---- 2025-10-13 ------------------------
# Play ground
wnd = GLFWWindow()
wnd.load_font('resource/font/MTCORSVA.TTF')
wnd.init_window()

shader, vao = compile()

glfw.set_key_callback(wnd.window, key_callback)

wnd.render_loop(main_render)

wnd.cleanup()

# %% ---- 2025-10-13 ------------------------
# Pending


# %% ---- 2025-10-13 ------------------------
# Pending
