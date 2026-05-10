# Assembly Notes

Status: ready for JLCPCB fabrication output review.

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
- No KiCad DRC or unconnected-net blockers remain.
- Final external JLCPCB/JLCDFM preview and LCSC/customer-supplied part selection still need human review before purchase.
