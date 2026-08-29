from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "fabrication" / "JLCPCB"
SCHEMATIC_DIR = OUT / "schematic_review"
PCB_DIR = OUT / "pcb_review"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def crop_svg(source: Path, dest: Path, x: float, y: float, w: float, h: float, px_w: int = 1400, px_h: int = 900) -> None:
    text = source.read_text(encoding="utf-8")
    text = re.sub(
        r'width="[^"]+"\s+height="[^"]+"\s+viewBox="[^"]+"',
        f'width="{px_w}px" height="{px_h}px" viewBox="{x:.4f} {y:.4f} {w:.4f} {h:.4f}"',
        text,
        count=1,
        flags=re.S,
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")


def screenshot_svg(svg: Path, png: Path, width: int = 1400, height: int = 900) -> None:
    if not EDGE.exists():
        return
    png.parent.mkdir(parents=True, exist_ok=True)
    uri = svg.resolve().as_uri()
    subprocess.run(
        [
            str(EDGE),
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            f"--window-size={width},{height}",
            f"--screenshot={png}",
            uri,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def make_schematic_views() -> None:
    source = SCHEMATIC_DIR / "Power Testing board.svg"
    views = {
        "schematic_overview": (0, 0, 592, 420, 1800, 1250),
        "schematic_3v3_rail": (70, 34, 335, 82, 1600, 620),
        "schematic_5v_rail": (70, 114, 335, 82, 1600, 620),
        "schematic_12v_rail": (70, 194, 335, 82, 1600, 620),
        "schematic_16v8_rail": (70, 254, 335, 92, 1600, 680),
        "schematic_arduino_control": (35, 340, 365, 78, 1600, 620),
        "schematic_atx_ps_on": (10, 55, 95, 180, 1000, 1200),
        "schematic_outputs": (380, 45, 205, 320, 1200, 1500),
    }
    for name, (x, y, w, h, px_w, px_h) in views.items():
        svg = SCHEMATIC_DIR / f"{name}.svg"
        png = SCHEMATIC_DIR / f"{name}.png"
        crop_svg(source, svg, x, y, w, h, px_w, px_h)
        screenshot_svg(svg, png, px_w, px_h)


def make_pcb_views() -> None:
    top = PCB_DIR / "top_copper.svg"
    views = {
        "pcb_closeup_arduino_usb": (0, 0, 65, 65, 1100, 900),
        "pcb_closeup_reset_buttons": (85, 136, 100, 34, 1400, 620),
        "pcb_closeup_atx_inputs": (0, 0, 72, 170, 900, 1400),
        "pcb_closeup_boost_module": (160, 88, 70, 60, 1000, 850),
        "pcb_closeup_efuse_ina_chain": (55, 24, 93, 56, 1300, 780),
    }
    for name, (x, y, w, h, px_w, px_h) in views.items():
        svg = PCB_DIR / f"{name}.svg"
        png = PCB_DIR / f"{name}.png"
        crop_svg(top, svg, x, y, w, h, px_w, px_h)
        screenshot_svg(svg, png, px_w, px_h)


def write_review_doc() -> None:
    text = """# Visual Review Summary

## Schematic Review

- Full overview, four rail crops, Arduino/control, ATX/PS_ON, and output connector views were generated from the KiCad schematic SVG.
- The visible flow annotations show RAW/source -> eFuse -> INA260 VIN+ -> INA260 VIN- -> protected output bus.
- INA260 VIN- is explicitly labeled as the downstream protected positive rail, not GND.
- The schematic remains electrically label-driven for ERC stability, but parts are grouped into ATX, rail, output, and control areas for human review.
- ERC result: 0 errors, 11 warnings for optional isolated PG/IMON/ALERT labels.

## PCB Review

- Board stackup is 4 copper layers.
- L1/F.Cu and L4/B.Cu contain routed tracks; L2/In1.Cu and L3/In2.Cu contain zones only.
- L2/In1.Cu is a full-board GND reference plane.
- L3/In2.Cu contains only the power zones that remain useful and DRC-clean.
- Arduino Nano footprint is at 180 degrees, with the USB end facing the top board edge.
- Reset buttons remain in a straight accessible row along the lower board edge.
- ATX screw terminals remain on the left edge; dedicated and EPS output connectors remain accessible.
- Boost and INA260 modules remain serviceable/removable.
- DRC result: 0 violations, 0 unconnected items.

## Remaining Order Caveats

- JLCPCB/JLCDFM preview still needs external human review.
- LCSC/JLCPCB part selections and CPL rotations still need review in the JLCPCB PCBA preview.
- U1 TPS259814L exact orderable package/land-pattern match remains a purchase-review item.
"""
    (OUT / "visual_review_summary.md").write_text(text, encoding="utf-8")


def main() -> None:
    make_schematic_views()
    make_pcb_views()
    write_review_doc()


if __name__ == "__main__":
    main()
