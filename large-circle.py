"""
File: large-circle.py
Author: Chuncheng Zhang
Date: 2026-01-28
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Render large circle to the screen.

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
from util.glfw_window import GLFWWindow, TextAnchor

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
    'vert': open('./shader/circle/a.vert').read(),
    'frag': open('./shader/circle/a.frag').read()
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

    if chr(key).lower() == 'r':
        opt.rotation_speed = 1-opt.rotation_speed

    if chr(key).lower() == 'b':
        opt.blink_toggle = not opt.blink_toggle

    if chr(key).lower() in ['=', '+']:
        opt.blink_freq = min(opt.blink_freq+0.1, 20)

    if chr(key).lower() in ['-', '_']:
        opt.blink_freq = max(opt.blink_freq-0.1, 0.5)

    # Close the window if ESC is pressed.
    if key == glfw.KEY_ESCAPE:
        print("ESC is pressed, bye bye.")
        glfw.set_window_should_close(window, True)

    return


def main_render():
    glUseProgram(shader)

    opt.set(shader)
    # ratio_loc = glGetUniformLocation(shader, 'uRatio')
    # glUniform1f(ratio_loc, opt.ratio)

    glBindVertexArray(vao)
    # glDrawArrays(GL_TRIANGLES, 0, 3)
    glDrawElements(GL_TRIANGLES, index_count, GL_UNSIGNED_INT, None)
    glBindVertexArray(0)

    t = glfw.get_time()

    wnd.draw_text("Hello Modern OpenGL!",
                  math.sin(t), math.cos(t), 1.0, color=(1.0, 0.5, 0.2))
    wnd.draw_text("中文测试", 0.7, 0.5, 1.0, color=(0.2, 0.8, 1.0))
    wnd.draw_text("中文测试", 0.7, 0, 1.0, color=(1.0, 1.0, 1.0))
    wnd.draw_text(opt.__str__(), 0, -0.8, 0.8,
                  TextAnchor.B, color=(1.0, 1.0, 1.0))

    wnd.draw_rect(0.7, 0.0, 0.2, 0.3, 0.5)

    return


class Options:
    ratio: float
    tic: float
    wedges: int
    rings: int
    maxr: float

    blink_freq: float
    blink_toggle: bool

    rotation_speed: float

    def __str__(self):
        def convert_to_str(e):
            if isinstance(e, float):
                return f'{e:0.2f}'
            return f'{e}'
        return ', '.join([f'{k}={convert_to_str(self.__getattribute__(k))}' for k in self.__annotations__])

    def get_time(self):
        return time.time() - self.tic

    def reset_time(self):
        self.tic = time.time()

    def set(self, shader):
        loc = glGetUniformLocation(shader, 'uRatio')
        glUniform1f(loc, self.ratio)

        loc = glGetUniformLocation(shader, 'uTime')
        glUniform1f(loc, self.get_time())

        loc = glGetUniformLocation(shader, 'uWedges')
        glUniform1i(loc, self.wedges)

        loc = glGetUniformLocation(shader, 'uRings')
        glUniform1i(loc, self.rings)

        loc = glGetUniformLocation(shader, 'uMaxR')
        glUniform1f(loc, self.maxr)

        loc = glGetUniformLocation(shader, 'uBlinkFreq')
        glUniform1f(loc, self.blink_freq)

        loc = glGetUniformLocation(shader, 'uBlinkToggle')
        glUniform1i(loc, self.blink_toggle)

        loc = glGetUniformLocation(shader, 'uRotationSpeed')
        glUniform1f(loc, self.rotation_speed)


# %% ---- 2026-01-28 ------------------------
# Play ground
wnd = GLFWWindow()
wnd.load_font('resource/font/MTCORSVA.TTF')
wnd.init_window()

opt = Options()
opt.ratio = wnd.width / wnd.height
opt.reset_time()
opt.wedges = 12
opt.rings = 5
opt.maxr = 0.7
opt.rotation_speed = 0.0
opt.blink_freq = 3
opt.blink_toggle = False

print(opt)

shader, vao, index_count = compile_square()

glfw.set_key_callback(wnd.window, key_callback)

wnd.render_loop(main_render)

wnd.cleanup()

# %% ---- 2026-01-28 ------------------------
# Pending


# %% ---- 2026-01-28 ------------------------
# Pending
