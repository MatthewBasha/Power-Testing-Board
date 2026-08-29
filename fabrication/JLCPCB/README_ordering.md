# JLCPCB Ordering README

Status: ready for fabrication-file review.

## Current gate

- Gerber ZIP: generated after DRC clean.
- Drill files: generated after DRC clean.
- KiCad DRC: 0 violations, 0 unconnected items.
- Use JLCPCB/JLCDFM preview to verify board outline, drills, solder mask, and assembly rotations before purchase.


## Recommended 4-layer order settings after DRC is clean

- PCB type: FR-4, 4 layers.
- Board thickness: 1.6 mm.
- Stackup intent: L1/F.Cu components, high-current routing/pours, local signals; L2/In1.Cu solid uninterrupted GND reference; L3/In2.Cu power-distribution planes/zones; L4/B.Cu signals and secondary GND fill.
- Copper weight: 2 oz outer copper preferred for high-current margin. Inner copper can remain JLCPCB default 0.5 oz unless price/availability allows 1 oz or 2 oz inner copper for the selected 4-layer stackup.
- If selecting 2 oz inner copper, verify the current JLCPCB order-page availability and required stackup before purchase; JLCPCB notes inner-layer copper options vary by layer count, thickness, and stackup.
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
