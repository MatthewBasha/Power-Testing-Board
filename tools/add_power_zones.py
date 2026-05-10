from __future__ import annotations

from pathlib import Path

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
PCB = ROOT / "Power Testing board.kicad_pcb"
MM = 1_000_000


def v(x: float, y: float) -> pcbnew.VECTOR2I:
    return pcbnew.VECTOR2I(int(x * MM), int(y * MM))


def add_zone(
    board: pcbnew.BOARD,
    netname: str,
    layer: int,
    points: list[tuple[float, float]],
    *,
    clearance: float = 0.3,
    priority: int = 10,
    full_pad_connection: bool = True,
) -> None:
    zone = pcbnew.ZONE(board)
    zone.SetLayer(layer)
    zone.SetNetCode(board.FindNet(netname).GetNetCode())
    zone.SetAssignedPriority(priority)
    zone.SetLocalClearance(int(clearance * MM))
    zone.SetMinThickness(int(0.25 * MM))
    zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL if full_pad_connection else pcbnew.ZONE_CONNECTION_THERMAL)
    if not full_pad_connection:
        zone.SetThermalReliefGap(int(0.25 * MM))
        zone.SetThermalReliefSpokeWidth(int(0.5 * MM))
    for x, y in points:
        zone.AppendCorner(v(x, y), -1)
    board.Add(zone)


def main() -> None:
    board = pcbnew.LoadBoard(str(PCB))
    for zone in list(board.Zones()):
        board.Remove(zone)

    add_zone(
        board,
        "GND",
        pcbnew.B_Cu,
        [(0.8, 0.8), (229.2, 0.8), (229.2, 169.2), (0.8, 169.2)],
        clearance=0.3,
        priority=0,
        full_pad_connection=True,
    )

    # Raw/input copper corridors. Fine-pitch eFuse pins still require short neck-downs;
    # these pours add the bulk copper for the ATX/module-to-eFuse current paths.
    add_zone(board, "+3V3_RAW", pcbnew.F_Cu, [(6, 65), (28, 65), (28, 36), (86, 36), (86, 45), (36, 45), (36, 75), (6, 75)], priority=20)
    add_zone(board, "+5V_RAW", pcbnew.B_Cu, [(6, 54), (45, 54), (45, 65), (86, 65), (86, 74), (36, 74), (36, 65), (6, 65)], priority=20)
    add_zone(board, "+12V_RAW", pcbnew.F_Cu, [(6, 45), (24, 45), (24, 93), (80, 93), (80, 104), (178, 104), (178, 116), (76, 116), (76, 104), (36, 104), (36, 55), (6, 55)], priority=20)
    add_zone(board, "+16V8_RAW", pcbnew.B_Cu, [(78, 112), (228, 112), (228, 126), (90, 126), (90, 134), (78, 134)], priority=20)

    # eFuse OUT to INA260 VIN+ copper corridors.
    add_zone(board, "+3V3_EFUSE_OUT", pcbnew.F_Cu, [(82, 31), (112, 31), (112, 50), (82, 50)], priority=25)
    add_zone(board, "+5V_EFUSE_OUT", pcbnew.F_Cu, [(82, 61), (112, 61), (112, 80), (82, 80)], priority=25)
    add_zone(board, "+12V_EFUSE_OUT", pcbnew.B_Cu, [(82, 91), (112, 91), (112, 110), (82, 110)], priority=25)
    add_zone(board, "+16V8_EFUSE_OUT", pcbnew.F_Cu, [(82, 121), (112, 121), (112, 140), (82, 140)], priority=25)

    # Protected output distribution pours to the dedicated connector and EPS power pins.
    add_zone(board, "+3V3_PROTECTED", pcbnew.F_Cu, [(112, 45), (224, 45), (224, 55), (180, 55), (180, 80), (150, 80), (150, 72), (170, 72), (170, 55), (112, 55)], priority=15)
    add_zone(board, "+5V_PROTECTED", pcbnew.B_Cu, [(112, 72), (180, 72), (180, 46), (224, 46), (224, 36), (172, 36), (172, 82), (112, 82)], priority=15)
    add_zone(board, "+12V_PROTECTED", pcbnew.F_Cu, [(112, 102), (150, 102), (150, 78), (162, 78), (162, 36), (224, 36), (224, 27), (152, 27), (152, 78), (112, 102)], priority=15)
    add_zone(board, "+16V8_PROTECTED", pcbnew.B_Cu, [(112, 132), (180, 132), (180, 72), (224, 72), (224, 17), (172, 17), (172, 72), (112, 132)], priority=15)

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(PCB), board)


if __name__ == "__main__":
    main()
