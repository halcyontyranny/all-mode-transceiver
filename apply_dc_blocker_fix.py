#!/usr/bin/env python3
"""
Apply the HackRF IQ DC-offset fix to HackRF_Siggen.py after GRC regeneration.

Two changes are made:
  1. Insert  dc_blocker_cc_rx_0  instantiation right after dc_blocker_xx_rx_am.
  2. Route the narrow-band RX path through dc_blocker_cc_rx_0 instead of
     fanning out directly from the 8M→48k resampler.
"""

import re
import sys
from pathlib import Path

TARGET = Path(__file__).parent / "HackRF_Siggen.py"

# ── change 1: add cc blocker instantiation ───────────────────────────────────
CC_BLOCKER_INST = "        self.dc_blocker_cc_rx_0 = filter.dc_blocker_cc(32, True)\n"

# ── change 2: rewired connections ────────────────────────────────────────────
OLD_CONNS = """\
        self.connect((self.rational_resampler_xxx_rx_0, 0), (self.analog_nbfm_rx_0, 0))
        self.connect((self.rational_resampler_xxx_rx_0, 0), (self.fft_filter_xxx_rx_am, 0))
        self.connect((self.rational_resampler_xxx_rx_0, 0), (self.fft_filter_xxx_rx_dsb, 0))
        self.connect((self.rational_resampler_xxx_rx_0, 0), (self.fft_filter_xxx_rx_lsb, 0))
        self.connect((self.rational_resampler_xxx_rx_0, 0), (self.fft_filter_xxx_rx_usb, 0))
        self.connect((self.rational_resampler_xxx_rx_0, 0), (self.qtgui_waterfall_sink_x_1, 0))"""

NEW_CONNS = """\
        self.connect((self.rational_resampler_xxx_rx_0, 0), (self.dc_blocker_cc_rx_0, 0))
        self.connect((self.dc_blocker_cc_rx_0, 0), (self.analog_nbfm_rx_0, 0))
        self.connect((self.dc_blocker_cc_rx_0, 0), (self.fft_filter_xxx_rx_am, 0))
        self.connect((self.dc_blocker_cc_rx_0, 0), (self.fft_filter_xxx_rx_dsb, 0))
        self.connect((self.dc_blocker_cc_rx_0, 0), (self.fft_filter_xxx_rx_lsb, 0))
        self.connect((self.dc_blocker_cc_rx_0, 0), (self.fft_filter_xxx_rx_usb, 0))
        self.connect((self.dc_blocker_cc_rx_0, 0), (self.qtgui_waterfall_sink_x_1, 0))"""


def apply(text: str) -> tuple[str, list[str]]:
    applied = []
    skipped = []

    # ── change 1 ─────────────────────────────────────────────────────────────
    marker = "self.dc_blocker_xx_rx_am = filter.dc_blocker_ff(32, True)"
    cc_marker = "self.dc_blocker_cc_rx_0 = filter.dc_blocker_cc(32, True)"
    if cc_marker in text:
        skipped.append("cc blocker instantiation (already present)")
    elif marker in text:
        text = text.replace(
            f"        {marker}\n",
            f"        {marker}\n{CC_BLOCKER_INST}",
        )
        applied.append("inserted dc_blocker_cc_rx_0 instantiation")
    else:
        skipped.append(f"cc blocker instantiation (anchor '{marker}' not found)")

    # ── change 2 ─────────────────────────────────────────────────────────────
    if NEW_CONNS in text:
        skipped.append("connection rewire (already applied)")
    elif OLD_CONNS in text:
        text = text.replace(OLD_CONNS, NEW_CONNS)
        applied.append("rewired RX path through dc_blocker_cc_rx_0")
    else:
        skipped.append("connection rewire (old pattern not found — regenerated layout may differ)")

    return text, applied, skipped


def main():
    if not TARGET.exists():
        sys.exit(f"ERROR: {TARGET} not found")

    original = TARGET.read_text()
    patched, applied, skipped = apply(original)

    if applied:
        TARGET.write_text(patched)
        for msg in applied:
            print(f"  APPLIED  {msg}")
    if skipped:
        for msg in skipped:
            print(f"  SKIPPED  {msg}")

    if not applied and not skipped:
        print("Nothing to do.")
    elif not applied:
        print("\nNo changes written.")
    else:
        print(f"\nWrote {TARGET}")


if __name__ == "__main__":
    main()
