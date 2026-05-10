from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import math
import os
import shutil
import subprocess
import uuid


ROOT = Path(__file__).resolve().parents[1]
PROJECT = "Power Testing board"
SCH = ROOT / f"{PROJECT}.kicad_sch"
PCB = ROOT / f"{PROJECT}.kicad_pcb"
PRO = ROOT / f"{PROJECT}.kicad_pro"
SYM_LIB = ROOT / "Power_Testing_Board.kicad_sym"
FP_LIB = ROOT / "Power_Testing_Board.pretty"
KICAD_SHARE = Path(r"C:\Program Files\KiCad\10.0\share\kicad")


def u() -> str:
    return str(uuid.uuid4())


@dataclass
class Pin:
    number: str
    name: str
    x: float
    y: float
    angle: int
    etype: str = "passive"


@dataclass
class SymbolDef:
    name: str
    prefix: str
    pins: list[Pin]
    footprint: str = ""
    datasheet: str = "~"
    description: str = ""
    w: float = 12.7
    h: float = 12.7


@dataclass
class Component:
    ref: str
    symbol: str
    value: str
    footprint: str
    x: float
    y: float
    pin_nets: dict[str, str] = field(default_factory=dict)
    rot: float = 0.0
    on_board: bool = True


SYMBOLS: dict[str, SymbolDef] = {}
COMPONENTS: list[Component] = []


def add_symbol(sym: SymbolDef) -> None:
    SYMBOLS[sym.name] = sym


def sx(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def fmt(n: float) -> str:
    return f"{n:.4f}".rstrip("0").rstrip(".")


def symbol_text(sym: SymbolDef, embedded: bool = False) -> str:
    symbol_name = f"Power_Testing_Board:{sym.name}" if embedded else sym.name
    x1 = -sym.w / 2
    x2 = sym.w / 2
    y1 = sym.h / 2
    y2 = -sym.h / 2
    lines = [
        f'  (symbol "{sx(symbol_name)}"',
        "    (exclude_from_sim no)",
        "    (in_bom yes)",
        "    (on_board yes)",
        '    (property "Reference" "{}" (at 0 {} 0) (effects (font (size 1.27 1.27))))'.format(
            sym.prefix, fmt(y1 + 2.54)
        ),
        '    (property "Value" "{}" (at 0 {} 0) (effects (font (size 1.27 1.27))))'.format(
            sx(sym.name), fmt(y2 - 2.54)
        ),
        '    (property "Footprint" "{}" (at 0 {} 0) (effects (font (size 1.27 1.27)) hide))'.format(
            sx(sym.footprint), fmt(y2 - 5.08)
        ),
        '    (property "Datasheet" "{}" (at 0 {} 0) (effects (font (size 1.27 1.27)) hide))'.format(
            sx(sym.datasheet), fmt(y2 - 7.62)
        ),
        '    (property "Description" "{}" (at 0 {} 0) (effects (font (size 1.27 1.27)) hide))'.format(
            sx(sym.description), fmt(y2 - 10.16)
        ),
        f'    (symbol "{sx(sym.name)}_0_1"',
        f"      (rectangle (start {fmt(x1)} {fmt(y1)}) (end {fmt(x2)} {fmt(y2)}) (stroke (width 0.254) (type default)) (fill (type background)))",
        "    )",
        f'    (symbol "{sx(sym.name)}_1_1"',
    ]
    for p in sym.pins:
        lines += [
            f"      (pin {p.etype} line",
            f"        (at {fmt(p.x)} {fmt(p.y)} {p.angle})",
            "        (length 2.54)",
            f'        (name "{sx(p.name)}" (effects (font (size 1.0 1.0))))',
            f'        (number "{sx(p.number)}" (effects (font (size 1.0 1.0))))',
            "      )",
        ]
    lines += ["    )", "  )"]
    return "\n".join(lines)


def make_symbols() -> None:
    # Small generic symbols use left/right pins to make generated labels precise and readable.
    add_symbol(SymbolDef("R", "R", [Pin("1", "1", -3.81, 0, 0), Pin("2", "2", 3.81, 0, 180)], "Resistor_SMD:R_0603_1608Metric", "~", "Generic resistor", 4, 2.8))
    add_symbol(SymbolDef("C", "C", [Pin("1", "1", -3.81, 0, 0), Pin("2", "2", 3.81, 0, 180)], "Capacitor_SMD:C_0805_2012Metric", "~", "Generic capacitor", 4, 2.8))
    add_symbol(SymbolDef("TP", "TP", [Pin("1", "TP", -3.81, 0, 0)], "TestPoint:TestPoint_Pad_D1.0mm", "~", "Compact one-pad test point", 3, 2.8))
    add_symbol(SymbolDef("SW_Push", "SW", [Pin("1", "1", -3.81, 0, 0), Pin("2", "2", 3.81, 0, 180)], "Button_Switch_THT:SW_PUSH_6mm", "~", "Momentary reset button", 5, 4))
    add_symbol(SymbolDef("NMOS_GSD", "Q", [Pin("1", "G", -5.08, 0, 0), Pin("2", "S", 5.08, -2.54, 180), Pin("3", "D", 5.08, 2.54, 180)], "Package_TO_SOT_SMD:SOT-23", "~", "2N7002 open-drain pulldown", 5, 6))

    for n in (2, 4, 8, 10):
        pins = [Pin(str(i), f"Pin_{i}", -5.08, (n - 1) * 1.27 - (i - 1) * 2.54, 0) for i in range(1, n + 1)]
        add_symbol(SymbolDef(f"Conn_01x{n:02d}", "J", pins, "", "~", f"Generic {n}-pin connector", 5, max(5, n * 2.54)))

    arduino_pins = [
        Pin("1", "D1/TX", -12.7, 15.24, 0),
        Pin("2", "D0/RX", -12.7, 12.7, 0),
        Pin("4", "GND", -12.7, 10.16, 0),
        Pin("5", "D2", -12.7, 7.62, 0),
        Pin("6", "D3", -12.7, 5.08, 0),
        Pin("7", "D4", -12.7, 2.54, 0),
        Pin("8", "D5", -12.7, 0, 0),
        Pin("9", "D6", -12.7, -2.54, 0),
        Pin("10", "D7", -12.7, -5.08, 0),
        Pin("11", "D8", -12.7, -7.62, 0),
        Pin("12", "D9", -12.7, -10.16, 0),
        Pin("13", "D10", -12.7, -12.7, 0),
        Pin("14", "D11", -12.7, -15.24, 0),
        Pin("23", "A4/SDA", 12.7, -5.08, 180),
        Pin("24", "A5/SCL", 12.7, -7.62, 180),
        Pin("27", "5V", 12.7, 7.62, 180),
        Pin("29", "GND", 12.7, 5.08, 180),
    ]
    add_symbol(SymbolDef("Arduino_Nano_USB_Powered", "A", arduino_pins, "Module:Arduino_Nano", "https://docs.arduino.cc/hardware/nano/", "Socketed Arduino Nano, powered by USB", 20, 36))

    ina_pins = [
        Pin("7", "VIN+", -10.16, 5.08, 0),
        Pin("8", "VIN-", 10.16, 5.08, 180),
        Pin("1", "VCC", -10.16, -2.54, 0),
        Pin("2", "GND", -10.16, -5.08, 0),
        Pin("3", "SCL", 10.16, -2.54, 180),
        Pin("4", "SDA", 10.16, -5.08, 180),
        Pin("5", "ALERT", 10.16, -7.62, 180),
        Pin("6", "VBUS_NC", 10.16, -10.16, 180),
    ]
    add_symbol(SymbolDef("Adafruit_INA260_4226_Module", "U", ina_pins, "Power_Testing_Board:Adafruit_INA260_4226_Module", "https://www.adafruit.com/product/4226", "Adafruit INA260 Product 4226 breakout module", 15, 22))

    tps266 = [
        Pin("1", "IN", -12.7, 15.24, 0),
        Pin("2", "IN", -12.7, 12.7, 0),
        Pin("5", "IN_SYS", -12.7, 10.16, 0),
        Pin("6", "UVLO", -12.7, 5.08, 0),
        Pin("7", "OVP", -12.7, 2.54, 0),
        Pin("10", "ILIM", -12.7, 0, 0),
        Pin("12", "~SHDN", -12.7, -5.08, 0),
        Pin("11", "MODE_OPEN", -12.7, -10.16, 0),
        Pin("8", "GND", -12.7, -15.24, 0),
        Pin("25", "EP_GND", -12.7, -17.78, 0),
        Pin("17", "OUT", 12.7, 15.24, 180),
        Pin("18", "OUT", 12.7, 12.7, 180),
        Pin("14", "~FLT", 12.7, 5.08, 180),
        Pin("16", "PGOOD", 12.7, 2.54, 180),
        Pin("15", "PGTH", 12.7, 0, 180),
        Pin("13", "IMON", 12.7, -2.54, 180),
        Pin("9", "dVdT_OPEN", 12.7, -7.62, 180),
        Pin("3", "B_GATE_OPEN", 12.7, -12.7, 180),
        Pin("4", "DRV_OPEN", 12.7, -15.24, 180),
    ]
    add_symbol(SymbolDef("TPS26631RGE_eFuse", "U", tps266, "Package_DFN_QFN:Texas_RGE0024H_VQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm_ThermalVias", "https://www.ti.com/lit/gpn/tps2663", "TPS26631RGE 60 V, 6 A eFuse", 20, 38))

    tps259 = [
        Pin("1", "EN/UVLO", -10.16, 10.16, 0),
        Pin("2", "EN/OVLO", -10.16, 7.62, 0),
        Pin("5", "IN", -10.16, 2.54, 0),
        Pin("8", "GND", -10.16, -5.08, 0),
        Pin("9", "ILM", -10.16, -7.62, 0),
        Pin("6", "OUT", 10.16, 2.54, 180),
        Pin("3", "PG", 10.16, 7.62, 180),
        Pin("4", "~FLT", 10.16, 5.08, 180),
        Pin("7", "DVDT_OPEN", 10.16, -5.08, 180),
        Pin("10", "ITIMER_OPEN", 10.16, -7.62, 180),
    ]
    add_symbol(SymbolDef("TPS259814L_RPW_eFuse", "U", tps259, "Package_DFN_QFN:Texas_RPU0010A_VQFN-HR-10_2x2mm_P0.5mm", "https://www.ti.com/lit/gpn/tps25981", "TPS259814L latch-off eFuse; RPW land pattern must be verified", 16, 24))

    boost = [
        Pin("1", "IN-", -10.16, 7.62, 0),
        Pin("2", "IN+", -10.16, 2.54, 0),
        Pin("3", "OUT-", 10.16, 7.62, 180),
        Pin("4", "OUT+", 10.16, 2.54, 180),
        Pin("5", "SW1_OPT", 10.16, -5.08, 180),
        Pin("6", "SW2_OPT", 10.16, -7.62, 180),
    ]
    add_symbol(SymbolDef("Boost_Module_60x42", "U", boost, "Power_Testing_Board:Boost_Module_60x42_VERIFIED", "~", "Amazon boost converter module, 60 mm x 42 mm x 20 mm; footprint physically verified", 16, 20))

    h1_pins = []
    h1_selected = [22, 24, 27, 31, 32, 36, 39, 40, 42, 47, 48, 49, 52]
    for i, pin in enumerate(h1_selected):
        side = -12.7 if i % 2 == 0 else 12.7
        angle = 0 if side < 0 else 180
        y = 15.24 - (i // 2) * 2.54
        h1_pins.append(Pin(str(pin), f"H1_{pin}", side, y, angle))
    add_symbol(SymbolDef("PC104_H1_SelectedPowerPins", "J", h1_pins, "Connector_PinSocket_2.54mm:PinSocket_2x26_P2.54mm_Vertical", "~", "PC/104 H1 selected mission power/GND pins only", 20, 36))

    h2_pins = []
    h2_selected = [25, 26, 27, 28, 29, 30, 31, 32, 36, 39, 40, 41, 42, 43, 44, 45, 46]
    for i, pin in enumerate(h2_selected):
        side = -12.7 if i % 2 == 0 else 12.7
        angle = 0 if side < 0 else 180
        y = 20.32 - (i // 2) * 2.54
        h2_pins.append(Pin(str(pin), f"H2_{pin}", side, y, angle))
    add_symbol(SymbolDef("PC104_H2_SelectedPowerPins", "J", h2_pins, "Connector_PinSocket_2.54mm:PinSocket_2x26_P2.54mm_Vertical", "~", "PC/104 H2 selected mission power/GND pins only", 20, 46))


def add(ref: str, symbol: str, value: str, footprint: str, x: float, y: float, pin_nets: dict[str, str], rot: float = 0.0, on_board: bool = True) -> None:
    # Keep generated schematic pins and wire endpoints on KiCad's 1.27 mm connection grid.
    x = round(x / 1.27) * 1.27
    y = round(y / 1.27) * 1.27
    COMPONENTS.append(Component(ref, symbol, value, footprint, x, y, {str(k): v for k, v in pin_nets.items()}, rot, on_board))


def add_res(ref: str, value: str, a: str, b: str, x: float, y: float, fp: str = "Resistor_SMD:R_0603_1608Metric") -> None:
    add(ref, "R", value, fp, x, y, {"1": a, "2": b})


def add_cap(ref: str, value: str, a: str, b: str, x: float, y: float) -> None:
    add(ref, "C", value, "Capacitor_SMD:C_0805_2012Metric", x, y, {"1": a, "2": b})


def add_tp(ref: str, net: str, x: float, y: float, label: str | None = None) -> None:
    add(ref, "TP", label or net, "TestPoint:TestPoint_Pad_D1.0mm", x, y, {"1": net})


def make_components() -> None:
    add("A1", "Arduino_Nano_USB_Powered", "Arduino Nano USB-powered socket", "Module:Arduino_Nano", 30, 38, {
        "4": "GND", "29": "GND", "27": "+ARDUINO_5V",
        "23": "I2C_SDA", "24": "I2C_SCL",
        "5": "ARD_RESET_3V3", "6": "ARD_RESET_5V", "7": "ARD_RESET_12V", "8": "ARD_RESET_16V8",
        "9": "FLT_3V3", "10": "FLT_5V", "11": "FLT_12V", "12": "FLT_16V8",
        "13": "ATX_PS_ON_CTL", "14": "ATX_PWR_OK",
    }, rot=90)

    add("J1", "Conn_01x10", "J_ATX_PWR: 3V3 3V3 5V 5V 12V 12V GNDx4", "TerminalBlock:TerminalBlock_MaiXu_MX126-5.0-10P_1x10_P5.00mm", 18, 75, {
        "1": "+3V3_RAW", "2": "+3V3_RAW", "3": "+5V_RAW", "4": "+5V_RAW", "5": "+12V_RAW", "6": "+12V_RAW",
        "7": "GND", "8": "GND", "9": "GND", "10": "GND",
    }, rot=90)
    add("J2", "Conn_01x04", "J_ATX_CTRL: PS_ON PWR_OK 5VSB GND", "TerminalBlock:TerminalBlock_MaiXu_MX126-5.0-04P_1x04_P5.00mm", 18, 130, {
        "1": "ATX_PS_ON_N", "2": "ATX_PWR_OK", "3": "+5VSB", "4": "GND",
    }, rot=90)
    add("J3", "Conn_01x02", "ATX_SWITCH", "TerminalBlock:TerminalBlock_MaiXu_MX126-5.0-02P_1x02_P5.00mm", 18, 154, {
        "1": "ATX_PS_ON_N", "2": "GND",
    }, rot=90)
    add("J4", "Conn_01x08", "DEDICATED OUTPUTS: 3V3/G 5V/G 12V/G 16V8/G", "TerminalBlock:TerminalBlock_MaiXu_MX126-5.0-08P_1x08_P5.00mm", 250, 120, {
        "1": "+3V3_PROTECTED", "2": "GND", "3": "+5V_PROTECTED", "4": "GND",
        "5": "+12V_PROTECTED", "6": "GND", "7": "+16V8_PROTECTED", "8": "GND",
    }, rot=90)

    add("U9", "Boost_Module_60x42", "Boost 12V to 16.8V module 60x42 VERIFIED", "Power_Testing_Board:Boost_Module_60x42_VERIFIED", 58, 270, {
        "1": "GND", "2": "+12V_RAW", "3": "GND", "4": "+16V8_RAW",
    })

    rails = [
        ("3V3", "U1", "TPS259814L_RPW_eFuse", "+3V3_RAW", "+3V3_EFUSE_OUT", "+3V3_PROTECTED", "RESET_3V3", "ARD_RESET_3V3", "FLT_3V3", 68, 62),
        ("5V", "U2", "TPS26631RGE_eFuse", "+5V_RAW", "+5V_EFUSE_OUT", "+5V_PROTECTED", "RESET_5V", "ARD_RESET_5V", "FLT_5V", 68, 122),
        ("12V", "U3", "TPS26631RGE_eFuse", "+12V_RAW", "+12V_EFUSE_OUT", "+12V_PROTECTED", "RESET_12V", "ARD_RESET_12V", "FLT_12V", 68, 182),
        ("16V8", "U4", "TPS26631RGE_eFuse", "+16V8_RAW", "+16V8_EFUSE_OUT", "+16V8_PROTECTED", "RESET_16V8", "ARD_RESET_16V8", "FLT_16V8", 68, 242),
    ]

    rnum = 1
    cnum = 1
    qnum = 1
    sw_num = 1
    for idx, (name, uref, sym, raw, efout, prot, reset, ard_reset, flt, x, y) in enumerate(rails):
        if sym == "TPS259814L_RPW_eFuse":
            add(uref, sym, f"TPS259814L {name} eFuse latch-off", "Package_DFN_QFN:Texas_RPU0010A_VQFN-HR-10_2x2mm_P0.5mm", x, y, {
                "1": reset, "2": f"OVLO_{name}", "5": raw, "8": "GND", "9": f"ILIM_{name}",
                "6": efout, "3": f"PG_{name}", "4": flt,
            })
            add_res(f"R{rnum}", "1.10k 1% ILM ~6A", f"ILIM_{name}", "GND", x - 14, y + 19, "Resistor_SMD:R_0805_2012Metric"); rnum += 1
            add_res(f"R{rnum}", "100k 1% EN top 2.40V", raw, reset, x - 20, y - 14); rnum += 1
            add_res(f"R{rnum}", "100k 1% EN bottom", reset, "GND", x - 7, y - 14); rnum += 1
            add_res(f"R{rnum}", "24.9k 1% OVLO top 4.19V", raw, f"OVLO_{name}", x + 9, y - 14); rnum += 1
            add_res(f"R{rnum}", "10k 1% OVLO bottom", f"OVLO_{name}", "GND", x + 22, y - 14); rnum += 1
        else:
            add(uref, sym, f"TPS26631RGE {name} eFuse", "Package_DFN_QFN:Texas_RGE0024H_VQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm_ThermalVias", x, y, {
                "1": raw, "2": raw, "5": raw, "6": f"UVLO_{name}", "7": f"OVP_{name}", "8": "GND", "10": f"ILIM_{name}", "12": reset, "25": "GND",
                "17": efout, "18": efout, "14": flt, "16": f"PG_{name}", "13": f"IMON_{name}",
            })
            add_res(f"R{rnum}", "3.00k 1% ILIM ~6A", f"ILIM_{name}", "GND", x - 14, y + 22, "Resistor_SMD:R_0805_2012Metric"); rnum += 1
            # TPS26631 UVLO/OVP dividers use the 1.20 V typical rising threshold.
            # Threshold = 1.20 V * (Rtop + Rbottom) / Rbottom.
            vals = {
                "5V": ("261k 1% UVLO top 4.33V", "100k 1% UVLO bottom", "383k 1% OVP top 5.80V", "100k 1% OVP bottom"),
                "12V": ("806k 1% UVLO top 10.87V", "100k 1% UVLO bottom", "1.05M 1% OVP top 13.80V", "100k 1% OVP bottom"),
                "16V8": ("1.07M 1% UVLO top 14.04V", "100k 1% UVLO bottom", "1.40M 1% OVP top 18.00V", "100k 1% OVP bottom"),
            }[name]
            add_res(f"R{rnum}", vals[0], raw, f"UVLO_{name}", x - 23, y - 23); rnum += 1
            add_res(f"R{rnum}", vals[1], f"UVLO_{name}", "GND", x - 7, y - 23); rnum += 1
            add_res(f"R{rnum}", vals[2], raw, f"OVP_{name}", x + 9, y - 23); rnum += 1
            add_res(f"R{rnum}", vals[3], f"OVP_{name}", "GND", x + 25, y - 23); rnum += 1

        vin_rating = "25V" if name in {"3V3", "5V"} else "50V"
        add_cap(f"C{cnum}", f"1uF {vin_rating} X7R input close to eFuse", raw, "GND", x - 22, y + 14); cnum += 1
        add_cap(f"C{cnum}", f"10uF {vin_rating} X7R output close to eFuse", efout, "GND", x + 22, y + 14); cnum += 1

        add(f"U{5 + idx}", "Adafruit_INA260_4226_Module", f"INA260 {name} module", "Power_Testing_Board:Adafruit_INA260_4226_Module", x + 58, y, {
            "7": efout, "8": prot, "1": "+ARDUINO_5V", "2": "GND", "3": "I2C_SCL", "4": "I2C_SDA", "5": f"ALERT_{name}",
        })

        add(f"SW{sw_num}", "SW_Push", f"{reset} edge button", "Button_Switch_THT:SW_PUSH_6mm", 190 + (sw_num - 1) * 18, 282, {"1": reset, "2": "GND"}); sw_num += 1
        add(f"Q{qnum}", "NMOS_GSD", f"2N7002 {reset} pulldown", "Package_TO_SOT_SMD:SOT-23", 182 + (qnum - 1) * 18, 270, {"1": f"GATE_{name}", "2": "GND", "3": reset}); qnum += 1
        add_res(f"R{rnum}", "330 gate", ard_reset, f"GATE_{name}", 180 + (idx * 18), 260); rnum += 1
        add_res(f"R{rnum}", "100k gate pulldown", f"GATE_{name}", "GND", 180 + (idx * 18), 265); rnum += 1
        add_res(f"R{rnum}", "10k FLT pullup", flt, "+ARDUINO_5V", 170, 55 + idx * 18); rnum += 1

    add("Q5", "NMOS_GSD", "2N7002 ATX PS_ON# pulldown", "Package_TO_SOT_SMD:SOT-23", 34, 246, {"1": "GATE_PS_ON", "2": "GND", "3": "ATX_PS_ON_N"})
    add_res(f"R{rnum}", "330 gate", "ATX_PS_ON_CTL", "GATE_PS_ON", 34, 236); rnum += 1
    add_res(f"R{rnum}", "100k gate pulldown", "GATE_PS_ON", "GND", 34, 241); rnum += 1

    add("JH1", "PC104_H1_SelectedPowerPins", "H1 selected power/GND pins only", "Connector_PinSocket_2.54mm:PinSocket_2x26_P2.54mm_Vertical", 250, 70, {
        **{str(p): "GND" for p in [22, 24, 27, 31, 32, 36, 39, 40, 42]},
        "47": "+5V_PROTECTED", "49": "+5V_PROTECTED", "48": "+3V3_PROTECTED", "52": "+12V_PROTECTED",
    })
    add("JH2", "PC104_H2_SelectedPowerPins", "H2 selected power/GND pins only", "Connector_PinSocket_2.54mm:PinSocket_2x26_P2.54mm_Vertical", 250, 168, {
        "25": "+5V_PROTECTED", "26": "+5V_PROTECTED", "27": "+3V3_PROTECTED", "28": "+3V3_PROTECTED",
        **{str(p): "GND" for p in [29, 30, 31, 32, 36, 39, 40, 41, 42, 43, 44]},
        "45": "+16V8_PROTECTED", "46": "+16V8_PROTECTED",
    })

    tp_nets = [
        "+3V3_RAW", "+3V3_EFUSE_OUT", "+3V3_PROTECTED",
        "+5V_RAW", "+5V_EFUSE_OUT", "+5V_PROTECTED",
        "+12V_RAW", "+12V_EFUSE_OUT", "+12V_PROTECTED",
        "+16V8_RAW", "+16V8_EFUSE_OUT", "+16V8_PROTECTED",
        "GND", "I2C_SDA", "I2C_SCL", "ATX_PS_ON_N", "ATX_PWR_OK", "+5VSB",
        "RESET_3V3", "RESET_5V", "RESET_12V", "RESET_16V8",
        "FLT_3V3", "FLT_5V", "FLT_12V", "FLT_16V8",
    ]
    for i, net in enumerate(tp_nets, start=1):
        add_tp(f"TP{i}", net, 218 + (i % 2) * 14, 25 + (i // 2) * 4)
    add_tp("TP27", "+12V_RAW", 218, 83, "BOOST_IN+ (+12V_RAW)")
    add_tp("TP28", "+16V8_RAW", 232, 83, "BOOST_OUT+ (+16V8_RAW)")
    add_tp("TP29", "GND", 218, 87, "BOOST_GND")


def write_symbol_library() -> None:
    body = "\n".join(symbol_text(sym) for sym in SYMBOLS.values())
    SYM_LIB.write_text(
        "(kicad_symbol_lib\n"
        "  (version 20241209)\n"
        '  (generator "codex-compact-power-board")\n'
        f"{body}\n"
        ")\n",
        encoding="utf-8",
    )


def symbol_lib_body_for_schematic() -> str:
    return "\n".join("    " + line if line else "" for sym in SYMBOLS.values() for line in symbol_text(sym, embedded=True).splitlines())


def write_footprints() -> None:
    FP_LIB.mkdir(exist_ok=True)

    def prop(name: str, value: str, x: float, y: float, layer: str) -> str:
        return (
            f'\t(property "{name}" "{value}"\n'
            f"\t\t(at {fmt(x)} {fmt(y)} 0)\n"
            f'\t\t(layer "{layer}")\n'
            f'\t\t(uuid "{u()}")\n'
            "\t\t(effects (font (size 1 1) (thickness 0.15)))\n"
            "\t)\n"
        )

    def line(x1: float, y1: float, x2: float, y2: float, width: float = 0.12, layer: str = "F.SilkS") -> str:
        return (
            f"\t(fp_line (start {fmt(x1)} {fmt(y1)}) (end {fmt(x2)} {fmt(y2)})\n"
            f'\t\t(stroke (width {fmt(width)}) (type solid))\n'
            f'\t\t(layer "{layer}")\n'
            f'\t\t(uuid "{u()}")\n'
            "\t)\n"
        )

    def box(x1: float, y1: float, x2: float, y2: float, layer: str = "F.SilkS") -> str:
        return line(x1, y1, x2, y1, layer=layer) + line(x2, y1, x2, y2, layer=layer) + line(x2, y2, x1, y2, layer=layer) + line(x1, y2, x1, y1, layer=layer)

    def user_text(text: str, x: float, y: float, size: float = 0.8, rot: float = 0, layer: str = "F.SilkS") -> str:
        return (
            f'\t(fp_text user "{sx(text)}"\n'
            f"\t\t(at {fmt(x)} {fmt(y)} {fmt(rot)})\n"
            f'\t\t(layer "{layer}")\n'
            f'\t\t(uuid "{u()}")\n'
            f"\t\t(effects (font (size {fmt(size)} {fmt(size)}) (thickness 0.1)))\n"
            "\t)\n"
        )

    def pad(name: str | int, kind: str, shape: str, x: float, y: float, sx_: float, sy_: float, drill: float, rot: float = 0) -> str:
        rot_part = f" {fmt(rot)}" if rot else ""
        return (
            f'\t(pad "{name}" {kind} {shape}\n'
            f"\t\t(at {fmt(x)} {fmt(y)}{rot_part})\n"
            f"\t\t(size {fmt(sx_)} {fmt(sy_)})\n"
            f"\t\t(drill {fmt(drill)})\n"
            '\t\t(layers "*.Cu" "*.Mask")\n'
            f'\t\t(uuid "{u()}")\n'
            "\t)\n"
        )

    def footprint(name: str, desc: str, tags: str, body: str, ref_y: float, val_y: float) -> str:
        return (
            f'(footprint "{name}"\n'
            "\t(version 20260206)\n"
            '\t(generator "pcbnew")\n'
            '\t(generator_version "10.0")\n'
            '\t(layer "F.Cu")\n'
            f'\t(descr "{sx(desc)}")\n'
            f'\t(tags "{sx(tags)}")\n'
            + prop("Reference", "REF**", 0, ref_y, "F.SilkS")
            + prop("Value", name, 0, val_y, "F.Fab")
            + "\t(attr through_hole)\n"
            + body
            + ")\n"
        )

    # Adafruit INA260 Product 4226 carrier footprint from Adafruit Eagle board geometry:
    # board 22.86 x 22.86 mm, 2.5 mm mounting holes, 8-pin header, 5.08 mm current terminal.
    ina_body = box(-11.43, -11.43, 11.43, 11.43)
    ina_body += user_text("VCC GND SCL SDA ALERT VBUS IN+ IN-", 0, -9.6, 0.7, layer="F.Fab")
    # Header positions 7/8 exist mechanically on the breakout but are not used as carrier-board
    # high-current nodes. VIN+ and VIN- are routed to the 5.08 mm terminal pads below.
    for idx, x in enumerate([-8.89, -6.35, -3.81, -1.27, 1.27, 3.81], start=1):
        ina_body += pad(idx, "thru_hole", "rect" if idx == 1 else "circle", x, -8.89, 1.78, 1.78, 1.0)
    ina_body += pad("H7", "thru_hole", "circle", 6.35, -8.89, 1.78, 1.78, 1.0)
    ina_body += pad("H8", "thru_hole", "circle", 8.89, -8.89, 1.78, 1.78, 1.0)
    ina_body += pad(7, "thru_hole", "oval", -2.54, 7.62, 2.2, 3.0, 1.1, 90)
    ina_body += pad(8, "thru_hole", "oval", 2.54, 7.62, 2.2, 3.0, 1.1, 90)
    ina_body += pad("", "np_thru_hole", "circle", -8.89, 8.89, 3.2, 3.2, 2.5)
    ina_body += pad("", "np_thru_hole", "circle", 8.89, 8.89, 3.2, 3.2, 2.5)
    (FP_LIB / "Adafruit_INA260_4226_Module.kicad_mod").write_text(
        footprint(
            "Adafruit_INA260_4226_Module",
            "Adafruit INA260 Product 4226 breakout carrier footprint: 22.86mm square, 8-pin header plus duplicated VIN terminal pads",
            "Adafruit INA260 4226 module",
            ina_body,
            -12.7,
            12.7,
        ),
        encoding="utf-8",
    )

    # Boost converter footprint from user-provided screenshots and later physical verification: 60 mm x 42 mm x 20 mm.
    boost_body = box(-30, -21, 30, 21, layer="F.SilkS")
    boost_body += user_text("VERIFIED 60x42 MODULE, M3 HOLES, TERMINALS", 0, 0, 0.9, layer="F.Fab")
    boost_body += user_text("IN- IN+", -27, -5, 0.8, 90, layer="F.Fab")
    boost_body += user_text("OUT- OUT+", 27, -5, 0.8, 90, layer="F.Fab")
    boost_body += pad(1, "thru_hole", "circle", -27, 5, 3.6, 3.6, 1.8)
    boost_body += pad(2, "thru_hole", "circle", -27, -5, 3.6, 3.6, 1.8)
    boost_body += pad(3, "thru_hole", "circle", 27, 5, 3.6, 3.6, 1.8)
    boost_body += pad(4, "thru_hole", "circle", 27, -5, 3.6, 3.6, 1.8)
    boost_body += pad(5, "thru_hole", "circle", -24, -15, 1.8, 1.8, 0.9)
    boost_body += pad(6, "thru_hole", "circle", -21, -15, 1.8, 1.8, 0.9)
    for hx in (-26, 26):
        for hy in (-17, 17):
            boost_body += pad("", "np_thru_hole", "circle", hx, hy, 3.2, 3.2, 3.2)
    old_boost = FP_LIB / "Boost_Module_60x42_VERIFY.kicad_mod"
    if old_boost.exists():
        old_boost.unlink()
    (FP_LIB / "Boost_Module_60x42_VERIFIED.kicad_mod").write_text(
        footprint(
            "Boost_Module_60x42_VERIFIED",
            "Amazon boost converter module carrier, 60x42x20mm; hole and terminal positions physically verified",
            "boost converter module 60x42 verified",
            boost_body,
            -23.5,
            23.5,
        ),
        encoding="utf-8",
    )


def write_tables_and_gitignore() -> None:
    (ROOT / "sym-lib-table").write_text(
        '(sym_lib_table\n  (version 7)\n  (lib (name "Power_Testing_Board")(type "KiCad")(uri "${KIPRJMOD}/Power_Testing_Board.kicad_sym")(options "")(descr "Project-local symbols for compact CubeSat power testing board"))\n)\n',
        encoding="utf-8",
    )
    (ROOT / "fp-lib-table").write_text(
        '(fp_lib_table\n  (version 7)\n  (lib (name "Power_Testing_Board")(type "KiCad")(uri "${KIPRJMOD}/Power_Testing_Board.pretty")(options "")(descr "Project-local footprints for compact CubeSat power testing board"))\n)\n',
        encoding="utf-8",
    )
    gitignore = ROOT / ".gitignore"
    existing = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    entries = [
        "*.kicad_prl",
        "*.lck",
        "*-backups/",
        ".history/",
        "*/.history/",
        "fp-info-cache",
        "*.net",
        "*erc*.rpt",
        "*drc*.rpt",
        "gerbers/",
        "__pycache__/",
    ]
    merged = existing
    if "KiCad local/cache files" not in merged:
        merged += "\n# KiCad local/cache files\n"
    for e in entries:
        if e not in merged.splitlines():
            merged += e + "\n"
    gitignore.write_text(merged.lstrip(), encoding="utf-8")


def write_schematic() -> None:
    lib_symbols = symbol_lib_body_for_schematic()
    items: list[str] = []
    items.append('  (title_block (title "Compact CubeSat EPS Power Testing Board") (rev "2") (company "CSULB SHARKSAT TEAM"))')
    items.append("  (lib_symbols\n" + lib_symbols + "\n  )")

    for c in COMPONENTS:
        sym = SYMBOLS[c.symbol]
        dnp = "no" if c.on_board else "yes"
        items += [
            f'  (symbol (lib_id "Power_Testing_Board:{sx(c.symbol)}") (at {fmt(c.x)} {fmt(c.y)} 0) (unit 1) (in_bom yes) (on_board {"yes" if c.on_board else "no"}) (dnp {dnp}) (uuid "{u()}")',
            f'    (property "Reference" "{sx(c.ref)}" (at {fmt(c.x)} {fmt(c.y - sym.h/2 - 2.2)} 0) (effects (font (size 1.0 1.0))))',
            f'    (property "Value" "{sx(c.value)}" (at {fmt(c.x)} {fmt(c.y + sym.h/2 + 2.2)} 0) (effects (font (size 1.0 1.0))))',
            f'    (property "Footprint" "{sx(c.footprint)}" (at {fmt(c.x)} {fmt(c.y)} 0) (effects (font (size 1.0 1.0)) hide))',
            f'    (property "Datasheet" "{sx(sym.datasheet)}" (at {fmt(c.x)} {fmt(c.y)} 0) (effects (font (size 1.0 1.0)) hide))',
            f'    (instances (project "{PROJECT}" (path "/" (reference "{sx(c.ref)}") (unit 1))))',
            "  )",
        ]
        # Wire stubs and local labels.
        pin_lookup = {p.number: p for p in sym.pins}
        for pin_no, net in c.pin_nets.items():
            p = pin_lookup.get(str(pin_no))
            if p is None:
                continue
            px = c.x + p.x
            py = c.y - p.y
            if p.angle == 0:
                lx, ly = px - 2.54, py
            elif p.angle == 180:
                lx, ly = px + 2.54, py
            elif p.angle == 90:
                lx, ly = px, py - 2.54
            else:
                lx, ly = px, py + 2.54
            items.append(f'  (wire (pts (xy {fmt(px)} {fmt(py)}) (xy {fmt(lx)} {fmt(ly)})) (stroke (width 0) (type default)) (uuid "{u()}"))')
            items.append(f'  (label "{sx(net)}" (at {fmt(lx)} {fmt(ly)} 0) (effects (font (size 0.9 0.9)) (justify left bottom)) (uuid "{u()}"))')
        for p in sym.pins:
            if p.number in {str(k) for k in c.pin_nets}:
                continue
            px = c.x + p.x
            py = c.y - p.y
            items.append(f'  (no_connect (at {fmt(px)} {fmt(py)}) (uuid "{u()}"))')

    notes = [
        (10, 10, "Power path on every rail: RAW -> eFuse -> INA260 VIN+ -> INA260 VIN- -> PROTECTED output. INA260 VIN- is the downstream positive rail, never GND."),
        (10, 15, "Serviceable layout choice: eFuse ICs are on the main PCB for manufacturer assembly. If field replacement becomes more important than board area, move each eFuse circuit to a plug-in daughterboard."),
        (10, 20, "Boost module footprint uses physically verified 60 mm x 42 mm x 20 mm module geometry."),
        (10, 25, "Only user-selected H1/H2 mission power and GND pins are connected. Excluded/communication pins are not represented in this schematic."),
    ]
    for x, y, text in notes:
        items.append(f'  (text "{sx(text)}" (exclude_from_sim no) (at {fmt(x)} {fmt(y)} 0) (effects (font (size 1.2 1.2) (bold yes)) (justify left bottom)) (uuid "{u()}"))')

    SCH.write_text(
        "(kicad_sch\n"
        "  (version 20250114)\n"
        '  (generator "codex-compact-power-board")\n'
        f'  (uuid "{u()}")\n'
        '  (paper "A3")\n'
        + "\n".join(items)
        + "\n)\n",
        encoding="utf-8",
    )


def update_project() -> None:
    if not PRO.exists():
        return
    try:
        data = json.loads(PRO.read_text(encoding="utf-8"))
    except Exception:
        return
    data.setdefault("meta", {})
    data.setdefault("schematic", {})
    data["schematic"]["drawing"] = data["schematic"].get("drawing", {})
    data["schematic"]["drawing"]["default_line_thickness"] = data["schematic"]["drawing"].get("default_line_thickness", 6)
    data["sheets"] = [[str(uuid.uuid4()), "Root"]]
    data.setdefault("net_settings", {})
    data["net_settings"]["meta"] = {"version": 5}
    data["net_settings"]["classes"] = [
        {
            "bus_width": 12,
            "clearance": 0.2,
            "diff_pair_gap": 0.25,
            "diff_pair_via_gap": 0.25,
            "diff_pair_width": 0.2,
            "line_style": 0,
            "microvia_diameter": 0.3,
            "microvia_drill": 0.1,
            "name": "Default",
            "pcb_color": "rgba(0, 0, 0, 0.000)",
            "priority": 2147483647,
            "schematic_color": "rgba(0, 0, 0, 0.000)",
            "track_width": 0.25,
            "tuning_profile": "",
            "via_diameter": 0.6,
            "via_drill": 0.3,
            "wire_width": 6,
        },
        {
            "bus_width": 12,
            "clearance": 0.35,
            "diff_pair_gap": 0.25,
            "diff_pair_via_gap": 0.25,
            "diff_pair_width": 0.2,
            "line_style": 0,
            "microvia_diameter": 0.3,
            "microvia_drill": 0.1,
            "name": "HIGH_CURRENT_3V3",
            "pcb_color": "rgba(255, 128, 0, 0.800)",
            "priority": 100,
            "schematic_color": "rgba(255, 128, 0, 0.800)",
            "track_width": 3.0,
            "tuning_profile": "",
            "via_diameter": 1.6,
            "via_drill": 0.8,
            "wire_width": 6,
        },
        {
            "bus_width": 12,
            "clearance": 0.35,
            "diff_pair_gap": 0.25,
            "diff_pair_via_gap": 0.25,
            "diff_pair_width": 0.2,
            "line_style": 0,
            "microvia_diameter": 0.3,
            "microvia_drill": 0.1,
            "name": "HIGH_CURRENT_5V",
            "pcb_color": "rgba(255, 64, 64, 0.800)",
            "priority": 100,
            "schematic_color": "rgba(255, 64, 64, 0.800)",
            "track_width": 3.0,
            "tuning_profile": "",
            "via_diameter": 1.6,
            "via_drill": 0.8,
            "wire_width": 6,
        },
        {
            "bus_width": 12,
            "clearance": 0.4,
            "diff_pair_gap": 0.25,
            "diff_pair_via_gap": 0.25,
            "diff_pair_width": 0.2,
            "line_style": 0,
            "microvia_diameter": 0.3,
            "microvia_drill": 0.1,
            "name": "HIGH_CURRENT_12V",
            "pcb_color": "rgba(255, 220, 0, 0.800)",
            "priority": 100,
            "schematic_color": "rgba(255, 220, 0, 0.800)",
            "track_width": 3.5,
            "tuning_profile": "",
            "via_diameter": 1.8,
            "via_drill": 0.9,
            "wire_width": 6,
        },
        {
            "bus_width": 12,
            "clearance": 0.45,
            "diff_pair_gap": 0.25,
            "diff_pair_via_gap": 0.25,
            "diff_pair_width": 0.2,
            "line_style": 0,
            "microvia_diameter": 0.3,
            "microvia_drill": 0.1,
            "name": "HIGH_CURRENT_16V8",
            "pcb_color": "rgba(180, 80, 255, 0.800)",
            "priority": 100,
            "schematic_color": "rgba(180, 80, 255, 0.800)",
            "track_width": 3.5,
            "tuning_profile": "",
            "via_diameter": 1.8,
            "via_drill": 0.9,
            "wire_width": 6,
        },
        {
            "bus_width": 12,
            "clearance": 0.3,
            "diff_pair_gap": 0.25,
            "diff_pair_via_gap": 0.25,
            "diff_pair_width": 0.2,
            "line_style": 0,
            "microvia_diameter": 0.3,
            "microvia_drill": 0.1,
            "name": "GND_POWER",
            "pcb_color": "rgba(0, 180, 80, 0.800)",
            "priority": 100,
            "schematic_color": "rgba(0, 180, 80, 0.800)",
            "track_width": 2.0,
            "tuning_profile": "",
            "via_diameter": 1.2,
            "via_drill": 0.6,
            "wire_width": 6,
        },
        {
            "bus_width": 12,
            "clearance": 0.2,
            "diff_pair_gap": 0.25,
            "diff_pair_via_gap": 0.25,
            "diff_pair_width": 0.2,
            "line_style": 0,
            "microvia_diameter": 0.3,
            "microvia_drill": 0.1,
            "name": "SIGNAL",
            "pcb_color": "rgba(128, 128, 128, 0.800)",
            "priority": 100,
            "schematic_color": "rgba(128, 128, 128, 0.800)",
            "track_width": 0.25,
            "tuning_profile": "",
            "via_diameter": 0.6,
            "via_drill": 0.3,
            "wire_width": 6,
        },
        {
            "bus_width": 12,
            "clearance": 0.2,
            "diff_pair_gap": 0.25,
            "diff_pair_via_gap": 0.25,
            "diff_pair_width": 0.2,
            "line_style": 0,
            "microvia_diameter": 0.3,
            "microvia_drill": 0.1,
            "name": "I2C",
            "pcb_color": "rgba(0, 128, 255, 0.800)",
            "priority": 100,
            "schematic_color": "rgba(0, 128, 255, 0.800)",
            "track_width": 0.25,
            "tuning_profile": "",
            "via_diameter": 0.6,
            "via_drill": 0.3,
            "wire_width": 6,
        },
        {
            "bus_width": 12,
            "clearance": 0.2,
            "diff_pair_gap": 0.25,
            "diff_pair_via_gap": 0.25,
            "diff_pair_width": 0.2,
            "line_style": 0,
            "microvia_diameter": 0.3,
            "microvia_drill": 0.1,
            "name": "CONTROL",
            "pcb_color": "rgba(0, 220, 220, 0.800)",
            "priority": 100,
            "schematic_color": "rgba(0, 220, 220, 0.800)",
            "track_width": 0.25,
            "tuning_profile": "",
            "via_diameter": 0.6,
            "via_drill": 0.3,
            "wire_width": 6,
        },
    ]
    data["net_settings"]["netclass_patterns"] = [
        {"netclass": "HIGH_CURRENT_3V3", "pattern": "+3V3_*"},
        {"netclass": "HIGH_CURRENT_5V", "pattern": "+5V_*"},
        {"netclass": "HIGH_CURRENT_12V", "pattern": "+12V_*"},
        {"netclass": "HIGH_CURRENT_16V8", "pattern": "+16V8_*"},
        {"netclass": "GND_POWER", "pattern": "GND"},
        {"netclass": "I2C", "pattern": "I2C_*"},
        {"netclass": "CONTROL", "pattern": "RESET_*"},
        {"netclass": "CONTROL", "pattern": "ARD_RESET_*"},
        {"netclass": "CONTROL", "pattern": "GATE_*"},
        {"netclass": "CONTROL", "pattern": "FLT_*"},
        {"netclass": "CONTROL", "pattern": "ATX_*"},
        {"netclass": "CONTROL", "pattern": "+ARDUINO_5V"},
        {"netclass": "CONTROL", "pattern": "+5VSB"},
    ]
    data["net_settings"]["netclass_assignments"] = None
    data["net_settings"]["net_colors"] = None
    PRO.write_text(json.dumps(data, indent=2), encoding="utf-8")


def board_load_footprint(footprint: str):
    import pcbnew

    lib, name = footprint.split(":", 1)
    if lib == "Power_Testing_Board":
        return pcbnew.FootprintLoad(str(FP_LIB), name)
    # KiCad footprint libraries live in share/kicad/footprints/<lib>.pretty.
    lib_path = KICAD_SHARE / "footprints" / f"{lib}.pretty"
    return pcbnew.FootprintLoad(str(lib_path), name)


def write_board() -> None:
    import pcbnew

    board = pcbnew.BOARD()
    settings = board.GetDesignSettings()
    settings.m_MinThroughDrill = int(0.2 * 1_000_000)
    settings.m_MinSilkTextHeight = int(0.7 * 1_000_000)
    settings.m_MinSilkTextThickness = int(0.1 * 1_000_000)
    net_items: dict[str, object] = {}

    def netinfo(name: str):
        if name not in net_items:
            ni = pcbnew.NETINFO_ITEM(board, name)
            board.Add(ni)
            net_items[name] = ni
        return net_items[name]

    placements = {
        "J1": (10, 72, 90), "J2": (16, 160, 0), "J3": (45, 160, 0), "J4": (222, 52, 90),
        "A1": (36, 24, 90), "U9": (198, 118, 0),
        "U1": (82, 40, 0), "U2": (82, 70, 0), "U3": (82, 100, 0), "U4": (82, 130, 0),
        "U5": (112, 40, 0), "U6": (112, 70, 0), "U7": (112, 100, 0), "U8": (112, 130, 0),
        "JH1": (158, 18, 0), "JH2": (176, 18, 0),
        "SW1": (104, 160, 0), "SW2": (126, 160, 0), "SW3": (148, 160, 0), "SW4": (170, 160, 0),
        "Q1": (104, 150, 0), "Q2": (126, 150, 0), "Q3": (148, 150, 0), "Q4": (170, 150, 0), "Q5": (65, 160, 0),
        "C1": (69, 32, 0), "C2": (96, 32, 0), "C3": (69, 62, 0), "C4": (96, 62, 0),
        "C5": (69, 92, 0), "C6": (96, 92, 0), "C7": (88, 122, 0), "C8": (96, 122, 0),
        "R1": (69, 48, 0), "R2": (54, 28, 0), "R3": (62, 28, 0), "R4": (54, 52, 0), "R5": (62, 52, 0),
        "R8": (132, 32, 0), "R9": (69, 78, 0), "R10": (54, 58, 0), "R11": (62, 58, 0),
        "R12": (54, 82, 0), "R13": (62, 82, 0), "R16": (132, 62, 0), "R17": (69, 108, 0),
        "R18": (54, 88, 0), "R19": (62, 88, 0), "R20": (54, 112, 0), "R21": (62, 112, 0),
        "R24": (132, 92, 0), "R25": (69, 138, 0), "R26": (54, 118, 0), "R27": (62, 118, 0),
        "R28": (54, 142, 0), "R29": (62, 142, 0), "R32": (132, 122, 0),
        "R6": (100, 144, 0), "R7": (108, 144, 0), "R14": (122, 144, 0), "R15": (130, 144, 0),
        "R22": (144, 144, 0), "R23": (152, 144, 0), "R30": (166, 144, 0), "R31": (174, 144, 0),
        "R33": (62, 150, 0), "R34": (70, 150, 0),
        "TP1": (73, 30, 0), "TP2": (98, 26, 0), "TP3": (126, 48, 0),
        "TP4": (73, 60, 0), "TP5": (98, 56, 0), "TP6": (126, 78, 0),
        "TP7": (73, 90, 0), "TP8": (98, 86, 0), "TP9": (126, 108, 0),
        "TP10": (92, 124, 0), "TP11": (98, 116, 0), "TP12": (126, 138, 0),
        "TP13": (32, 150, 0), "TP14": (114, 26, 0), "TP15": (121, 26, 0),
        "TP16": (56, 160, 0), "TP17": (78, 30, 0), "TP18": (32, 154, 0),
        "TP19": (96, 152, 0), "TP20": (118, 152, 0), "TP21": (140, 152, 0), "TP22": (162, 152, 0),
        "TP23": (132, 36, 0), "TP24": (132, 66, 0), "TP25": (132, 96, 0), "TP26": (132, 126, 0),
        "TP27": (176, 106, 0), "TP28": (220, 106, 0), "TP29": (178, 126, 0),
    }

    # Compact autogenerated fallback placement for passives and test points.
    passive_x, passive_y = 54, 112
    for c in COMPONENTS:
        if c.ref not in placements:
            if c.ref.startswith("TP"):
                idx = int(c.ref[2:]) - 1
                placements[c.ref] = (88 + (idx % 10) * 7, 5 + (idx // 10) * 6, 0)
            elif c.ref.startswith("R"):
                idx = int(c.ref[1:]) - 1
                placements[c.ref] = (106 + (idx % 7) * 7, 75 + (idx // 7) * 5, 0)
            elif c.ref.startswith("C"):
                idx = int(c.ref[1:]) - 1
                placements[c.ref] = (106 + (idx % 7) * 7, 106 + (idx // 7) * 5, 0)
            else:
                placements[c.ref] = (passive_x, passive_y, 0)
                passive_x += 8

    for c in COMPONENTS:
        fp = board_load_footprint(c.footprint)
        if fp is None:
            raise RuntimeError(f"Could not load footprint {c.footprint} for {c.ref}")
        fp.SetReference(c.ref)
        fp.SetValue(c.value)
        x, y, rot = placements[c.ref]
        fp.SetPosition(pcbnew.VECTOR2I(int(x * 1_000_000), int(y * 1_000_000)))
        fp.SetOrientationDegrees(rot)
        for pad in fp.Pads():
            net = c.pin_nets.get(pad.GetNumber())
            if net:
                pad.SetNet(netinfo(net))
        board.Add(fp)

    # Board outline: clarity/testability layout with module clearance and accessible edge connectors.
    outline = [(0, 0), (230, 0), (230, 170), (0, 170), (0, 0)]
    for (x1, y1), (x2, y2) in zip(outline, outline[1:]):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pcbnew.VECTOR2I(int(x1 * 1_000_000), int(y1 * 1_000_000)))
        seg.SetEnd(pcbnew.VECTOR2I(int(x2 * 1_000_000), int(y2 * 1_000_000)))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(int(0.1 * 1_000_000))
        board.Add(seg)

    def add_text(txt: str, x: float, y: float, size: float = 1.0):
        t = pcbnew.PCB_TEXT(board)
        t.SetText(txt)
        t.SetPosition(pcbnew.VECTOR2I(int(x * 1_000_000), int(y * 1_000_000)))
        t.SetLayer(pcbnew.F_SilkS)
        t.SetTextSize(pcbnew.VECTOR2I(int(size * 1_000_000), int(size * 1_000_000)))
        t.SetTextThickness(int(0.15 * 1_000_000))
        board.Add(t)

    add_text("EPS POWER TEST - 2 OZ Cu RECOMMENDED", 82, 166, 1.0)
    add_text("ATX INPUTS", 15, 6, 1.0)
    add_text("RESET_3V3 RESET_5V RESET_12V RESET_16V8", 90, 154, 0.85)
    add_text("BOOST 60x42 VERIFIED", 166, 94, 0.9)
    add_text("H1/H2 POWER/GND ONLY", 146, 8, 0.9)
    add_text("RAW -> EFUSE -> INA260 -> OUTPUT", 104, 22, 0.9)

    pcbnew.SaveBoard(str(PCB), board)


def main() -> None:
    make_symbols()
    make_components()
    write_symbol_library()
    write_footprints()
    write_tables_and_gitignore()
    write_schematic()
    update_project()
    write_board()


if __name__ == "__main__":
    main()
