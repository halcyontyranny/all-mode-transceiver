#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Multimode Transceiver by KF0UXU
# Author: Chris Mack - KF0UXU
# Description: Multimode Signal Generator / Receiver
# GNU Radio version: 3.10.1.1

from packaging.version import Version as StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import eng_notation
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore
import osmosdr



from gnuradio import qtgui

class HackRF_Siggen(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Multimode Transceiver by KF0UXU", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Multimode Transceiver by KF0UXU")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "HackRF_Siggen")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.side_band_width = side_band_width = 3000.0
        self.samp_rate = samp_rate = 48000
        self.mod = mod = 4
        self.wfm_active = wfm_active = 1 if mod == 5 else 0
        self.wavefile = wavefile = '/home/halcyon/Downloads/gc.wav'
        self.tone = tone = 1000
        self.rx_volume = rx_volume = 1.0
        self.rx_if_gain = rx_if_gain = 24
        self.rx_bb_gain = rx_bb_gain = 16
        self.ptt = ptt = 0
        self.pl_level = pl_level = 0.130
        self.pl_freq = pl_freq = 141.3
        self.output_lvl = output_lvl = 24
        self.output_amp = output_amp = 0
        self.mic_gain = mic_gain = 1.0
        self.mc = mc = 0
        self.freq_correction = freq_correction = 0
        self.freq = freq = 75
        self.USB_band_pass_filter_taps = USB_band_pass_filter_taps = firdes.complex_band_pass(2.0, samp_rate, 150, side_band_width, 75, window.WIN_HAMMING, 6.76)
        self.LSB_band_pass_filter_taps = LSB_band_pass_filter_taps = firdes.complex_band_pass(2.0, samp_rate, -side_band_width, -150, 75, window.WIN_HAMMING, 6.76)
        self.FM_band_pass_filter_taps = FM_band_pass_filter_taps = firdes.complex_band_pass(1.0, samp_rate, -10000, 10000, 500, window.WIN_HAMMING, 6.76)
        self.DSB_band_pass_filter_taps = DSB_band_pass_filter_taps = firdes.complex_band_pass(1, samp_rate, -3200, 3200, 200, window.WIN_HAMMING, 6.76)
        self.AM_band_pass_filter_taps = AM_band_pass_filter_taps = firdes.complex_band_pass(0.5, samp_rate, -3200, 3200, 200, window.WIN_HAMMING, 6.76)

        ##################################################
        # Blocks
        ##################################################
        self._wavefile_tool_bar = Qt.QToolBar(self)
        self._wavefile_tool_bar.addWidget(Qt.QLabel("Wavefile" + ": "))
        self._wavefile_line_edit = Qt.QLineEdit(str(self.wavefile))
        self._wavefile_tool_bar.addWidget(self._wavefile_line_edit)
        self._wavefile_line_edit.returnPressed.connect(
            lambda: self.set_wavefile(str(str(self._wavefile_line_edit.text()))))
        self.top_grid_layout.addWidget(self._wavefile_tool_bar, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._tone_tool_bar = Qt.QToolBar(self)
        self._tone_tool_bar.addWidget(Qt.QLabel("Tone(Hz)" + ": "))
        self._tone_line_edit = Qt.QLineEdit(str(self.tone))
        self._tone_tool_bar.addWidget(self._tone_line_edit)
        self._tone_line_edit.returnPressed.connect(
            lambda: self.set_tone(int(str(self._tone_line_edit.text()))))
        self.top_grid_layout.addWidget(self._tone_tool_bar, 1, 2, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._rx_volume_range = Range(0, 2.0, 0.05, 1.0, 100)
        self._rx_volume_win = RangeWidget(self._rx_volume_range, self.set_rx_volume, "RX Volume", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._rx_volume_win, 5, 2, 1, 1)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._rx_if_gain_range = Range(0, 40, 8, 24, 100)
        self._rx_if_gain_win = RangeWidget(self._rx_if_gain_range, self.set_rx_if_gain, "RX IF Gain (dB)", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._rx_if_gain_win, 5, 0, 1, 1)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._rx_bb_gain_range = Range(0, 62, 2, 16, 100)
        self._rx_bb_gain_win = RangeWidget(self._rx_bb_gain_range, self.set_rx_bb_gain, "RX BB Gain (dB)", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._rx_bb_gain_win, 5, 1, 1, 1)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        _ptt_push_button = Qt.QPushButton('Push To Talk')
        _ptt_push_button = Qt.QPushButton('Push To Talk')
        self._ptt_choices = {'Pressed': 1, 'Released': 0}
        _ptt_push_button.pressed.connect(lambda: self.set_ptt(self._ptt_choices['Pressed']))
        _ptt_push_button.released.connect(lambda: self.set_ptt(self._ptt_choices['Released']))
        self.top_layout.addWidget(_ptt_push_button)
        # Create the options list
        self._pl_freq_options = [67.0, 71.9, 74.4, 77.0, 79.7, 82.5, 85.4, 88.5, 91.5, 94.8, 97.4, 100.0, 103.5, 107.2, 110.9, 114.8, 118.8, 123.0, 127.3, 131.8, 136.5, 141.3, 146.2, 151.4, 156.7, 162.2, 167.9, 173.8, 179.9, 186.2, 192.8, 203.5, 210.7, 218.1, 225.7, 233.6, 241.8, 250.3]
        # Create the labels list
        self._pl_freq_labels = ['67.0', '71.9', '74.4', '77.0', '79.7', '82.5', '85.4', '88.5', '91.5', '94.8', '97.4', '100.0', '103.5', '107.2', '110.9', '114.8', '118.8', '123.0', '127.3', '131.8', '136.5', '141.3', '146.2', '151.4', '156.7', '162.2', '167.9', '173.8', '179.9', '186.2', '192.8', '203.5', '210.7', '218.1', '225.7', '233.6', '241.8', '250.3']
        # Create the combo box
        self._pl_freq_tool_bar = Qt.QToolBar(self)
        self._pl_freq_tool_bar.addWidget(Qt.QLabel("PL Tone" + ": "))
        self._pl_freq_combo_box = Qt.QComboBox()
        self._pl_freq_tool_bar.addWidget(self._pl_freq_combo_box)
        for _label in self._pl_freq_labels: self._pl_freq_combo_box.addItem(_label)
        self._pl_freq_callback = lambda i: Qt.QMetaObject.invokeMethod(self._pl_freq_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._pl_freq_options.index(i)))
        self._pl_freq_callback(self.pl_freq)
        self._pl_freq_combo_box.currentIndexChanged.connect(
            lambda i: self.set_pl_freq(self._pl_freq_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._pl_freq_tool_bar, 2, 2, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._output_lvl_range = Range(0, 47, 1, 24, 100)
        self._output_lvl_win = RangeWidget(self._output_lvl_range, self.set_output_lvl, "Output Level", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._output_lvl_win, 3, 0, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        if int == bool:
        	self._output_amp_choices = {'Pressed': bool(14), 'Released': bool(0)}
        elif int == str:
        	self._output_amp_choices = {'Pressed': "14".replace("'",""), 'Released': "0".replace("'","")}
        else:
        	self._output_amp_choices = {'Pressed': 14, 'Released': 0}

        _output_amp_toggle_button = qtgui.ToggleButton(self.set_output_amp, 'HackRF Base Amp', self._output_amp_choices, False,"'value'".replace("'",""))
        _output_amp_toggle_button.setColors("red","green","green","default")
        self.output_amp = _output_amp_toggle_button

        self.top_grid_layout.addWidget(_output_amp_toggle_button, 2, 1, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._mod_options = [0, 1, 2, 3, 4, 5]
        # Create the labels list
        self._mod_labels = ['LSB', 'USB', 'DSB', 'AM', 'FM5K', 'WFM']
        # Create the combo box
        # Create the radio buttons
        self._mod_group_box = Qt.QGroupBox("Modulation Type" + ": ")
        self._mod_box = Qt.QHBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._mod_button_group = variable_chooser_button_group()
        self._mod_group_box.setLayout(self._mod_box)
        for i, _label in enumerate(self._mod_labels):
            radio_button = Qt.QRadioButton(_label)
            self._mod_box.addWidget(radio_button)
            self._mod_button_group.addButton(radio_button, i)
        self._mod_callback = lambda i: Qt.QMetaObject.invokeMethod(self._mod_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._mod_options.index(i)))
        self._mod_callback(self.mod)
        self._mod_button_group.buttonClicked[int].connect(
            lambda i: self.set_mod(self._mod_options[i]))
        self.top_grid_layout.addWidget(self._mod_group_box, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._mic_gain_range = Range(0.0, 1, 0.1, 1.0, 100)
        self._mic_gain_win = RangeWidget(self._mic_gain_range, self.set_mic_gain, "Mic Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._mic_gain_win, 0, 2, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._mc_options = [0, 1, 2, 3, 4, 5, 6]
        # Create the labels list
        self._mc_labels = ['WaveFile', 'WaveFile + PL Tone', 'Tone', 'Tone + PL Tone', 'Mic', 'Mic + PL Tone', 'None']
        # Create the combo box
        self._mc_tool_bar = Qt.QToolBar(self)
        self._mc_tool_bar.addWidget(Qt.QLabel("Mod Content" + ": "))
        self._mc_combo_box = Qt.QComboBox()
        self._mc_tool_bar.addWidget(self._mc_combo_box)
        for _label in self._mc_labels: self._mc_combo_box.addItem(_label)
        self._mc_callback = lambda i: Qt.QMetaObject.invokeMethod(self._mc_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._mc_options.index(i)))
        self._mc_callback(self.mc)
        self._mc_combo_box.currentIndexChanged.connect(
            lambda i: self.set_mc(self._mc_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._mc_tool_bar, 2, 0, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._freq_correction_range = Range(-100, 100, 1, 0, 200)
        self._freq_correction_win = RangeWidget(self._freq_correction_range, self.set_freq_correction, "Frequency Correction (PPM)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._freq_correction_win, 3, 1, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._freq_tool_bar = Qt.QToolBar(self)
        self._freq_tool_bar.addWidget(Qt.QLabel("Frequency(MHz)" + ": "))
        self._freq_line_edit = Qt.QLineEdit(str(self.freq))
        self._freq_tool_bar.addWidget(self._freq_line_edit)
        self._freq_line_edit.returnPressed.connect(
            lambda: self.set_freq(eng_notation.str_to_num(str(self._freq_line_edit.text()))))
        self.top_grid_layout.addWidget(self._freq_tool_bar, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._side_band_width_options = [300.0, 400.0, 600.0, 850.0, 1100.0, 1200.0, 1500.0, 1650.0, 1800.0, 1950.0, 2100.0, 2250.0, 2400.0, 2450.0, 2500.0, 2600.0, 2700.0, 2800.0, 2900.0, 3000.0, 3200.0, 3500.0, 4000.0]
        # Create the labels list
        self._side_band_width_labels = ['300 Hz', '400 Hz', '600 Hz', '850 Hz', '1100 Hz', '1200 Hz', '1500 Hz', '1650 Hz', '1800 Hz', '1950 Hz', '2100 Hz', '2250 Hz', '2400 Hz', '2450 Hz', '2500 Hz', '2600 Hz', '2700 Hz', '2800 Hz', '2900 Hz', '3000 Hz', '3200 Hz', '3500 Hz', '4000 Hz']
        # Create the combo box
        self._side_band_width_tool_bar = Qt.QToolBar(self)
        self._side_band_width_tool_bar.addWidget(Qt.QLabel("Side Band Width" + ": "))
        self._side_band_width_combo_box = Qt.QComboBox()
        self._side_band_width_tool_bar.addWidget(self._side_band_width_combo_box)
        for _label in self._side_band_width_labels: self._side_band_width_combo_box.addItem(_label)
        self._side_band_width_callback = lambda i: Qt.QMetaObject.invokeMethod(self._side_band_width_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._side_band_width_options.index(i)))
        self._side_band_width_callback(self.side_band_width)
        self._side_band_width_combo_box.currentIndexChanged.connect(
            lambda i: self.set_side_band_width(self._side_band_width_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._side_band_width_tool_bar, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.rational_resampler_xxx_rx_0 = filter.rational_resampler_ccf(
                interpolation=3,
                decimation=500,
                taps=[],
                fractional_bw=4e-3)
        self.rational_resampler_xxx_0_0_0_0 = filter.rational_resampler_ccf(
                interpolation=500,
                decimation=3,
                taps=[],
                fractional_bw=4e-3)
        self.rational_resampler_wfm_tx_0 = filter.rational_resampler_ccf(
                interpolation=50,
                decimation=3,
                taps=[],
                fractional_bw=4e-3)
        self.rational_resampler_wfm_rx_0 = filter.rational_resampler_ccf(
                interpolation=6,
                decimation=100,
                taps=[],
                fractional_bw=4e-3)
        self.qtgui_waterfall_sink_x_1 = qtgui.waterfall_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq*1e6, #fc
            samp_rate, #bw
            'RX Waterfall', #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_waterfall_sink_x_1.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_1.enable_grid(False)
        self.qtgui_waterfall_sink_x_1.enable_axis_labels(True)



        labels = ['RX Waterfall', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_1.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_1.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_1.set_intensity_range(-140, 10)

        self._qtgui_waterfall_sink_x_1_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_1.qwidget(), Qt.QWidget)

        self.top_layout.addWidget(self._qtgui_waterfall_sink_x_1_win)
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_c(
            16384, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq*1e6, #fc
            samp_rate, #bw
            'TX Waterfall', #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_0.enable_grid(False)
        self.qtgui_waterfall_sink_x_0.enable_axis_labels(True)



        labels = ['TX Waterfall', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_0.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_0.set_intensity_range(-140, 10)

        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.qwidget(), Qt.QWidget)

        self.top_grid_layout.addWidget(self._qtgui_waterfall_sink_x_0_win, 4, 2, 1, 1)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            16384, #size
            samp_rate, #samp_rate
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-2, 2)

        self.qtgui_time_sink_x_0.set_y_label('TX IQ Drive Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(True)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)

        self.qtgui_time_sink_x_0.disable_legend()

        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win, 4, 0, 1, 1)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            16384, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate/1, #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-200, 0)
        self.qtgui_freq_sink_x_0.set_y_label('TX Drive Spectrum', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(0.2)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(True)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)

        self.qtgui_freq_sink_x_0.disable_legend()


        labels = ['IF Spectrum', '', '', '', '',
            '', '', '', '', '']
        widths = [2, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 4, 1, 1, 1)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.osmosdr_transceiver_0 = osmosdr.transceiver("hackrf=0")
        self.osmosdr_transceiver_0.set_sample_rate(8000000)
        self.osmosdr_transceiver_0.set_center_freq(freq * 1e6, 0)
        self.osmosdr_transceiver_0.set_freq_corr(freq_correction, 0)
        self.osmosdr_transceiver_0.set_gain(output_amp, 0)
        self.osmosdr_transceiver_0.set_if_gain(rx_if_gain, 0)
        self.osmosdr_transceiver_0.set_bb_gain(rx_bb_gain, 0)
        self.osmosdr_transceiver_0.set_tx_gain(output_lvl, 0)
        self.osmosdr_transceiver_0.set_bandwidth(0, 0)
        self.osmosdr_transceiver_0.set_transmit(ptt)
        self.fft_filter_xxx_rx_usb = filter.fft_filter_ccc(1, USB_band_pass_filter_taps, 1)
        self.fft_filter_xxx_rx_usb.declare_sample_delay(0)
        self.fft_filter_xxx_rx_lsb = filter.fft_filter_ccc(1, LSB_band_pass_filter_taps, 1)
        self.fft_filter_xxx_rx_lsb.declare_sample_delay(0)
        self.fft_filter_xxx_rx_dsb = filter.fft_filter_ccc(1, DSB_band_pass_filter_taps, 1)
        self.fft_filter_xxx_rx_dsb.declare_sample_delay(0)
        self.fft_filter_xxx_rx_am = filter.fft_filter_ccc(1, AM_band_pass_filter_taps, 1)
        self.fft_filter_xxx_rx_am.declare_sample_delay(0)
        self.fft_filter_xxx_0_0_0_0_0 = filter.fft_filter_ccc(1, FM_band_pass_filter_taps, 1)
        self.fft_filter_xxx_0_0_0_0_0.declare_sample_delay(0)
        self.fft_filter_xxx_0_0_0_0 = filter.fft_filter_ccc(1, AM_band_pass_filter_taps, 1)
        self.fft_filter_xxx_0_0_0_0.declare_sample_delay(0)
        self.fft_filter_xxx_0_0_0 = filter.fft_filter_ccc(1, DSB_band_pass_filter_taps, 1)
        self.fft_filter_xxx_0_0_0.declare_sample_delay(0)
        self.fft_filter_xxx_0_0 = filter.fft_filter_ccc(1, USB_band_pass_filter_taps, 1)
        self.fft_filter_xxx_0_0.declare_sample_delay(0)
        self.fft_filter_xxx_0 = filter.fft_filter_ccc(1, LSB_band_pass_filter_taps, 1)
        self.fft_filter_xxx_0.declare_sample_delay(0)
        self.dc_blocker_xx_rx_am = filter.dc_blocker_ff(32, True)
        self.dc_blocker_cc_rx_0 = filter.dc_blocker_cc(32, True)
        self.blocks_wavfile_source_0 = blocks.wavfile_source(wavefile, True)
        self.blocks_selector_tx_out = blocks.selector(gr.sizeof_gr_complex*1,wfm_active,0)
        self.blocks_selector_tx_out.set_enabled(True)
        self.blocks_selector_rx = blocks.selector(gr.sizeof_float*1,mod,0)
        self.blocks_selector_rx.set_enabled(True)
        self.blocks_selector_0_1 = blocks.selector(gr.sizeof_float*1,mc,0)
        self.blocks_selector_0_1.set_enabled(True)
        self.blocks_selector_0_0 = blocks.selector(gr.sizeof_float*1,mod,0)
        self.blocks_selector_0_0.set_enabled(True)
        self.blocks_selector_0 = blocks.selector(gr.sizeof_gr_complex*1,mod,0)
        self.blocks_selector_0.set_enabled(True)
        self.blocks_null_source_wfm = blocks.null_source(gr.sizeof_gr_complex*1)
        self.blocks_null_source_0 = blocks.null_source(gr.sizeof_float*1)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_multiply_const_vxx_rx_vol = blocks.multiply_const_ff(rx_volume)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_ff(mic_gain)
        self.blocks_multiply_const_vxx_0_0_1 = blocks.multiply_const_ff(1.0/(1.0+pl_level))
        self.blocks_multiply_const_vxx_0_0_0 = blocks.multiply_const_ff(1.0/(1.0+pl_level))
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_ff(1.0/(1.0+pl_level))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(mic_gain)
        self.blocks_message_debug_0 = blocks.message_debug(True)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_complex_to_real_rx_usb = blocks.complex_to_real(1)
        self.blocks_complex_to_real_rx_lsb = blocks.complex_to_real(1)
        self.blocks_complex_to_real_rx_dsb = blocks.complex_to_real(1)
        self.blocks_complex_to_mag_rx_am = blocks.complex_to_mag(1)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.blocks_add_xx_1 = blocks.add_vff(1)
        self.blocks_add_xx_0_1 = blocks.add_vff(1)
        self.blocks_add_xx_0_0 = blocks.add_vff(1)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.audio_source_0 = audio.source(samp_rate, 'pulse', True)
        self.audio_sink_0 = audio.sink(samp_rate, 'pulse', False)
        self.analog_wfm_tx_0 = analog.wfm_tx(
        	audio_rate=samp_rate,
        	quad_rate=480000,
        	tau=75e-6,
        	max_dev=75e3,
        	fh=-1.0,
        )
        self.analog_wfm_rcv_0 = analog.wfm_rcv(
        	quad_rate=480000,
        	audio_decimation=10,
        )
        self.analog_sig_source_x_1_0 = analog.sig_source_f(samp_rate, analog.GR_COS_WAVE, pl_freq, pl_level, 0, 0)
        self.analog_sig_source_x_1 = analog.sig_source_f(samp_rate, analog.GR_COS_WAVE, tone, mic_gain, 0, 0)
        self.analog_nbfm_tx_0 = analog.nbfm_tx(
        	audio_rate=samp_rate,
        	quad_rate=samp_rate,
        	tau=75e-6,
        	max_dev=5e3,
        	fh=-1,
                )
        self.analog_nbfm_rx_0 = analog.nbfm_rx(
        	audio_rate=samp_rate,
        	quad_rate=samp_rate,
        	tau=75e-6,
        	max_dev=5e3,
          )
        self.analog_const_source_x_0_0_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 1.0)
        self.analog_const_source_x_0_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 0)
        self.analog_const_source_x_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.analog_const_source_x_0_0, 0), (self.blocks_selector_0_0, 1))
        self.connect((self.analog_const_source_x_0_0, 0), (self.blocks_selector_0_0, 2))
        self.connect((self.analog_const_source_x_0_0, 0), (self.blocks_selector_0_0, 5))
        self.connect((self.analog_const_source_x_0_0, 0), (self.blocks_selector_0_0, 0))
        self.connect((self.analog_const_source_x_0_0, 0), (self.blocks_selector_0_0, 4))
        self.connect((self.analog_const_source_x_0_0_0, 0), (self.blocks_selector_0_0, 3))
        self.connect((self.analog_nbfm_rx_0, 0), (self.blocks_selector_rx, 4))
        self.connect((self.analog_nbfm_tx_0, 0), (self.fft_filter_xxx_0_0_0_0_0, 0))
        self.connect((self.analog_sig_source_x_1, 0), (self.blocks_multiply_const_vxx_0_0_0, 0))
        self.connect((self.analog_sig_source_x_1, 0), (self.blocks_selector_0_1, 2))
        self.connect((self.analog_sig_source_x_1_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.analog_sig_source_x_1_0, 0), (self.blocks_add_xx_0_0, 0))
        self.connect((self.analog_sig_source_x_1_0, 0), (self.blocks_add_xx_1, 0))
        self.connect((self.analog_wfm_rcv_0, 0), (self.blocks_selector_rx, 5))
        self.connect((self.analog_wfm_tx_0, 0), (self.rational_resampler_wfm_tx_0, 0))
        self.connect((self.audio_source_0, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_selector_0_1, 1))
        self.connect((self.blocks_add_xx_0_0, 0), (self.blocks_selector_0_1, 3))
        self.connect((self.blocks_add_xx_0_1, 0), (self.blocks_float_to_complex_0, 1))
        self.connect((self.blocks_add_xx_1, 0), (self.blocks_selector_0_1, 5))
        self.connect((self.blocks_complex_to_float_0, 1), (self.blocks_null_sink_0, 0))
        self.connect((self.blocks_complex_to_float_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_complex_to_mag_rx_am, 0), (self.dc_blocker_xx_rx_am, 0))
        self.connect((self.blocks_complex_to_real_rx_dsb, 0), (self.blocks_selector_rx, 2))
        self.connect((self.blocks_complex_to_real_rx_lsb, 0), (self.blocks_selector_rx, 0))
        self.connect((self.blocks_complex_to_real_rx_usb, 0), (self.blocks_selector_rx, 1))
        self.connect((self.blocks_float_to_complex_0, 0), (self.fft_filter_xxx_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.fft_filter_xxx_0_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.fft_filter_xxx_0_0_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.fft_filter_xxx_0_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_selector_0_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_0, 0), (self.blocks_add_xx_0_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0_0_1, 0), (self.blocks_add_xx_1, 1))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.blocks_multiply_const_vxx_0_0_1, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.blocks_selector_0_1, 4))
        self.connect((self.blocks_multiply_const_vxx_rx_vol, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_null_source_0, 0), (self.blocks_selector_0_1, 6))
        self.connect((self.blocks_null_source_wfm, 0), (self.blocks_selector_0, 5))
        self.connect((self.blocks_selector_0, 0), (self.blocks_complex_to_float_0, 0))
        self.connect((self.blocks_selector_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.blocks_selector_0, 0), (self.qtgui_waterfall_sink_x_0, 0))
        self.connect((self.blocks_selector_0, 0), (self.rational_resampler_xxx_0_0_0_0, 0))
        self.connect((self.blocks_selector_0_0, 0), (self.blocks_add_xx_0_1, 0))
        self.connect((self.blocks_selector_0_1, 0), (self.analog_nbfm_tx_0, 0))
        self.connect((self.blocks_selector_0_1, 0), (self.analog_wfm_tx_0, 0))
        self.connect((self.blocks_selector_0_1, 0), (self.blocks_add_xx_0_1, 1))
        self.connect((self.blocks_selector_rx, 0), (self.blocks_multiply_const_vxx_rx_vol, 0))
        self.connect((self.blocks_selector_tx_out, 0), (self.osmosdr_transceiver_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.dc_blocker_xx_rx_am, 0), (self.blocks_selector_rx, 3))
        self.connect((self.fft_filter_xxx_0, 0), (self.blocks_selector_0, 0))
        self.connect((self.fft_filter_xxx_0_0, 0), (self.blocks_selector_0, 1))
        self.connect((self.fft_filter_xxx_0_0_0, 0), (self.blocks_selector_0, 2))
        self.connect((self.fft_filter_xxx_0_0_0_0, 0), (self.blocks_selector_0, 3))
        self.connect((self.fft_filter_xxx_0_0_0_0_0, 0), (self.blocks_selector_0, 4))
        self.connect((self.fft_filter_xxx_rx_am, 0), (self.blocks_complex_to_mag_rx_am, 0))
        self.connect((self.fft_filter_xxx_rx_dsb, 0), (self.blocks_complex_to_real_rx_dsb, 0))
        self.connect((self.fft_filter_xxx_rx_lsb, 0), (self.blocks_complex_to_real_rx_lsb, 0))
        self.connect((self.fft_filter_xxx_rx_usb, 0), (self.blocks_complex_to_real_rx_usb, 0))
        self.connect((self.osmosdr_transceiver_0, 0), (self.rational_resampler_wfm_rx_0, 0))
        self.connect((self.osmosdr_transceiver_0, 0), (self.rational_resampler_xxx_rx_0, 0))
        self.connect((self.rational_resampler_wfm_rx_0, 0), (self.analog_wfm_rcv_0, 0))
        self.connect((self.rational_resampler_wfm_tx_0, 0), (self.blocks_selector_tx_out, 1))
        self.connect((self.rational_resampler_xxx_0_0_0_0, 0), (self.blocks_selector_tx_out, 0))
        self.connect((self.rational_resampler_xxx_rx_0, 0), (self.dc_blocker_cc_rx_0, 0))
        self.connect((self.dc_blocker_cc_rx_0, 0), (self.analog_nbfm_rx_0, 0))
        self.connect((self.dc_blocker_cc_rx_0, 0), (self.fft_filter_xxx_rx_am, 0))
        self.connect((self.dc_blocker_cc_rx_0, 0), (self.fft_filter_xxx_rx_dsb, 0))
        self.connect((self.dc_blocker_cc_rx_0, 0), (self.fft_filter_xxx_rx_lsb, 0))
        self.connect((self.dc_blocker_cc_rx_0, 0), (self.fft_filter_xxx_rx_usb, 0))
        self.connect((self.dc_blocker_cc_rx_0, 0), (self.qtgui_waterfall_sink_x_1, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "HackRF_Siggen")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_side_band_width(self):
        return self.side_band_width

    def set_side_band_width(self, side_band_width):
        self.side_band_width = side_band_width
        self.set_LSB_band_pass_filter_taps(firdes.complex_band_pass(2.0, self.samp_rate, -self.side_band_width, -150, 75, window.WIN_HAMMING, 6.76))
        self.set_USB_band_pass_filter_taps(firdes.complex_band_pass(2.0, self.samp_rate, 150, self.side_band_width, 75, window.WIN_HAMMING, 6.76))
        self._side_band_width_callback(self.side_band_width)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_AM_band_pass_filter_taps(firdes.complex_band_pass(0.5, self.samp_rate, -3200, 3200, 200, window.WIN_HAMMING, 6.76))
        self.set_DSB_band_pass_filter_taps(firdes.complex_band_pass(1, self.samp_rate, -3200, 3200, 200, window.WIN_HAMMING, 6.76))
        self.set_FM_band_pass_filter_taps(firdes.complex_band_pass(1.0, self.samp_rate, -10000, 10000, 500, window.WIN_HAMMING, 6.76))
        self.set_LSB_band_pass_filter_taps(firdes.complex_band_pass(2.0, self.samp_rate, -self.side_band_width, -150, 75, window.WIN_HAMMING, 6.76))
        self.set_USB_band_pass_filter_taps(firdes.complex_band_pass(2.0, self.samp_rate, 150, self.side_band_width, 75, window.WIN_HAMMING, 6.76))
        self.analog_sig_source_x_1.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_1_0.set_sampling_freq(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate/1)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(self.freq*1e6, self.samp_rate)
        self.qtgui_waterfall_sink_x_1.set_frequency_range(self.freq*1e6, self.samp_rate)

    def get_mod(self):
        return self.mod

    def set_mod(self, mod):
        self.mod = mod
        self._mod_callback(self.mod)
        self.set_wfm_active(1 if self.mod == 5 else 0)
        self.blocks_selector_0.set_input_index(self.mod)
        self.blocks_selector_0_0.set_input_index(self.mod)
        self.blocks_selector_rx.set_input_index(self.mod)

    def get_wfm_active(self):
        return self.wfm_active

    def set_wfm_active(self, wfm_active):
        self.wfm_active = wfm_active
        self.blocks_selector_tx_out.set_input_index(self.wfm_active)

    def get_wavefile(self):
        return self.wavefile

    def set_wavefile(self, wavefile):
        self.wavefile = wavefile
        Qt.QMetaObject.invokeMethod(self._wavefile_line_edit, "setText", Qt.Q_ARG("QString", str(self.wavefile)))

    def get_tone(self):
        return self.tone

    def set_tone(self, tone):
        self.tone = tone
        Qt.QMetaObject.invokeMethod(self._tone_line_edit, "setText", Qt.Q_ARG("QString", str(self.tone)))
        self.analog_sig_source_x_1.set_frequency(self.tone)

    def get_rx_volume(self):
        return self.rx_volume

    def set_rx_volume(self, rx_volume):
        self.rx_volume = rx_volume
        self.blocks_multiply_const_vxx_rx_vol.set_k(self.rx_volume)

    def get_rx_if_gain(self):
        return self.rx_if_gain

    def set_rx_if_gain(self, rx_if_gain):
        self.rx_if_gain = rx_if_gain
        self.osmosdr_transceiver_0.set_if_gain(self.rx_if_gain, 0)

    def get_rx_bb_gain(self):
        return self.rx_bb_gain

    def set_rx_bb_gain(self, rx_bb_gain):
        self.rx_bb_gain = rx_bb_gain
        self.osmosdr_transceiver_0.set_bb_gain(self.rx_bb_gain, 0)

    def get_ptt(self):
        return self.ptt

    def set_ptt(self, ptt):
        self.ptt = ptt
        self.osmosdr_transceiver_0.set_transmit(self.ptt)

    def get_pl_level(self):
        return self.pl_level

    def set_pl_level(self, pl_level):
        self.pl_level = pl_level
        self.analog_sig_source_x_1_0.set_amplitude(self.pl_level)
        self.blocks_multiply_const_vxx_0_0.set_k(1.0/(1.0+self.pl_level))
        self.blocks_multiply_const_vxx_0_0_0.set_k(1.0/(1.0+self.pl_level))
        self.blocks_multiply_const_vxx_0_0_1.set_k(1.0/(1.0+self.pl_level))

    def get_pl_freq(self):
        return self.pl_freq

    def set_pl_freq(self, pl_freq):
        self.pl_freq = pl_freq
        self._pl_freq_callback(self.pl_freq)
        self.analog_sig_source_x_1_0.set_frequency(self.pl_freq)

    def get_output_lvl(self):
        return self.output_lvl

    def set_output_lvl(self, output_lvl):
        self.output_lvl = output_lvl
        self.osmosdr_transceiver_0.set_tx_gain(self.output_lvl, 0)

    def get_output_amp(self):
        return self.output_amp

    def set_output_amp(self, output_amp):
        self.output_amp = output_amp
        self.osmosdr_transceiver_0.set_gain(self.output_amp, 0)

    def get_mic_gain(self):
        return self.mic_gain

    def set_mic_gain(self, mic_gain):
        self.mic_gain = mic_gain
        self.analog_sig_source_x_1.set_amplitude(self.mic_gain)
        self.blocks_multiply_const_vxx_0.set_k(self.mic_gain)
        self.blocks_multiply_const_vxx_1.set_k(self.mic_gain)

    def get_mc(self):
        return self.mc

    def set_mc(self, mc):
        self.mc = mc
        self._mc_callback(self.mc)
        self.blocks_selector_0_1.set_input_index(self.mc)

    def get_freq_correction(self):
        return self.freq_correction

    def set_freq_correction(self, freq_correction):
        self.freq_correction = freq_correction
        self.osmosdr_transceiver_0.set_freq_corr(self.freq_correction, 0)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        Qt.QMetaObject.invokeMethod(self._freq_line_edit, "setText", Qt.Q_ARG("QString", eng_notation.num_to_str(self.freq)))
        self.osmosdr_transceiver_0.set_center_freq(self.freq * 1e6, 0)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(self.freq*1e6, self.samp_rate)
        self.qtgui_waterfall_sink_x_1.set_frequency_range(self.freq*1e6, self.samp_rate)

    def get_USB_band_pass_filter_taps(self):
        return self.USB_band_pass_filter_taps

    def set_USB_band_pass_filter_taps(self, USB_band_pass_filter_taps):
        self.USB_band_pass_filter_taps = USB_band_pass_filter_taps
        self.fft_filter_xxx_0_0.set_taps(self.USB_band_pass_filter_taps)
        self.fft_filter_xxx_rx_usb.set_taps(self.USB_band_pass_filter_taps)

    def get_LSB_band_pass_filter_taps(self):
        return self.LSB_band_pass_filter_taps

    def set_LSB_band_pass_filter_taps(self, LSB_band_pass_filter_taps):
        self.LSB_band_pass_filter_taps = LSB_band_pass_filter_taps
        self.fft_filter_xxx_0.set_taps(self.LSB_band_pass_filter_taps)
        self.fft_filter_xxx_rx_lsb.set_taps(self.LSB_band_pass_filter_taps)

    def get_FM_band_pass_filter_taps(self):
        return self.FM_band_pass_filter_taps

    def set_FM_band_pass_filter_taps(self, FM_band_pass_filter_taps):
        self.FM_band_pass_filter_taps = FM_band_pass_filter_taps
        self.fft_filter_xxx_0_0_0_0_0.set_taps(self.FM_band_pass_filter_taps)

    def get_DSB_band_pass_filter_taps(self):
        return self.DSB_band_pass_filter_taps

    def set_DSB_band_pass_filter_taps(self, DSB_band_pass_filter_taps):
        self.DSB_band_pass_filter_taps = DSB_band_pass_filter_taps
        self.fft_filter_xxx_0_0_0.set_taps(self.DSB_band_pass_filter_taps)
        self.fft_filter_xxx_rx_dsb.set_taps(self.DSB_band_pass_filter_taps)

    def get_AM_band_pass_filter_taps(self):
        return self.AM_band_pass_filter_taps

    def set_AM_band_pass_filter_taps(self, AM_band_pass_filter_taps):
        self.AM_band_pass_filter_taps = AM_band_pass_filter_taps
        self.fft_filter_xxx_0_0_0_0.set_taps(self.AM_band_pass_filter_taps)
        self.fft_filter_xxx_rx_am.set_taps(self.AM_band_pass_filter_taps)




def main(top_block_cls=HackRF_Siggen, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
