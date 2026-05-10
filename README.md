# Power Testing Board

Compact CubeSat EPS ground power-test board for ATX/boost-supplied rails.

## Current Design State

- Root KiCad project: `Power Testing board.kicad_pro`
- Schematic was regenerated first in `Power Testing board.kicad_sch`.
- Serviceable PCB placement was generated in `Power Testing board.kicad_pcb`.
- Board outline is 230 mm x 170 mm.
- PCB is routed with rail-specific copper zones, a solid B.Cu GND plane, and final JLCPCB fabrication outputs in `fabrication/JLCPCB/`.

## Electrical Architecture

Each rail follows the required order:

`RAW input -> eFuse -> INA260 VIN+ -> INA260 VIN- -> protected output distribution`

Protected outputs then split to the dedicated output terminal and the selected EPS/H1/H2 power pins. The INA260 VIN- node is the downstream positive rail, not ground.

Rails:

- `+3V3_RAW -> TPS259814L -> U5 INA260 -> +3V3_PROTECTED`
- `+5V_RAW -> TPS26631RGE -> U6 INA260 -> +5V_PROTECTED`
- `+12V_RAW -> TPS26631RGE -> U7 INA260 -> +12V_PROTECTED`
- `+16V8_RAW -> TPS26631RGE -> U8 INA260 -> +16V8_PROTECTED`

## GitHub Portability

The project includes repo-local libraries so another computer can open it after cloning:

- `Power_Testing_Board.kicad_sym`
- `Power_Testing_Board.pretty/`
- `sym-lib-table`
- `fp-lib-table`

Keep those files committed with the KiCad project. Do not rely on absolute local library paths for the custom INA260 or boost module footprints.

## Verification Notes

- ERC: 0 errors, 11 warnings. Remaining warnings are isolated optional status labels such as PG, IMON, and ALERT.
- DRC: 0 violations, 0 unconnected items after routing and zone refill.
- Gerbers/drills are generated in `fabrication/JLCPCB/` after the clean DRC gate.
- Boost footprint is based on the supplied Amazon screenshots and has been physically verified: 60 mm x 42 mm x 20 mm.
- TPS259814L footprint is marked for package/land-pattern verification against the exact ordered part.
- eFuses are on the main PCB for compactness. If repairability becomes more important than board area, move each eFuse circuit to a plug-in daughterboard.
- Passive component purposes, design checks, test point map, and assembly notes are documented in `docs/passive_component_purpose_table.md`.

## Before Ordering

- Review the Gerber ZIP and drill files in JLCPCB/JLCDFM before purchase.
- Use 2 oz copper as documented in `fabrication/JLCPCB/README_ordering.md`.
- Verify ATX, EPS/H1/H2, output terminal, boost module, INA260 module, and eFuse footprints against the physical parts.
- Select/verify the LCSC or customer-supplied plan for all SMD BOM entries before placing the PCBA order.
