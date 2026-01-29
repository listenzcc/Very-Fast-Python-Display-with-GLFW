"""
File: large-circle-v2.py
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
    'vert': open('./shader/circle/b.vert').read(),
    'frag': open('./shader/circle/b.frag').read()
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


class KeyboardHandler:
    def __init__(self):
        self.shift_map = self._create_shift_map()

    def _create_shift_map(self):
        '''创建Shift键映射表'''
        return {
            '-': '_', '=': '+', '9': '(', '0': ')',
            '[': '{', ']': '}', ';': ':', "'": '"',
            ',': '<', '.': '>', '/': '?', '\\': '|',
            '`': '~', '1': '!', '2': '@', '3': '#',
            '4': '$', '5': '%', '6': '^', '7': '&',
            '8': '*'
        }

    def process_key(self, key, mods):
        '''处理按键，返回转换后的字符'''
        base_char = chr(key).lower()
        has_shift = mods & glfw.MOD_SHIFT

        if has_shift:
            # 检查是否是特殊字符
            if base_char in self.shift_map:
                return self.shift_map[base_char]
            # 否则转换为大写
            return base_char.upper()
        else:
            return base_char


# 使用示例
keyboard = KeyboardHandler()


def key_callback(window, key, scancode, action, mods):
    '''
    Key press callback.
    '''

    # Only be interested in PRESS event.
    if not action == glfw.PRESS:
        return

    c = keyboard.process_key(key, mods)

    print(key, c, scancode, action, mods)

    # In command mode
    if opt.command_mode:
        # Clear command and escape command_mode
        if key == glfw.KEY_ESCAPE:
            opt.clear_command()
            opt.command_mode = False

        # Append the command
        if c in 'abcdefghijklmnopqrstuvwxyz1234567890-_=+. ()[],':
            opt.command.append(c)

        if key == glfw.KEY_BACKSPACE:
            opt.command.pop()

        if key == glfw.KEY_ENTER:
            cmd = ''.join(opt.command).replace('=', ' ').strip()
            try:
                key, value = cmd.split(' ', 1)
                value = value.strip()
                print(f'{key=}, {value=}')
                eval(f'setattr(opt, "{key}", {value})')
            except:
                pass
            opt.clear_command()
            opt.command_mode = False

        return

    # Enter the command mode
    if c in ';:' and mods:
        opt.command_mode = True
        return

    # Close the window if ESC is pressed.
    if key == glfw.KEY_ESCAPE:
        print("ESC is pressed, bye bye.")
        glfw.set_window_should_close(window, True)

    # Toggle rotation
    if c == 'r':
        opt.rotation_speed = 1-opt.rotation_speed

    # Toggle blink
    if c == 'b':
        opt.blink_toggle = not opt.blink_toggle

    # Change focus color
    if c == 'f':
        opt.focus_color = tuple([random.random() for _ in range(3)])

    # Toggle dump_mode
    if c == 's':
        opt.switch_idle_display_mode()

    # Increase blink speed
    if c in '=+':
        opt.blink_freq = min(opt.blink_freq+(1 if mods else 0.1), 20)

    # Decree blink speed
    if c in '-_':
        opt.blink_freq = max(opt.blink_freq-(1 if mods else 0.1), 0.5)

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

    # wnd.draw_text("Hello Modern OpenGL!",
    #               math.sin(t), math.cos(t), 1.0, color=(1.0, 0.5, 0.2))
    # wnd.draw_text("中文测试", 0.7, 0.5, 1.0, color=(0.2, 0.8, 1.0))
    # wnd.draw_text("中文测试", 0.7, 0, 1.0, color=(1.0, 1.0, 1.0))
    # wnd.draw_rect(0.7, 0.0, 0.2, 0.3, 0.5)

    # Display options
    options = opt.__str__().split('||')
    for i, o in enumerate(options):
        wnd.draw_text(o, -0.9, 0.9-i*0.06, 0.8,
                      TextAnchor.L, color=(1.0, 1.0, 1.0))

    # Display commands
    if opt.command_mode:
        wnd.draw_text('>> ' + ''.join(opt.command), 0, 0.8, 1.0,
                      TextAnchor.B, color=(1.0, 1.0, 1.0))

    return


class Options:
    ratio: float  # screen width/height
    tic: float  # tic of the session
    wedges: int = 12  # how many wedges
    max_r: float = 0.7  # max r limit
    ring_edges: list = [0.2, 0.3, 0.5, 0.6, 0.9]  # ring edges

    # Focus
    focus_r1: float = 0.02  # r1 of focus (inner)
    focus_r2: float = 0.05  # r2 of focus (outer)
    focus_color: tuple = (0, 0, 1)  # rgb color of focus

    # Blink toggle
    blink_toggle: bool = False  # toggle blinking

    # Grids
    grids: int = 4  # Patch splits into grids x grids parts

    # selected patches (idxRing, idxWedge, freq)
    selected_patches: list = []

    # how to display when idle (not blinking)
    # 0 for gradient mode
    # 1 for checkbox mode
    # 2 for checkboxGrid mode
    idle_display_mode: int = 0

    # rotate for text
    rotation_speed: float = 0

    # UI
    command_mode: bool = False
    command: list = []

    def __str__(self):
        def convert_to_str(k, e):
            if k == 'focus_color':
                return '(' + ', '.join(f'{g:0.2f}' for g in e) + ')'
            if isinstance(e, float):
                return f'{e:0.2f}'
            return f'{e}'
        return '||'.join([f'{k}={convert_to_str(k, self.__getattribute__(k))}' for k in self.__annotations__])

    def clear_command(self):
        self.command = []

    def get_time(self):
        return time.time() - self.tic

    def reset_time(self):
        self.tic = time.time()

    def switch_idle_display_mode(self):
        self.idle_display_mode += 1
        self.idle_display_mode %= 3

    def set(self, shader):
        loc = glGetUniformLocation(shader, 'uIdleDisplayMode')
        glUniform1i(loc, self.idle_display_mode)

        loc = glGetUniformLocation(shader, 'uRatio')
        glUniform1f(loc, self.ratio)

        loc = glGetUniformLocation(shader, 'uTime')
        glUniform1f(loc, self.get_time())

        loc = glGetUniformLocation(shader, 'uWedges')
        glUniform1i(loc, self.wedges)

        loc = glGetUniformLocation(shader, 'uBlinkToggle')
        glUniform1i(loc, self.blink_toggle)

        loc = glGetUniformLocation(shader, 'uRotationSpeed')
        glUniform1f(loc, self.rotation_speed)

        loc = glGetUniformLocation(shader, 'uFocusR1')
        glUniform1f(loc, self.focus_r1)

        loc = glGetUniformLocation(shader, 'uFocusR2')
        glUniform1f(loc, self.focus_r2)

        loc = glGetUniformLocation(shader, 'uFocusColor')
        glUniform3f(loc, *self.focus_color)

        loc = glGetUniformLocation(shader, 'uCommandMode')
        glUniform1i(loc, self.command_mode)

        loc = glGetUniformLocation(shader, 'uGrids')
        glUniform1i(loc, self.grids)

        # Selected patches
        n = len(self.selected_patches)
        assert n < 100, f'Too many selected_patches({n=})'
        loc = glGetUniformLocation(shader, 'uNumSelectedPatches')
        glUniform1i(loc, n)
        for i in range(n):
            loc = glGetUniformLocation(shader, f"uSelectedPatches[{i}]")
            glUniform3f(loc, *self.selected_patches[i])

        # Ring edges
        n = len(self.ring_edges)
        assert n < 100, f'Too many ring_edges({n=})'
        loc = glGetUniformLocation(shader, 'uNumRings')
        glUniform1i(loc, n)
        loc = glGetUniformLocation(shader, 'uMaxR')
        glUniform1f(loc, self.ring_edges[-1])
        for i in range(n):
            loc = glGetUniformLocation(shader, f"uRingEdges[{i}]")
            glUniform1f(loc, self.ring_edges[i])


# %% ---- 2026-01-28 ------------------------
# Play ground
wnd = GLFWWindow()
wnd.load_font('resource/font/MTCORSVA.TTF')
wnd.init_window()

keyboard = KeyboardHandler()

opt = Options()
opt.ratio = wnd.width / wnd.height
opt.reset_time()
opt.selected_patches = [
    (0, 1, 10),
    (1, 2, 20),
]

print(opt)

shader, vao, index_count = compile_square()

glfw.set_key_callback(wnd.window, key_callback)

wnd.render_loop(main_render)

wnd.cleanup()

# %% ---- 2026-01-28 ------------------------
# Pending


# %% ---- 2026-01-28 ------------------------
# Pending
