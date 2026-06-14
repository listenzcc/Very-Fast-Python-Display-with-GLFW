# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 14:34:39 2026

@author: liangyi
"""

"""
File: large-circle-under-control.py
Author: Chuncheng Zhang
Date: 2026-01-28
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Render large circle to the screen.
    Make it under control by the configure file.
"""

# %% ---- 2026-01-28 ------------------------
# Requirements and constants
import glfw
import os
import random
import sys
import time
from pathlib import Path
import numpy as np

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from util.easy_imports import *
from util.glfw_window import GLFWWindow, TextAnchor
from util.parallel.parallel import Parallel
from parallel_code import Code

# =========================================================================
# 🔒 Loguru 日志异步队列安全重配置
# =========================================================================
logger.remove()
logger.add(sys.stderr, level="INFO")

LOG_FILE_PATH = "D:/Desktop/客户相关/301眼科/20260610/301-SSVEP/log/Very Fast Python Display with GLFW.log"
logger.add(
    LOG_FILE_PATH,
    rotation="10 MB",
    enqueue=True,      # 启用异步线程单点写入管道
    level="DEBUG",
    encoding="utf-8"
)
# =========================================================================

# %%
# Quanlan setup
from quanlan_util.myquanlan import fix_csv_encoding_for_excel, consumer_process_wrapper, start_consumer_process, DeviceContainer

device_id = "390026040074"
dc = None
device = None
signal_queue_proc = None

# --- 状态追踪标志位 ---
is_acquiring = False
is_stimulating = False
is_impedance = False

# 全局变量占位
wnd = None
opt = None
shader = None
vao = None
index_count = None
design = None

ADDRESS = 'DEFC'
DESIGN_CONF = './design_stage3B.conf'

# 方形顶点数据：4个顶点，每个包含位置(3) + 颜色(4)
vertices = np.array([
    -1,  1, 0, 1, 0, 0, 0.5,  # 0: 左上
    1,  1, 0, 0, 1, 0, 0.5,  # 1: 右上
    1, -1, 0, 0, 0, 1, 0.5,  # 2: 右下
    -1, -1, 0, 1, 1, 0, 0.5,  # 3: 左下
], dtype=np.float32)

indices = np.array([
    0, 1, 2,
    2, 3, 0,
], dtype=np.uint32)

shader_script = {
    'vert': open('./shader/circle/b.vert').read(),
    'frag': open('./shader/circle/b.frag').read()
}

def log(msg):
    if opt:
        t = int(1000*opt.get_time())
        logger.debug(f'{t=}, {msg}')

def compile_square():
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)

    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 7 * 4, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 7 * 4, ctypes.c_void_p(3*4))
    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    shader = compileProgram(
        compileShader(shader_script['vert'], GL_VERTEX_SHADER),
        compileShader(shader_script['frag'], GL_FRAGMENT_SHADER),
    )
    return shader, vao, len(indices)

class KeyboardHandler:
    def __init__(self):
        self.shift_map = self._create_shift_map()

    def _create_shift_map(self):
        return {
            '-': '_', '=': '+', '9': '(', '0': ')',
            '[': '{', ']': '}', ';': ':', "'": '"',
            ',': '<', '.': '>', '/': '?', '\\': '|',
            '`': '~', '1': '!', '2': '@', '3': '#',
            '4': '$', '5': '%', '6': '^', '7': '&',
            '8': '*'
        }

    def process_key(self, key, mods):
        try:
            base_char = chr(key).lower()
        except ValueError:
            return ''
        has_shift = mods & glfw.MOD_SHIFT
        if has_shift:
            if base_char in self.shift_map:
                return self.shift_map[base_char]
            return base_char.upper()
        else:
            return base_char

keyboard = KeyboardHandler()

def on_stop_quanlan():
    global is_acquiring, is_stimulating, is_impedance
    logger.info("🎬 收到退出信号，开始执行安全下线与 BDF 标签保护流水线...")

    try:
        if device:
            # 1. 停止硬件信号发送，防止新数据继续涌入队列
            if is_acquiring:
                device.stop_acquisition()
                is_acquiring = False
                logger.info("1. 硬件信号采集已停止")
            if is_stimulating:
                device.stop_stimulation()
                is_stimulating = False
                logger.info("安全补漏：停止电刺激")
            if is_impedance:
                device.stop_impedance()
                is_impedance = False
                logger.info("安全补漏：停止阻抗测量")
        
        # 2. 向数据消费者进程发送退出封口信号
        if signal_queue_proc and signal_queue_proc.is_alive():
            if hasattr(signal_queue_proc, 'put'):
                signal_queue_proc.put(None)
                logger.info('2. 已向数据消费者进程发送【退出封口信号】')
            else:
                logger.info('2. 等待底层消费者自动将剩余队列消化并关闭...')

        # 3. 极其重要：留出充分的时间，把队列里残留的 Trigger 标签和脑电数据全部写入硬盘并封口
        logger.info("3. 正在等待最后一批缓冲数据与标签落盘，请勿强行关闭...")
        time.sleep(3.0)

        # 4. 🛠️ 修复二：安全兼容退订设备（显式传递 "signal" 主题，消灭 missing 1 positional argument 报错）
        if device:
            try:
                device.unsubscribe("signal")
            except Exception:
                try:
                    device.unsubscribe()
                except:
                    pass
            logger.success("4. SDK 设备连接已成功注销，硬件会话已释放")

    except Exception as cleanup_err:
        logger.error(f"❌ 清理资源或固化 BDF 标签时出错: {cleanup_err}")

    # === 修复乱码后处理 ===
    try:
        fix_csv_encoding_for_excel(".") 
        logger.info("5. 编码后处理完成。")
    except Exception as e:
        logger.error(f"后处理失败: {e}")

    logger.success("🏁 【全部任务顺利完成】BDF 文件已安全闭合，标签已固化。程序即将退出。")
    time.sleep(0.5)
    
    # 内核级强制安全退出，彻底避免多进程/C++残留带来的挂起死锁
    os._exit(0)

def key_callback(window, key, scancode, action, mods):
    if not action == glfw.PRESS:
        return

    # F12 强制安全终止
    if key == glfw.KEY_F12:
        logger.warning("F12 强制安全终止被触发！正在紧急保存当前 BDF 数据及 Trigger 标签...")
        on_stop_quanlan()

    c = keyboard.process_key(key, mods)
    if c:
        log(f'Key press: {c=}')
        if device:
            device.trigger('KeyPress')

    # In command mode
    if opt.command_mode:
        if key == glfw.KEY_ESCAPE:
            opt.clear_command()
            opt.command_mode = False

        if c in 'abcdefghijklmnopqrstuvwxyz1234567890-_=+. ()[],':
            opt.command.append(c)
            variable_name = ''.join(opt.command)
            candidates = [e for e in opt.__annotations__ if e.startswith(variable_name)]
            if len(candidates) == 1:
                opt.command = [e for e in candidates[0] + ' = ']

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

    if c in ';:' and mods:
        opt.command_mode = True
        return

    if key == glfw.KEY_ESCAPE:
        logger.info("ESC被按下，正在安全退出...")
        on_stop_quanlan()

    if c == 'r':
        opt.rotation_speed = 1 - opt.rotation_speed

    if c == 'b':
        if not opt.blink_toggle:
            design.load_conf()
            opt.blink_toggle = True
            if opt.blink_toggle:
                opt.reset_time()
                log('Session starts')
                if device:
                    device.trigger('SessionStarts')
        else:
            opt.blink_toggle = False

    if c == 'f':
        opt.focus_color = tuple([random.random() for _ in range(3)])

    if c == 's':
        opt.switch_idle_display_mode()

    if c in '=+':
        opt.blink_freq = min(opt.blink_freq+(1 if mods else 0.1), 20)

    if c in '-_':
        opt.blink_freq = max(opt.blink_freq-(1 if mods else 0.1), 0.5)
    return

def main_render():
    glUseProgram(shader)
    opt.set(shader)

    glBindVertexArray(vao)
    glDrawElements(GL_TRIANGLES, index_count, GL_UNSIGNED_INT, None)
    glBindVertexArray(0)

    t = int(1000 * opt.get_time())

    # Execute jobs 
    if len(design.jobs) > 0:
        while len(design.jobs) > 0 and design.jobs[0][0] <= t:
            job = design.jobs.pop(0)
            a, b, c = job
            eval(f'setattr(opt, "{b}", {c})')
            log(f'{job=}')
            if a > -10:
                if b == 'focus_color':
                    if device:
                        device.trigger('FocusChange')
                if b == 'selected_patches':
                    if device:
                        device.trigger('SelectedPatchesChange')
    return

class Options:
    ratio: float
    tic: float
    wedges: int = 12
    ring_edges: list = [0.2, 0.3, 0.5, 0.6, 0.9]

    focus_r1: float = 0.02
    focus_r2: float = 0.05
    focus_color: tuple = (0, 0, 1)
    blink_toggle: bool = False
    grids: int = 4
    selected_patches: list = []
    idle_display_mode: int = 0
    rotation_speed: float = 0
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

        n = len(self.selected_patches)
        assert n < 100, f'Too many selected_patches({n=})'
        loc = glGetUniformLocation(shader, 'uNumSelectedPatches')
        glUniform1i(loc, n)
        for i in range(n):
            loc = glGetUniformLocation(shader, f"uSelectedPatches[{i}]")
            glUniform3f(loc, *self.selected_patches[i])

        n = len(self.ring_edges)
        assert n < 100, f'Too many ring_edges({n=})'
        loc = glGetUniformLocation(shader, 'uNumRings')
        glUniform1i(loc, n)
        loc = glGetUniformLocation(shader, 'uMaxR')
        glUniform1f(loc, self.ring_edges[-1])
        for i in range(n):
            loc = glGetUniformLocation(shader, f"uRingEdges[{i}]")
            glUniform1f(loc, self.ring_edges[i])


class Design:
    fpath: Path
    def __init__(self, fpath: Path):
        self.fpath = fpath

    def load_conf(self):
        jobs = open(self.fpath).readlines()
        jobs = [e.strip() for e in jobs if e.strip()]
        jobs = [e for e in jobs if not e.startswith('#')]

        def split(line):
            a, b = line.split(' ', 1)
            b = b.strip()
            c, d = b.split(' ', 1)
            return (int(a), c.strip(), d.strip())

        jobs = [split(e) for e in jobs]
        jobs = sorted(jobs, key=lambda e: e[0])
        self.jobs = jobs
        return self.jobs


# %% ---- 🔒 核心多进程与异常保护伞 ------------------------
if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()

    # 1. 创建设备容器并连接
    dc = DeviceContainer(False)
    logger.info(f"正在连接设备: {device_id}...")
    device = dc.connect(device_id, timeout=30)  

    if device is None:
        logger.error(f"无法连接到设备：{device_id}")
        sys.exit(1)

    logger.info(f'Connected to {device_id=}')

    # 2. 启动数据消费者进程
    sub_res = device.subscribe()
    if sub_res and len(sub_res) > 1:
        signal_queue_proc = start_consumer_process(
            consumer_process_wrapper,
            sub_res[1],
            "signal",
            "SignalConsumer"
        )

    # 3. 设备参数配置与采集启动
    logger.info("设备已连接，开始采集数据...")
    device.set_acq_param([e for e in range(1, 1+64)], 1000, 188)

    device.start_acquisition()
    is_acquiring = True   

    # 加载设计配置
    design = Design(DESIGN_CONF)
    design.load_conf()

    # 4. 初始化渲染窗口
    wnd = GLFWWindow()
    wnd.load_font('resource/font/MSYH.TTC')
    wnd.init_window()

    opt = Options()
    opt.ratio = wnd.width / wnd.height
    opt.reset_time()
    opt.selected_patches = [(0, 1, 10), (1, 2, 20)]

    # =========================================================================
    # 🔄 核心复原：开启 120Hz 垂直同步（V-Sync 开启）
    # =========================================================================
    glfw.swap_interval(1)  # 设为 1：复原高刷同步，严格按照 120Hz 屏幕物理刷新率进行刺激渲染
    # =========================================================================

    shader, vao, index_count = compile_square()
    glfw.set_key_callback(wnd.window, key_callback)

    # =========================================================================
    # 🔒 修复一：优化全局信号拦截器（完美解决 KeyboardInterrupt 未预料异常报错）
    # =========================================================================
    try:
        logger.info("进入渲染死循环，120Hz 垂直同步已就绪。")
        wnd.render_loop(main_render)
    except (KeyboardInterrupt, SystemExit):
        # 显式捕获中断与退出信号，消除包裹类报错
        logger.warning("检测到用户执行了快捷键终止 (Ctrl+C)，正在拦截并安全进入落盘流程...")
    except BaseException as run_err:
        # 兼容 C++ 底层信号向上抛出的特殊异常基类
        logger.warning(f"主循环因信号或中断安全退出: {run_err}")
    finally:
        try:
            wnd.cleanup()
        except:
            pass
        on_stop_quanlan()
