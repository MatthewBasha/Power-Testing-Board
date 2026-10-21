# Power Testing Board

KiCad 10 project imported from the supplied `PTB1Schem1.kicad_sch` and
`PTB1Schem2.kicad_sch` on October 17, 2026.

Open **Power Testing board.kicad_pro** in KiCad. Its root schematic links to
both supplied sheets as pages 2 and 3. The PCB is a fresh, empty board awaiting
footprint assignment and layout.

## Import details

- The original wiring, positions, symbol shapes, pin definitions, and UUIDs are preserved.
- Duplicate references were made unique across the project: three repeated
  `J3` instances became `J4`, `J5`, and `J6`; `SW?` became `SW1`. Five repeated
  power-symbol references on sheet 2 were also renumbered.
- Symbol instance paths now point to this project's hierarchy, including stale
  source instances that previously pointed to another project name.
- `PTB_Imported.kicad_sym` contains all 13 embedded symbol definitions, including
  the customized INA260 module symbols. Keep it and `sym-lib-table` with the project.
- KiCad exports three schematic pages and a netlist containing all 16 physical
  components. There are 102 placed symbols including power symbols.
- Import metadata and reference changes are recorded in `import-report.json`.

## Electrical status

Initial KiCad ERC reports **81 errors and 31 warnings**. The report is saved as
`validation/initial-erc.json`. The remaining findings are 72 unconnected pins,
9 power inputs without a driver, 24 unconnected wire endpoints, 3 off-grid
endpoints, and 4 conflicts between net names. These findings need design review.
The supplied wiring has not been electrically corrected, and most footprints
still need assignment.

The previous board, fabrication outputs, project files, and source originals
were backed up outside this repository before replacement. The repository's Git
history is retained.

## KiCad MCP

The supplied KiCAD MCP Server v2.8.2 is installed locally and registered in
Codex as `kicad`. See `MCP-SETUP.md` for the installation and usage details.
