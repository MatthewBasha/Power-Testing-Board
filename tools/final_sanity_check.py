from __future__ import annotations

import csv
from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
PCB = ROOT / "Power Testing board.kicad_pcb"
OUT = ROOT / "fabrication" / "JLCPCB" / "final_sanity_check.txt"


def pad_net(board: pcbnew.BOARD, ref: str, pad: str) -> str:
    fp = board.FindFootprintByReference(ref)
    if fp is None:
        return "<missing footprint>"
    p = fp.FindPadByNumber(str(pad))
    if p is None:
        return "<missing pad>"
    return p.GetNetname()


def expect(lines: list[str], label: str, actual, expected) -> int:
    ok = actual == expected
    lines.append(f"{'PASS' if ok else 'FAIL'}: {label}: actual={actual} expected={expected}")
    return 0 if ok else 1


def read_bom_refs(path: Path) -> set[str]:
    if not path.exists():
        return set()
    refs: set[str] = set()
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            designators = row.get("Designator", "")
            for ref in designators.replace(" ", "").split(","):
                if ref:
                    refs.add(ref)
    return refs


def read_cpl_refs(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as f:
        return {row["Designator"] for row in csv.DictReader(f)}


def main() -> None:
    board = pcbnew.LoadBoard(str(PCB))
    lines = ["Final sanity check for Power Testing Board 4-layer revision", ""]
    failures = 0

    rails = [
        ("3V3", "U1", "U5", "+3V3_RAW", "+3V3_EFUSE_OUT", "+3V3_PROTECTED"),
        ("5V", "U2", "U6", "+5V_RAW", "+5V_EFUSE_OUT", "+5V_PROTECTED"),
        ("12V", "U3", "U7", "+12V_RAW", "+12V_EFUSE_OUT", "+12V_PROTECTED"),
        ("16V8", "U4", "U8", "+16V8_RAW", "+16V8_EFUSE_OUT", "+16V8_PROTECTED"),
    ]
    for name, efuse, ina, raw, efout, prot in rails:
        if efuse == "U1":
            failures += expect(lines, f"{name} eFuse IN", pad_net(board, efuse, "5"), raw)
            failures += expect(lines, f"{name} eFuse OUT", pad_net(board, efuse, "6"), efout)
        else:
            failures += expect(lines, f"{name} eFuse IN pins", {pad_net(board, efuse, p) for p in ("1", "2", "5")}, {raw})
            failures += expect(lines, f"{name} eFuse OUT pins", {pad_net(board, efuse, p) for p in ("17", "18")}, {efout})
        failures += expect(lines, f"{name} INA260 VIN+", pad_net(board, ina, "7"), efout)
        failures += expect(lines, f"{name} INA260 VIN-", pad_net(board, ina, "8"), prot)

    for pad, net in {
        "1": "+3V3_PROTECTED",
        "2": "GND",
        "3": "+5V_PROTECTED",
        "4": "GND",
        "5": "+12V_PROTECTED",
        "6": "GND",
        "7": "+16V8_PROTECTED",
        "8": "GND",
    }.items():
        failures += expect(lines, f"J4 pad {pad}", pad_net(board, "J4", pad), net)

    for pad, net in {
        "48": "+3V3_PROTECTED",
        "47": "+5V_PROTECTED",
        "49": "+5V_PROTECTED",
        "52": "+12V_PROTECTED",
    }.items():
        failures += expect(lines, f"JH1 pin {pad}", pad_net(board, "JH1", pad), net)
    for pad in ["22", "24", "27", "31", "32", "36", "39", "40", "42"]:
        failures += expect(lines, f"JH1 GND pin {pad}", pad_net(board, "JH1", pad), "GND")

    for pad, net in {
        "25": "+5V_PROTECTED",
        "26": "+5V_PROTECTED",
        "27": "+3V3_PROTECTED",
        "28": "+3V3_PROTECTED",
        "45": "+16V8_PROTECTED",
        "46": "+16V8_PROTECTED",
    }.items():
        failures += expect(lines, f"JH2 pin {pad}", pad_net(board, "JH2", pad), net)
    for pad in ["29", "30", "31", "32", "36", "39", "40", "41", "42", "43", "44"]:
        failures += expect(lines, f"JH2 GND pin {pad}", pad_net(board, "JH2", pad), "GND")

    failures += expect(lines, "PS_ON terminal J2 pin 1", pad_net(board, "J2", "1"), "ATX_PS_ON_N")
    failures += expect(lines, "ATX switch J3 pin 1", pad_net(board, "J3", "1"), "ATX_PS_ON_N")
    failures += expect(lines, "PS_ON MOSFET Q5 drain", pad_net(board, "Q5", "3"), "ATX_PS_ON_N")
    failures += expect(lines, "Arduino D10 PS_ON control net", pad_net(board, "A1", "13"), "ATX_PS_ON_CTL")

    fp = board.FindFootprintByReference("A1")
    failures += expect(lines, "Arduino Nano orientation", round(fp.GetOrientationDegrees(), 2), 180.0)

    layer_counts = {board.GetLayerName(layer): 0 for layer in [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]}
    for track in board.GetTracks():
        name = board.GetLayerName(track.GetLayer())
        layer_counts[name] = layer_counts.get(name, 0) + 1
    failures += expect(lines, "No tracks on In1.Cu", layer_counts.get("In1.Cu", 0), 0)
    failures += expect(lines, "No tracks on In2.Cu", layer_counts.get("In2.Cu", 0), 0)

    lines.extend(["", f"Rail/output sanity failures: {failures}", f"Tracks by layer: {layer_counts}", f"Zones: {len(list(board.Zones()))}"])
    for zone in board.Zones():
        lines.append(f"  {zone.GetNetname()} on {board.GetLayerName(zone.GetLayer())}, priority {zone.GetAssignedPriority()}")

    bom_refs = read_bom_refs(ROOT / "fabrication" / "JLCPCB" / "BOM_SMD_JLCPCB.csv")
    cpl_refs = read_cpl_refs(ROOT / "fabrication" / "JLCPCB" / "CPL_SMD_JLCPCB.csv")
    if bom_refs or cpl_refs:
        lines.append("")
        lines.append(
            f"BOM/CPL SMD refs: BOM={len(bom_refs)} CPL={len(cpl_refs)} "
            f"missing_in_CPL={sorted(bom_refs - cpl_refs)} missing_in_BOM={sorted(cpl_refs - bom_refs)}"
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
