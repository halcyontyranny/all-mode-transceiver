#!/usr/bin/env python3
"""
Apply post-GRC-save fixes to Multi-Mode-Transceiver.grc and HackRFMultiModeTransceiver.py.

Run this after any save from GNU Radio Companion. GRC Companion can strip blocks it
doesn't recognise during reformatting, and regenerates Python without them.

Three fixes are applied:

GRC file:
  1. Re-insert dc_blocker_cc_rx_0 block and its connections (IQ DC offset removal).
  2. Re-insert ptt_gate_tx_displays + blocks_null_sink_tx_disp and their connections
     (TX displays only active while PTT is pressed).

Python file:
  3. Insert dc_blocker_cc_rx_0 instantiation and rewire the RX connections through it.
     (PTT-gate wiring is generated correctly by GRC; only the cc dc_blocker needs patching.)
"""

import sys
from pathlib import Path

DIR = Path(__file__).parent
GRC_FILE = DIR / "Multi-Mode-Transceiver.grc"
PY_FILE  = DIR / "HackRFMultiModeTransceiver.py"

# ─── GRC fix 1: dc_blocker_cc_rx_0 block ─────────────────────────────────────

DC_BLOCKER_CC_BLOCK = """\
- name: dc_blocker_cc_rx_0
  id: dc_blocker_xx
  parameters:
    affinity: ''
    alias: ''
    comment: Remove HackRF IQ DC offset (eliminates center-frequency red line on waterfall)
    length: '32'
    long_form: 'True'
    maxoutbuf: '0'
    minoutbuf: '0'
    type: cc
  states:
    bus_sink: false
    bus_source: false
    bus_structure: null
    coordinate: [1640, 44.0]
    rotation: 0
    state: true
"""

GRC_DC_BLOCK_ANCHOR = "- name: snippet_0\n  id: snippet\n"

# ─── GRC fix 2: PTT-gate blocks ───────────────────────────────────────────────

PTT_GATE_BLOCKS = """\
- name: ptt_gate_tx_displays
  id: blocks_selector
  parameters:
    affinity: ''
    alias: ''
    comment: Pass TX signal to displays only while PTT is active
    enabled: 'True'
    input_index: '0'
    maxoutbuf: '0'
    minoutbuf: '0'
    num_inputs: '1'
    num_outputs: '2'
    output_index: ptt
    showports: 'True'
    type: complex
    vlen: '1'
  states:
    bus_sink: false
    bus_source: false
    bus_structure: null
    coordinate: [824, 100.0]
    rotation: 0
    state: true
- name: blocks_null_sink_tx_disp
  id: blocks_null_sink
  parameters:
    affinity: ''
    alias: ''
    bus_structure_sink: '[[0,],]'
    comment: Drain TX display path when PTT is off
    num_inputs: '1'
    type: complex
    vlen: '1'
  states:
    bus_sink: false
    bus_source: false
    bus_structure: null
    coordinate: [824, 180.0]
    rotation: 0
    state: true
"""

GRC_PTT_BLOCK_ANCHOR = "- name: snippet_0\n  id: snippet\n"

# ─── GRC connection fixes ─────────────────────────────────────────────────────

# dc_blocker RX path
GRC_OLD_RX_CONNS = """\
- [rational_resampler_xxx_rx_0, '0', analog_nbfm_rx_0, '0']
- [rational_resampler_xxx_rx_0, '0', fft_filter_xxx_rx_am, '0']
- [rational_resampler_xxx_rx_0, '0', fft_filter_xxx_rx_dsb, '0']
- [rational_resampler_xxx_rx_0, '0', fft_filter_xxx_rx_lsb, '0']
- [rational_resampler_xxx_rx_0, '0', fft_filter_xxx_rx_usb, '0']
- [rational_resampler_xxx_rx_0, '0', qtgui_waterfall_sink_x_1, '0']"""

GRC_NEW_RX_CONNS = """\
- [rational_resampler_xxx_rx_0, '0', dc_blocker_cc_rx_0, '0']
- [dc_blocker_cc_rx_0, '0', analog_nbfm_rx_0, '0']
- [dc_blocker_cc_rx_0, '0', fft_filter_xxx_rx_am, '0']
- [dc_blocker_cc_rx_0, '0', fft_filter_xxx_rx_dsb, '0']
- [dc_blocker_cc_rx_0, '0', fft_filter_xxx_rx_lsb, '0']
- [dc_blocker_cc_rx_0, '0', fft_filter_xxx_rx_usb, '0']
- [dc_blocker_cc_rx_0, '0', qtgui_waterfall_sink_x_1, '0']"""

# PTT-gate TX display path
GRC_OLD_TX_DISP_CONNS = """\
- [blocks_selector_0, '0', blocks_complex_to_float_0, '0']
- [blocks_selector_0, '0', qtgui_freq_sink_x_0, '0']
- [blocks_selector_0, '0', qtgui_waterfall_sink_x_0, '0']
- [blocks_selector_0, '0', rational_resampler_xxx_0_0_0_0, '0']"""

GRC_NEW_TX_DISP_CONNS = """\
- [blocks_selector_0, '0', ptt_gate_tx_displays, '0']
- [blocks_selector_0, '0', rational_resampler_xxx_0_0_0_0, '0']
- [ptt_gate_tx_displays, '0', blocks_null_sink_tx_disp, '0']
- [ptt_gate_tx_displays, '1', blocks_complex_to_float_0, '0']
- [ptt_gate_tx_displays, '1', qtgui_freq_sink_x_0, '0']
- [ptt_gate_tx_displays, '1', qtgui_waterfall_sink_x_0, '0']"""

# ─── Python file fixes ────────────────────────────────────────────────────────

PY_CC_BLOCKER_INST = "        self.dc_blocker_cc_rx_0 = filter.dc_blocker_cc(32, True)\n"
PY_FF_ANCHOR       = "self.dc_blocker_xx_rx_am = filter.dc_blocker_ff(32, True)"
PY_CC_MARKER       = "self.dc_blocker_cc_rx_0 = filter.dc_blocker_cc(32, True)"

PY_OLD_RX_CONNS = """\
        self.connect((self.rational_resampler_xxx_rx_0, 0), (self.analog_nbfm_rx_0, 0))
        self.connect((self.rational_resampler_xxx_rx_0, 0), (self.fft_filter_xxx_rx_am, 0))
        self.connect((self.rational_resampler_xxx_rx_0, 0), (self.fft_filter_xxx_rx_dsb, 0))
        self.connect((self.rational_resampler_xxx_rx_0, 0), (self.fft_filter_xxx_rx_lsb, 0))
        self.connect((self.rational_resampler_xxx_rx_0, 0), (self.fft_filter_xxx_rx_usb, 0))
        self.connect((self.rational_resampler_xxx_rx_0, 0), (self.qtgui_waterfall_sink_x_1, 0))"""

PY_NEW_RX_CONNS = """\
        self.connect((self.rational_resampler_xxx_rx_0, 0), (self.dc_blocker_cc_rx_0, 0))
        self.connect((self.dc_blocker_cc_rx_0, 0), (self.analog_nbfm_rx_0, 0))
        self.connect((self.dc_blocker_cc_rx_0, 0), (self.fft_filter_xxx_rx_am, 0))
        self.connect((self.dc_blocker_cc_rx_0, 0), (self.fft_filter_xxx_rx_dsb, 0))
        self.connect((self.dc_blocker_cc_rx_0, 0), (self.fft_filter_xxx_rx_lsb, 0))
        self.connect((self.dc_blocker_cc_rx_0, 0), (self.fft_filter_xxx_rx_usb, 0))
        self.connect((self.dc_blocker_cc_rx_0, 0), (self.qtgui_waterfall_sink_x_1, 0))"""

# PTT-gate TX display path (Python)
PY_PTT_GATE_INST_ANCHOR = "self.blocks_selector_tx_out = blocks.selector(gr.sizeof_gr_complex*1,wfm_active,0)\n        self.blocks_selector_tx_out.set_enabled(True)"
PY_PTT_GATE_INST_MARKER = "self.ptt_gate_tx_displays = blocks.selector"
PY_PTT_GATE_INST_NEW    = """\
        self.ptt_gate_tx_displays = blocks.selector(gr.sizeof_gr_complex*1,0,ptt)
        self.ptt_gate_tx_displays.set_enabled(True)
        self.blocks_null_sink_tx_disp = blocks.null_sink(gr.sizeof_gr_complex*1)"""

PY_OLD_TX_DISP_CONNS = """\
        self.connect((self.blocks_selector_0, 0), (self.blocks_complex_to_float_0, 0))
        self.connect((self.blocks_selector_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.blocks_selector_0, 0), (self.qtgui_waterfall_sink_x_0, 0))
        self.connect((self.blocks_selector_0, 0), (self.rational_resampler_xxx_0_0_0_0, 0))"""

PY_NEW_TX_DISP_CONNS = """\
        self.connect((self.blocks_selector_0, 0), (self.ptt_gate_tx_displays, 0))
        self.connect((self.blocks_selector_0, 0), (self.rational_resampler_xxx_0_0_0_0, 0))
        self.connect((self.ptt_gate_tx_displays, 0), (self.blocks_null_sink_tx_disp, 0))
        self.connect((self.ptt_gate_tx_displays, 1), (self.blocks_complex_to_float_0, 0))
        self.connect((self.ptt_gate_tx_displays, 1), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.ptt_gate_tx_displays, 1), (self.qtgui_waterfall_sink_x_0, 0))"""

PY_OLD_SET_PTT = """\
    def set_ptt(self, ptt):
        self.ptt = ptt
        self.osmosdr_transceiver_0.set_transmit(self.ptt)"""

PY_NEW_SET_PTT = """\
    def set_ptt(self, ptt):
        self.ptt = ptt
        self.osmosdr_transceiver_0.set_transmit(self.ptt)
        self.ptt_gate_tx_displays.set_output_index(int(self.ptt))"""


def fix_grc(text: str) -> tuple[str, list[str], list[str]]:
    applied, skipped = [], []

    # Block: dc_blocker_cc_rx_0
    if "name: dc_blocker_cc_rx_0" in text:
        skipped.append("GRC: dc_blocker_cc_rx_0 block (already present)")
    elif GRC_DC_BLOCK_ANCHOR in text:
        text = text.replace(GRC_DC_BLOCK_ANCHOR, DC_BLOCKER_CC_BLOCK + GRC_DC_BLOCK_ANCHOR)
        applied.append("GRC: inserted dc_blocker_cc_rx_0 block")
    else:
        skipped.append("GRC: dc_blocker_cc_rx_0 block (anchor not found)")

    # Block: ptt_gate_tx_displays + blocks_null_sink_tx_disp
    if "name: ptt_gate_tx_displays" in text:
        skipped.append("GRC: ptt_gate_tx_displays block (already present)")
    elif GRC_PTT_BLOCK_ANCHOR in text:
        text = text.replace(GRC_PTT_BLOCK_ANCHOR, PTT_GATE_BLOCKS + GRC_PTT_BLOCK_ANCHOR)
        applied.append("GRC: inserted ptt_gate_tx_displays + blocks_null_sink_tx_disp blocks")
    else:
        skipped.append("GRC: ptt_gate_tx_displays block (anchor not found)")

    # Connections: RX dc_blocker
    if GRC_NEW_RX_CONNS in text:
        skipped.append("GRC: RX dc_blocker connections (already applied)")
    elif GRC_OLD_RX_CONNS in text:
        text = text.replace(GRC_OLD_RX_CONNS, GRC_NEW_RX_CONNS)
        applied.append("GRC: rewired RX path through dc_blocker_cc_rx_0")
    else:
        skipped.append("GRC: RX dc_blocker connections (pattern not found)")

    # Connections: PTT-gate TX displays
    if GRC_NEW_TX_DISP_CONNS in text:
        skipped.append("GRC: PTT-gate TX display connections (already applied)")
    elif GRC_OLD_TX_DISP_CONNS in text:
        text = text.replace(GRC_OLD_TX_DISP_CONNS, GRC_NEW_TX_DISP_CONNS)
        applied.append("GRC: PTT-gated TX display connections")
    else:
        skipped.append("GRC: PTT-gate TX display connections (pattern not found)")

    return text, applied, skipped


def fix_py(text: str) -> tuple[str, list[str], list[str]]:
    applied, skipped = [], []

    # Instantiation
    if PY_CC_MARKER in text:
        skipped.append("PY: dc_blocker_cc_rx_0 instantiation (already present)")
    elif PY_FF_ANCHOR in text:
        text = text.replace(
            f"        {PY_FF_ANCHOR}\n",
            f"        {PY_FF_ANCHOR}\n{PY_CC_BLOCKER_INST}",
        )
        applied.append("PY: inserted dc_blocker_cc_rx_0 instantiation")
    else:
        skipped.append(f"PY: dc_blocker_cc_rx_0 instantiation (anchor not found)")

    # RX dc_blocker connections
    if PY_NEW_RX_CONNS in text:
        skipped.append("PY: RX dc_blocker connections (already applied)")
    elif PY_OLD_RX_CONNS in text:
        text = text.replace(PY_OLD_RX_CONNS, PY_NEW_RX_CONNS)
        applied.append("PY: rewired RX path through dc_blocker_cc_rx_0")
    else:
        skipped.append("PY: RX connections (pattern not found — layout may differ)")

    # PTT-gate instantiation
    if PY_PTT_GATE_INST_MARKER in text:
        skipped.append("PY: ptt_gate_tx_displays instantiation (already present)")
    elif PY_PTT_GATE_INST_ANCHOR in text:
        text = text.replace(
            PY_PTT_GATE_INST_ANCHOR,
            PY_PTT_GATE_INST_ANCHOR + "\n" + PY_PTT_GATE_INST_NEW,
        )
        applied.append("PY: inserted ptt_gate_tx_displays + blocks_null_sink_tx_disp instantiation")
    else:
        skipped.append("PY: ptt_gate_tx_displays instantiation (anchor not found)")

    # PTT-gate TX display connections
    if PY_NEW_TX_DISP_CONNS in text:
        skipped.append("PY: PTT-gate TX display connections (already applied)")
    elif PY_OLD_TX_DISP_CONNS in text:
        text = text.replace(PY_OLD_TX_DISP_CONNS, PY_NEW_TX_DISP_CONNS)
        applied.append("PY: PTT-gated TX display connections")
    else:
        skipped.append("PY: PTT-gate TX display connections (pattern not found)")

    # set_ptt callback — wire set_output_index
    if "ptt_gate_tx_displays.set_output_index" in text:
        skipped.append("PY: set_ptt callback (already updated)")
    elif PY_OLD_SET_PTT in text:
        text = text.replace(PY_OLD_SET_PTT, PY_NEW_SET_PTT)
        applied.append("PY: added ptt_gate_tx_displays.set_output_index to set_ptt")
    else:
        skipped.append("PY: set_ptt callback (pattern not found)")

    return text, applied, skipped


def process(path: Path, fixer) -> bool:
    if not path.exists():
        print(f"  MISSING  {path.name}")
        return False
    original = path.read_text()
    patched, applied, skipped = fixer(original)
    changed = patched != original
    if changed:
        path.write_text(patched)
    for msg in applied:
        print(f"  APPLIED  {msg}")
    for msg in skipped:
        print(f"  SKIPPED  {msg}")
    return changed


def main():
    grc_changed = process(GRC_FILE, fix_grc)
    py_changed  = process(PY_FILE,  fix_py)
    if grc_changed or py_changed:
        print(f"\nFiles updated. Commit when ready.")
    else:
        print("\nNothing to do — both files already patched.")


if __name__ == "__main__":
    main()
