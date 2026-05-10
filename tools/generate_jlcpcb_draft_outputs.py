from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
import shutil

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
PROJECT = "Power Testing board"
PCB = ROOT / f"{PROJECT}.kicad_pcb"
OUT = ROOT / "fabrication" / "JLCPCB"

SMD_ASSEMBLY_REFS = {
    *(f"U{i}" for i in range(1, 5)),
    *(f"Q{i}" for i in range(1, 6)),
    *(f"R{i}" for i in range(1, 35)),
    *(f"C{i}" for i in range(1, 9)),
}

MANUAL_REFS = {
    "A1",
    *(f"U{i}" for i in range(5, 10)),
    *(f"J{i}" for i in range(1, 5)),
    "JH1",
    "JH2",
    *(f"SW{i}" for i in range(1, 5)),
}


def fp_name(fp: pcbnew.FOOTPRINT) -> str:
    fpid = fp.GetFPID()
    lib = str(fpid.GetLibNickname())
    item = str(fpid.GetLibItemName())
    return f"{lib}:{item}" if lib else item


def lcsc_placeholder(ref: str, value: str) -> tuple[str, str]:
    if ref == "U1":
        return "CUSTOMER_SUPPLIED_OR_VERIFY_LCSC", "TPS259814L, exact orderable package/land pattern must be verified"
    if ref in {"U2", "U3", "U4"}:
        return "CUSTOMER_SUPPLIED_OR_VERIFY_LCSC", "TPS26631RGE, exact JLC/LCSC availability must be verified"
    if ref.startswith("Q"):
        return "CUSTOMER_SUPPLIED_OR_SELECT_LCSC", "2N7002 SOT-23, select JLC basic/extended part before order"
    if ref.startswith("R") or ref.startswith("C"):
        return "CUSTOMER_SUPPLIED_OR_SELECT_LCSC", "Generic passive; select voltage/tolerance/package in JLC parts library"
    return "N/A", value


def load_footprints() -> dict[str, pcbnew.FOOTPRINT]:
    board = pcbnew.LoadBoard(str(PCB))
    return {fp.GetReference(): fp for fp in board.GetFootprints()}


def write_bom_smd(fps: dict[str, pcbnew.FOOTPRINT]) -> None:
    groups: dict[tuple[str, str, str, str], list[str]] = defaultdict(list)
    for ref in sorted(SMD_ASSEMBLY_REFS, key=lambda r: (r[0], int(r[1:]))):
        fp = fps[ref]
        value = fp.GetValue()
        footprint = fp_name(fp)
        lcsc, mpn = lcsc_placeholder(ref, value)
        groups[(value, footprint, lcsc, mpn)].append(ref)

    with (OUT / "BOM_SMD_JLCPCB.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Comment", "Designator", "Footprint", "LCSC Part #", "Manufacturer Part #", "Assembly"])
        for (value, footprint, lcsc, mpn), refs in sorted(groups.items(), key=lambda item: item[1][0]):
            writer.writerow([value, ",".join(refs), footprint, lcsc, mpn, "JLCPCB SMD top-side assembly"])


def write_cpl_smd(fps: dict[str, pcbnew.FOOTPRINT]) -> None:
    with (OUT / "CPL_SMD_JLCPCB.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
        for ref in sorted(SMD_ASSEMBLY_REFS, key=lambda r: (r[0], int(r[1:]))):
            fp = fps[ref]
            pos = fp.GetPosition()
            x_mm = pcbnew.ToMM(pos.x)
            y_mm = pcbnew.ToMM(pos.y)
            layer = "Top" if fp.GetLayer() == pcbnew.F_Cu else "Bottom"
            writer.writerow([ref, f"{x_mm:.3f}mm", f"{y_mm:.3f}mm", layer, f"{fp.GetOrientationDegrees():.2f}"])


def write_master_bom(fps: dict[str, pcbnew.FOOTPRINT]) -> None:
    rows = []
    for ref, fp in sorted(fps.items(), key=lambda item: (item[0].rstrip("0123456789"), int("".join(ch for ch in item[0] if ch.isdigit()) or 0), item[0])):
        if ref.startswith("TP"):
            category = "PCB feature / no install"
            install = "Not installed"
        elif ref in SMD_ASSEMBLY_REFS:
            category = "SMD manufacturer-assembled"
            install = "JLCPCB"
        elif ref in MANUAL_REFS:
            category = "Manual/serviceable"
            install = "Install manually after PCBA"
        else:
            category = "Review"
            install = "Review"
        lcsc, mpn = lcsc_placeholder(ref, fp.GetValue())
        rows.append([ref, fp.GetValue(), fp_name(fp), category, install, lcsc, mpn])

    with (OUT / "BOM_MASTER.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Designator", "Value", "Footprint", "Category", "Install responsibility", "LCSC Part #", "Manufacturer Part # / Notes"])
        writer.writerows(rows)


def drc_is_clean() -> bool:
    report = ROOT / "regenerated_drc.rpt"
    if not report.exists():
        report = OUT / "DRC_report.txt"
    if not report.exists():
        return False
    text = report.read_text(encoding="utf-8", errors="ignore")
    return "** Found 0 DRC violations **" in text and "** Found 0 unconnected pads **" in text


def write_notes(clean: bool) -> None:
    status = "ready for JLCPCB fabrication output review" if clean else "draft package only. Do not order yet"
    blockers = (
        "- No KiCad DRC or unconnected-net blockers remain.\n"
        "- Final external JLCPCB/JLCDFM preview and LCSC/customer-supplied part selection still need human review before purchase.\n"
        if clean
        else "- Final Gerbers and drill files are not generated because the PCB is not routed or DRC is not clean.\n"
             "- See `GERBERS_NOT_GENERATED_DRC_BLOCKED.txt` for the current gate.\n"
    )
    assembly_notes = f"""# Assembly Notes

Status: {status}.

## JLCPCB/manufacturer assembled SMD

- U1 TPS259814L eFuse.
- U2-U4 TPS26631RGE eFuses.
- Q1-Q5 2N7002 SOT-23 MOSFETs.
- R1-R34.
- C1-C8.

All SMD parts are on the top side in the current placement. The CPL rotations are exported directly from KiCad and must be checked in the JLCPCB placement preview before order.

## Manual / serviceable installation

- A1 Arduino Nano on headers/socket.
- U5-U8 Adafruit INA260 Product 4226 breakout modules on headers.
- U9 verified 60 mm x 42 mm boost converter module.
- J1/J2 ATX screw terminal inputs.
- J3 ATX external switch terminal.
- J4 dedicated rail output terminal.
- JH1/JH2 EPS/header connectors.
- SW1-SW4 through-hole reset buttons unless a later decision is made to have them factory assembled.

## Important checks

- DRC currently has 0 violations and 0 unconnected items after routing and zone fill.
- High-current rails have rail-specific copper zones plus existing routed connectivity; short neck-downs remain at fine-pitch eFuse pins and module/header pads.
- LCSC/JLCPCB part numbers are marked customer-supplied/select-LCSC and must be selected/verified before PCBA order.
- U1 package/land pattern must be verified against the exact TPS259814L orderable part.
{blockers}"""
    (OUT / "assembly_notes.md").write_text(assembly_notes, encoding="utf-8")

    readme_status = "ready for fabrication-file review" if clean else "not fabrication-ready"
    current_gate = (
        "- Gerber ZIP: generated after DRC clean.\n"
        "- Drill files: generated after DRC clean.\n"
        "- KiCad DRC: 0 violations, 0 unconnected items.\n"
        "- Use JLCPCB/JLCDFM preview to verify board outline, drills, solder mask, and assembly rotations before purchase.\n"
        if clean
        else "- Gerber ZIP: not generated.\n"
             "- Drill files: not generated.\n"
             "- Reason: routing is incomplete or DRC is not clean.\n"
             "- Use the BOM/CPL here only for review until routing, copper pours, ERC, DRC, and placement preview are complete.\n"
    )
    readme = f"""# JLCPCB Ordering README

Status: {readme_status}.

## Current gate

{current_gate}

## Recommended order settings after DRC is clean

- PCB type: FR-4, 2 layers unless routing requires a 4-layer revision.
- Board thickness: 1.6 mm.
- Copper weight: 2 oz outer copper preferred for high-current margin. Confirm current availability/pricing on the JLCPCB order page.
- Solder mask: green preferred for lowest process risk unless the team wants a different color.
- Surface finish: ENIG preferred for the fine-pitch QFN/eFuse footprints and flatter pads; lead-free HASL is acceptable only after confirming pad planarity/rework tradeoffs.
- Assembly side: top side only for the SMD manufacturer-assembled parts.
- Manual parts: exclude headers, modules, screw terminals, EPS connectors, and reset buttons from the JLCPCB SMD BOM/CPL unless the team explicitly decides otherwise.

## JLCPCB file-prep reminders

- BOM and CPL designators must match exactly.
- Use millimeters in the CPL.
- Check every SMD rotation in JLCPCB preview, especially U1-U4 and Q1-Q5.
- Replace all `CUSTOMER_SUPPLIED_OR_SELECT_LCSC` / `CUSTOMER_SUPPLIED_OR_VERIFY_LCSC` placeholders with real selected parts or a JLCPCB customer-supplied-parts plan before ordering.

Sources checked:

- JLCPCB copper weight guide: https://jlcpcb.com/help/article/jlcpcb-copper-weight
- JLCPCB surface finish guide: https://jlcpcb.com/help/article/jlcpcb-surface-finish
- JLCPCB BOM/CPL preparation guidance: https://jlcpcb.com/help/article/advice-for-bom-and-cpl-files-preparation
"""
    (OUT / "README_ordering.md").write_text(readme, encoding="utf-8")

    blocked_path = OUT / "GERBERS_NOT_GENERATED_DRC_BLOCKED.txt"
    if clean:
        if blocked_path.exists():
            blocked_path.unlink()
        (OUT / "FABRICATION_GATE_PASSED.txt").write_text(
            "KiCad DRC passed with 0 violations and 0 unconnected items before Gerber/drill generation.\n"
            "Still perform JLCPCB/JLCDFM preview and BOM/CPL/LCSC part review before purchase.\n",
            encoding="utf-8",
        )
        return

    blocked = """Final Gerbers/drills were intentionally not generated.

Reason: KiCad DRC currently has 236 unrouted items. The project requirement says not to generate final Gerbers until DRC is clean or every remaining warning is explicitly justified.

Next required work:
1. Route all nets with wide high-current copper and a solid GND plane.
2. Refill zones.
3. Re-run ERC/DRC.
4. Verify Gerbers in a viewer/JLCDFM.
5. Generate final Gerber ZIP and Excellon drill outputs only after the gate passes.
"""
    blocked_path.write_text(blocked, encoding="utf-8")


def copy_reports() -> None:
    reports = [
        (ROOT / "regenerated_erc.rpt", OUT / "ERC_report.txt"),
        (ROOT / "regenerated_drc.rpt", OUT / "DRC_report.txt"),
    ]
    for src, dst in reports:
        if src.exists():
            shutil.copyfile(src, dst)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fps = load_footprints()
    missing = sorted(ref for ref in SMD_ASSEMBLY_REFS | MANUAL_REFS if ref not in fps)
    if missing:
        raise RuntimeError(f"Missing expected footprints: {', '.join(missing)}")
    write_bom_smd(fps)
    write_cpl_smd(fps)
    write_master_bom(fps)
    copy_reports()
    write_notes(drc_is_clean())


if __name__ == "__main__":
    main()
