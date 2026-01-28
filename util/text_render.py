"""
File: text_render.py
Author: Chuncheng Zhang
Date: 2025-10-09
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    TextRender

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2025-10-09 ------------------------
# Requirements and constants
from .easy_imports import *

import freetype
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GL.shaders import ShaderCompilationError
from collections import OrderedDict

# %%
# 顶点着色器
vertex_shader_source = open(
    './shader/font/shadow.vert', encoding='utf-8').read()
# 片段着色器
fragment_shader_source = open(
    './shader/font/shadow.frag', encoding='utf-8').read()

# %% ---- 2025-10-09 ------------------------
# Function and class


class TextShader:
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

        # 预分配缓冲区大小（6个顶点 * 4个float * 500个字符）
        glBufferData(GL_ARRAY_BUFFER, 6 * 4 * 500 *
                     sizeof(GLfloat), None, GL_DYNAMIC_DRAW)

        # 设置顶点属性指针
        # 位置属性
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE,
                              4 * sizeof(GLfloat), ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        # 纹理坐标属性
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 *
                              sizeof(GLfloat), ctypes.c_void_p(2 * sizeof(GLfloat)))
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        glUseProgram(self.shader_program)
        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "projection"),
                           1, GL_FALSE, self.projection)


class TextRenderer(TextShader):
    # I believe windows should have it.
    # And I believe it has every char I want.
    default_font_path = 'c:\\windows\\fonts\\msyh.ttc'
    default_font_size = 24

    def __init__(self, max_cache_size=1024):
        super().__init__()
        self.face = None
        self.characters = OrderedDict()  # 使用有序字典实现LRU缓存
        self.max_cache_size = max_cache_size  # 最大缓存字符数

    def load_font(self, font_path, size=None):
        """初始化字体"""
        if size is None:
            size = self.default_font_size

        self.face = freetype.Face(font_path)
        self.face.set_char_size(size << 6)

        self.default_face = freetype.Face(self.default_font_path)
        self.default_face.set_char_size(size << 6)

        logger.info(f'Using font: {font_path} ({size})')
        logger.info(f'Using font(default): {self.default_font_path} ({size})')

    def load_char(self, char):
        if char in self.characters:
            return self.characters[char]

        face = self.face if self.face.get_char_index(
            char) > 0 else self.default_face
        face.load_char(char, freetype.FT_LOAD_RENDER)
        bitmap = face.glyph.bitmap
        glyph = face.glyph

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)

        # 重要：单字节对齐，针对宽度不是4的情况
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        if bitmap.pixel_mode == freetype.FT_PIXEL_MODE_MONO:
            data = self.mono_to_grayscale(bitmap)
        else:
            # 直接构造 numpy array, 注意 shape/类型
            data = np.array(bitmap.buffer, dtype=np.ubyte)

        # 纹理参数
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # 上传纹理（单通道）
        if bitmap.width > 0 and bitmap.rows > 0:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, bitmap.width,
                         bitmap.rows, 0, GL_RED, GL_UNSIGNED_BYTE, data)
        else:
            empty_data = np.array([0], dtype=np.ubyte)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, 1, 1, 0,
                         GL_RED, GL_UNSIGNED_BYTE, empty_data)

        # 解绑纹理
        glBindTexture(GL_TEXTURE_2D, 0)

        self.characters[char] = {
            'texture': texture,
            'size': (bitmap.width, bitmap.rows),
            'bearing': (glyph.bitmap_left, glyph.bitmap_top),
            'advance': glyph.advance.x >> 6
        }

        return self.characters[char]

    def bounding_box(self, text, scale=1.0):
        """
        计算文本的边界框

        The (width, height) gives the bounding box of the text.
        The (width, height2) gives the real range of the text, which contains the descender of each char.

        :param text str: the input text.
        :param scale float: the scale factor.

        :return width int: the width of the input text.
        :return height int: the height of the input text, it shows the bottom line of the string.
        :return height2 int: the real height of the input text, it contains the descender of each char.
        """
        width = 0
        height = 0
        height2 = 0
        for char in text:
            ch = self.load_char(char)
            width += ch['advance'] * scale
            height = max(height, ch['size'][1] * scale)
            # height2 = max(
            #     height2, (ch['bbox_height'] + ch['descender']) * scale)
        height2 = height

        return width, height, height2

    def render_text(self, text, x, y, scale=1.0, color=(1.0, 1.0, 1.0)):
        """
        Render the text on position x, y.
        """
        if not text:
            return

        glUseProgram(self.shader_program)
        glUniform3f(glGetUniformLocation(self.shader_program, "textColor"),
                    color[0], color[1], color[2])

        glActiveTexture(GL_TEXTURE0)
        glBindVertexArray(self.vao)

        # 为整个文本准备顶点数据
        vertices = []
        textures_used = []  # 记录使用的纹理和对应的顶点范围

        start_index = 0

        for char in text:
            self.load_char(char)
            if char not in self.characters:
                continue  # 跳过未加载的字符

            ch = self.characters[char]

            # 计算位置
            xpos = x + ch['bearing'][0] * scale
            ypos = y - (ch['size'][1] - ch['bearing'][1]) * scale
            w = ch['size'][0] * scale
            h = ch['size'][1] * scale
            x += ch['advance'] * scale

            # 跳过完全透明的字符（如空格）
            if not all([w > 0, h > 0]):
                continue

            # 每个字符的6个顶点（2个三角形）
            # a----b
            # |1 / |
            # | / 2|
            # c----d
            # But the char on the screen is like
            # c----d
            # |2 / |
            # | / 1|
            # a----b
            _vertices = [
                # Triangle 1
                [xpos,     ypos + h, 0.0, 0.0],  # c
                [xpos + w, ypos,     1.0, 1.0],  # b
                [xpos,     ypos,     0.0, 1.0],  # a
                # Triangle 2
                [xpos,     ypos + h, 0.0, 0.0],  # c
                [xpos + w, ypos + h, 1.0, 0.0],  # d
                [xpos + w, ypos,     1.0, 1.0],  # b
            ]

            [vertices.extend(e) for e in _vertices]

            # 记录这个字符使用的纹理和顶点范围
            end_index = len(vertices) // 4  # 每个顶点4个float
            textures_used.append({
                'texture': ch['texture'],
                'start': start_index,
                'count': end_index - start_index
            })
            start_index = end_index

        if vertices:
            # 上传顶点数据
            vertices_array = np.array(vertices, dtype=np.float32)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferSubData(GL_ARRAY_BUFFER, 0,
                            vertices_array.nbytes, vertices_array)

            # 按纹理分组绘制
            for texture_info in textures_used:
                glBindTexture(GL_TEXTURE_2D, texture_info['texture'])
                glDrawArrays(
                    GL_TRIANGLES, texture_info['start'], texture_info['count'])

        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)
        return

    def mono_to_grayscale(self, bitmap):
        """将单色位图转换为灰度"""
        width = bitmap.width
        rows = bitmap.rows
        pitch = bitmap.pitch

        # 创建灰度数据数组
        data = np.zeros((rows, width), dtype=np.ubyte)

        for y in range(rows):
            for x in range(width):
                byte_index = y * pitch + x // 8
                bit_index = 7 - (x % 8)  # FT 位图是 MSB 优先

                if byte_index < len(bitmap.buffer):
                    byte_val = bitmap.buffer[byte_index]
                    bit_val = (byte_val >> bit_index) & 1
                    data[y, x] = 255 if bit_val else 0

        return data.flatten()

# %% ---- 2025-10-09 ------------------------
# Play ground


# %% ---- 2025-10-09 ------------------------
# Pending


# %% ---- 2025-10-09 ------------------------
# Pending
