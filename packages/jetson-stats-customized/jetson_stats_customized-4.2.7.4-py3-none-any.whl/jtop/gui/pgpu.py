# -*- coding: UTF-8 -*-
# This file is part of the jetson_stats package (https://github.com/rbonghi/jetson_stats or http://rnext.it).
# Copyright (c) 2019-2023 Raffaello Bonghi.
#
# License: GNU AGPL v3+

import curses
import glob
import os

from .jtopgui import Page
# Graphics elements
from .lib.common import NColors, plot_name_info, size_min, unit_to_string, size_to_string
from .lib.chart import Chart
from .lib.process_table import ProcessTable
from .lib.linear_gauge import basic_gauge, freq_gauge
from .lib.smallbutton import SmallButton
from .pcontrol import color_temperature


# --------- Thor-aware helpers ---------

def _read_int_file(path):
    try:
        with open(path, "r") as f:
            s = f.read().strip()
            # sysfs değerleri genelde Hz; biz kHz'e indirgeriz
            val = int(s)
            return max(0, val // 1000)
    except Exception:
        return None


def _collect_thor_freqs():
    """
    Thor ve benzeri yeni GPU isimleri için sysfs devfreq yollarını tarar ve
    {cur, min, max} değerlerini kHz cinsinden döndürür.
    Her iki motor (gpu-gpc-0, gpu-nvd-0) varsa, mevcut değerlerin en büyüğünü alırız.
    """
    base = "/sys/devices/platform"
    patterns = [
        os.path.join(base, "**", "gpu-*", "devfreq", "*", "cur_freq"),
        os.path.join(base, "**", "gpu-*", "devfreq", "*", "min_freq"),
        os.path.join(base, "**", "gpu-*", "devfreq", "*", "max_freq"),
    ]
    result = {}

    # cur
    cur_vals = []
    for p in glob.glob(patterns[0], recursive=True):
        v = _read_int_file(p)
        if v is not None:
            cur_vals.append(v)
    if cur_vals:
        result["cur"] = max(cur_vals)

    # min
    min_vals = []
    for p in glob.glob(patterns[1], recursive=True):
        v = _read_int_file(p)
        if v is not None:
            min_vals.append(v)
    if min_vals:
        result["min"] = min(min_vals)

    # max
    max_vals = []
    for p in glob.glob(patterns[2], recursive=True):
        v = _read_int_file(p)
        if v is not None:
            max_vals.append(v)
    if max_vals:
        result["max"] = max(max_vals)

    # governor (opsiyonel; bazı devfreq dizinlerinde var)
    gov_files = glob.glob(os.path.join(base, "**", "gpu-*", "devfreq", "*", "governor"), recursive=True)
    for gf in gov_files:
        try:
            with open(gf, "r") as f:
                result["governor"] = f.read().strip()
                break
        except Exception:
            pass

    return result


def _ensure_freq_dict(gpu_freq):
    """
    jtop'un beklediği yapı:
      {'name': 'Frq', 'cur': kHz, 'min': kHz, 'max': kHz, 'unit': 'k', 'governor': '...' }
    Eksikse Thor sysfs'inden doldurur; hâlâ eksikse çizim sırasında güvenli biçimde atlanır.
    """
    if gpu_freq is None or not isinstance(gpu_freq, dict):
        gpu_freq = {}

    # Eksik anahtarları Thor'dan topla
    need = any(k not in gpu_freq for k in ("cur", "min", "max"))
    if need:
        thor_vals = _collect_thor_freqs()
        for k in ("cur", "min", "max", "governor"):
            if k not in gpu_freq and k in thor_vals:
                gpu_freq[k] = thor_vals[k]

    # jtop gauge beklentileri
    gpu_freq.setdefault("name", "Frq")
    gpu_freq.setdefault("unit", "k")

    return gpu_freq


# --------- UI / Drawing ---------

def gpu_gauge(stdscr, pos_y, pos_x, size, gpu_data, idx):
    gpu_status = gpu_data.get('status', {})
    load_val = gpu_status.get('load', 0.0)

    data = {
        'name': 'GPU' if idx == 0 else 'GPU{idx}'.format(idx=idx),
        'color': NColors.green() | curses.A_BOLD,
        'values': [(load_val, NColors.igreen())],
    }

    # Draw current frequency (defansif)
    freq = gpu_data.get('freq') or {}
    cur_val = None
    try:
        cur_val = freq.get('cur')
    except Exception:
        cur_val = None

    if cur_val is not None:
        curr_string = unit_to_string(cur_val, 'k', 'Hz')
        try:
            stdscr.addstr(pos_y, pos_x + size - 8, curr_string, NColors.italic())
        except curses.error:
            pass

    basic_gauge(stdscr, pos_y, pos_x, size - 10, data, bar=" ")


def compact_gpu(stdscr, pos_y, pos_x, width, jetson):
    line_counter = 0
    if jetson.gpu:
        for idx, gpu in enumerate(jetson.gpu.values()):
            gpu_gauge(stdscr, pos_y + line_counter, pos_x, width, gpu, idx)
            line_counter += 1
    else:
        data = {
            'name': 'GPU',
            'color': NColors.green() | curses.A_BOLD,
            'online': False,
            'coffline': NColors.igreen(),
            'message': 'NVIDIA GPU NOT DETECTED/AVAILABLE',
        }
        basic_gauge(stdscr, pos_y, pos_x, width - 2, data)
        line_counter = 1
    return line_counter


class GPU(Page):

    def __init__(self, stdscr, jetson):
        super(GPU, self).__init__("GPU", stdscr, jetson)
        # Check if grey exist otherwise use white
        COLOR_GREY = 240 if curses.COLORS >= 256 else curses.COLOR_WHITE
        # Initialize GPU chart
        self.draw_gpus = {}
        for gpu_name in self.jetson.gpu:
            type_gpu = "i" if self.jetson.gpu[gpu_name].get('type') == 'integrated' else 'd'
            chart = Chart(jetson, "{t}GPU {name}".format(t=type_gpu, name=gpu_name), self.update_chart,
                          color_text=curses.COLOR_GREEN)
            button_3d_scaling = SmallButton(stdscr, self.action_scaling_3D, info={'name': gpu_name})
            if type_gpu == 'i':
                chart_ram = Chart(jetson, "GPU Shared RAM", self.update_chart_ram,
                                  type_value=float,
                                  color_text=curses.COLOR_GREEN,
                                  color_chart=[COLOR_GREY, curses.COLOR_GREEN])
            else:
                chart_ram = None
            self.draw_gpus[gpu_name] = {'chart': chart, '3d_scaling': button_3d_scaling, 'ram': chart_ram}
        # Add Process table
        self.process_table = ProcessTable(self.stdscr, self.jetson)

    def action_railgate(self, info, selected):
        status_railgate = not self.jetson.gpu.get_railgate(info['name'])
        self.jetson.gpu.set_railgate(info['name'], status_railgate)

    def action_scaling_3D(self, info, selected):
        status_3d_scaling = not self.jetson.gpu.get_scaling_3D(info['name'])
        self.jetson.gpu.set_scaling_3D(info['name'], status_3d_scaling)

    def update_chart(self, jetson, name):
        gpu_name = name.split(" ")[1]
        gpu_data = jetson.gpu.get(gpu_name, {})
        gpu_status = gpu_data.get('status', {})
        return {
            'value': [gpu_status.get('load', 0.0)],
        }

    def update_chart_ram(self, jetson, name):
        parameter = jetson.memory.get('RAM', {})
        max_val = parameter.get("tot", 100)
        cpu_val = parameter.get("used", 0)
        use_val = parameter.get("shared", 0)
        szw, divider, unit = size_min(max_val, start='k')
        used_out = (cpu_val) / divider
        gpu_out = (use_val) / divider
        return {
            'value': [used_out, gpu_out],
            'max': szw,
            'unit': unit
        }

    def draw(self, key, mouse):
        # Screen size
        height, width, first = self.size_page()
        # Measure height (len=0 guard)
        gpu_count = max(1, len(self.jetson.gpu))
        gpu_height = (height * 2 // 3 - 3) // gpu_count

        # Plot all GPU temperatures
        self.stdscr.addstr(first + 1, 1, "Temperatures:", curses.A_NORMAL)
        for idx, name in enumerate(self.jetson.temperature):
            if 'gpu' in name.lower():
                sensor = self.jetson.temperature[name]
                color_temperature(self.stdscr, first + 1, 15, name, sensor)

        # Draw all GPU
        for idx, (gpu_name, gpu_data) in enumerate(self.jetson.gpu.items()):
            chart = self.draw_gpus[gpu_name]['chart']
            chart_ram = self.draw_gpus[gpu_name]['ram']
            gpu_status = gpu_data.get('status', {})
            gpu_freq = _ensure_freq_dict(gpu_data.get('freq'))

            # Set size chart gpu
            size_x = [1, width // 2 - 2]
            size_y = [first + 2 + idx * (gpu_height + 1), first + 2 + (idx + 1) * (gpu_height - 3)]

            # Label & chart
            governor = gpu_freq.get('governor', '')
            label_chart_gpu = "{percent: >3.0f}% - gov: {governor}".format(
                percent=gpu_status.get('load', 0.0), governor=governor
            )
            chart.draw(self.stdscr, size_x, size_y, label=label_chart_gpu)

            # Draw GPU RAM chart if present
            size_x_ram = [1 + width // 2, width - 2]
            if chart_ram is not None:
                mem_data = self.jetson.memory.get('RAM', {})
                total = size_to_string(mem_data.get('tot', 0), 'k')
                shared = size_to_string(mem_data.get('shared', 0), 'k')
                chart_ram.draw(self.stdscr, size_x_ram, size_y, label="{used}/{total}B".format(used=shared, total=total))

            # Status line buttons/info
            button_position = width // 4
            button_idx = 0
            # 3D scaling
            scaling_string = "Active" if gpu_status.get('3d_scaling') else "Disable"
            scaling_status = NColors.green() if gpu_status.get('3d_scaling') else curses.A_NORMAL
            try:
                self.stdscr.addstr(first + 1 + (idx + 1) * gpu_height - 1, 1 + button_idx, "3D scaling:", curses.A_BOLD)
                self.draw_gpus[gpu_name]['3d_scaling'].update(
                    first + 1 + (idx + 1) * gpu_height - 1, 12 + button_idx,
                    scaling_string, key=key, mouse=mouse, color=scaling_status
                )
            except curses.error:
                pass
            button_idx += button_position

            # railgate status
            railgate_string = "Active" if gpu_status.get('railgate') else "Disable"
            railgate_status = NColors.green() if gpu_status.get('railgate') else curses.A_NORMAL
            plot_name_info(self.stdscr, first + 1 + (idx + 1) * gpu_height - 1,
                           1 + button_idx, "Railgate", railgate_string, color=railgate_status)
            button_idx += button_position

            # Power control
            plot_name_info(self.stdscr, first + 1 + (idx + 1) * gpu_height - 1,
                           1 + button_idx, "Power ctrl", gpu_data.get('power_control', ''))
            button_idx += button_position

            # TPC PG Mask
            if 'tpc_pg_mask' in gpu_status:
                tpc_pg_mask_string = "ON" if gpu_status.get('tpc_pg_mask') else "OFF"
                plot_name_info(self.stdscr, first + 1 + (idx + 1) * gpu_height - 1,
                               1 + button_idx, "TPC PG", tpc_pg_mask_string)
                button_idx += button_position

            # GPC per-domain freqs (varsa)
            frq_size = width - 3
            try:
                if isinstance(gpu_freq.get('GPC'), list) and gpu_freq['GPC']:
                    size_gpc_gauge = (width - 2) // (2 + len(gpu_freq['GPC']))
                    for gpc_idx, gpc in enumerate(gpu_freq['GPC']):
                        freq_data = {
                            'name': 'GPC{idx}'.format(idx=gpc_idx),
                            'cur': max(0, int(gpc)),
                            'unit': 'k',
                            'online': int(gpc) > 0,
                        }
                        freq_gauge(self.stdscr,
                                   first + 1 + (idx + 1) * gpu_height,
                                   width // 2 + gpc_idx * (size_gpc_gauge) + 2,
                                   size_gpc_gauge - 1, freq_data)
                    frq_size = width // 2
            except Exception:
                # GPC yoksa/yetersizse görmezden gel
                pass

            # Overall frequency gauge (defansif)
            try:
                freq_gauge(self.stdscr, first + 1 + (idx + 1) * gpu_height, 1, frq_size, gpu_freq)
            except Exception:
                # Eksik anahtarlar varsa gauge çizimini atla
                pass

        # Draw all Processes
        height_table = height - first + 2 + gpu_height
        self.process_table.draw(first + 2 + gpu_height, 0, width, height_table, key, mouse)

# EOF
