# Passive Component Purpose Table

Generated from the current root KiCad design in `E:\Power-Testing-Board`.

## Summary

- Resistors in schematic: R1-R34.
- Capacitors in schematic: C1-C8.
- No extra main-board I2C pullup resistors are currently fitted. The Adafruit INA260 Product 4226 breakout has onboard 10 kOhm SDA and SCL pullups, so four installed breakouts make an effective pullup of about 2.5 kOhm to `+ARDUINO_5V`.
- No main-board capacitors or resistors are placed specifically at the INA260 breakout headers. The INA260 boards are treated as complete modules with their own onboard support components.
- TPS26631 `dVdT`, `MODE`, `B_GATE`, `DRV`, and `PGTH` are intentionally left open/no-connect in this design state. `MODE` open is used for latch-off behavior per the design requirement.
- TPS259814L `DVDT` and `ITIMER` are intentionally left open/no-connect for fastest startup and fastest overcurrent response unless a delay is intentionally added later.
- TPS26631 `PGOOD`/`IMON` and TPS259814L `PG` labels are optional one-pin status nets right now. They are not pulled up or routed to test points yet except for `FLT`, which is pulled up and test-pointed.

## Capacitors

| Ref | Value | Footprint | Connected nets | Supports | Purpose | Status | Datasheet section or design reason | Value source |
|---|---:|---|---|---|---|---|---|---|
| C1 | 1 uF | C_0805_2012Metric | `+3V3_RAW` to `GND` | U1 TPS259814L | Local input bypass at 3.3 V eFuse input. | Required | TI TPS25981 application/layout guidance: keep input bypass close to IN/GND. | Estimated starting value from eFuse bypass practice; verify with final TI design review. |
| C2 | 10 uF | C_0805_2012Metric | `+3V3_EFUSE_OUT` to `GND` | U1 TPS259814L and U5 INA260 input side | Local output/load-side capacitance before the INA260 module. | Required | TI TPS25981 application/layout guidance for output capacitance and transient load support. | Estimated starting value; verify output cap limits and load profile. |
| C3 | 1 uF | C_0805_2012Metric | `+5V_RAW` to `GND` | U2 TPS26631 | Local input bypass at 5 V eFuse input. | Required | TI TPS2663 application/layout guidance: input capacitor close to IN/GND. | Estimated starting value; verify with TPS2663 datasheet/reference design. |
| C4 | 10 uF | C_0805_2012Metric | `+5V_EFUSE_OUT` to `GND` | U2 TPS26631 and U6 INA260 input side | Local output/load-side capacitance before the INA260 module. | Required | TI TPS2663 output capacitance/load transient guidance. | Estimated starting value; verify output cap/inrush behavior. |
| C5 | 1 uF | C_0805_2012Metric | `+12V_RAW` to `GND` | U3 TPS26631 | Local input bypass at 12 V eFuse input. | Required | TI TPS2663 application/layout guidance: input capacitor close to IN/GND. | Estimated starting value; verify voltage rating and derating. |
| C6 | 10 uF | C_0805_2012Metric | `+12V_EFUSE_OUT` to `GND` | U3 TPS26631 and U7 INA260 input side | Local output/load-side capacitance before the INA260 module. | Required | TI TPS2663 output capacitance/load transient guidance. | Estimated starting value; verify voltage rating and inrush behavior. |
| C7 | 1 uF | C_0805_2012Metric | `+16V8_RAW` to `GND` | U4 TPS26631 | Local input bypass at 16.8 V eFuse input. | Required | TI TPS2663 application/layout guidance: input capacitor close to IN/GND. | Estimated starting value; verify voltage rating and derating. |
| C8 | 10 uF | C_0805_2012Metric | `+16V8_EFUSE_OUT` to `GND` | U4 TPS26631 and U8 INA260 input side | Local output/load-side capacitance before the INA260 module. | Required | TI TPS2663 output capacitance/load transient guidance. | Estimated starting value; verify voltage rating and inrush behavior. |

## Resistors

| Ref | Value | Footprint | Connected nets | Supports | Purpose | Status | Datasheet section or design reason | Value source |
|---|---:|---|---|---|---|---|---|---|
| R1 | 1.10 kOhm 1% | R_0805_2012Metric | `ILIM_3V3` to `GND` | U1 TPS259814L | Sets 3.3 V eFuse current limit near 6 A. | Required | TI TPS25981 ILM/current-limit programming. | User requirement; calculated/selected for about 6 A. |
| R2 | 100 kOhm | R_0603_1608Metric | `+3V3_RAW` to `RESET_3V3` | U1 TPS259814L EN/UVLO | Top resistor of EN/UVLO divider; normally enables U1. | Required | TI TPS25981 EN/UVLO divider guidance. | User suggested starting divider; estimated. |
| R3 | 100 kOhm | R_0603_1608Metric | `RESET_3V3` to `GND` | U1 TPS259814L EN/UVLO | Bottom resistor of EN/UVLO divider and reset node bias. | Required | TI TPS25981 EN/UVLO divider guidance. | User suggested starting divider; estimated. |
| R4 | 24.9 kOhm | R_0603_1608Metric | `+3V3_RAW` to `OVLO_3V3` | U1 TPS259814L EN/OVLO | Top resistor of 3.3 V OVLO divider. | Required | TI TPS25981 EN/OVLO divider guidance. | User suggested value targeting about 4.1 V to 4.3 V OV trip. |
| R5 | 10 kOhm | R_0603_1608Metric | `OVLO_3V3` to `GND` | U1 TPS259814L EN/OVLO | Bottom resistor of 3.3 V OVLO divider. | Required | TI TPS25981 EN/OVLO divider guidance. | User suggested value targeting about 4.1 V to 4.3 V OV trip. |
| R6 | 330 Ohm | R_0603_1608Metric | `ARD_RESET_3V3` to `GATE_3V3` | Q1 2N7002 / U1 reset | Arduino-to-gate series resistor for open-drain reset pull-down. | Required if Arduino reset control is populated | GPIO protection/gate damping design practice. | Estimated standard value. |
| R7 | 100 kOhm | R_0603_1608Metric | `GATE_3V3` to `GND` | Q1 2N7002 / U1 reset | Holds reset MOSFET off while Arduino is reset/unpowered. | Required | Gate pulldown design practice. | Estimated standard value. |
| R8 | 10 kOhm | R_0603_1608Metric | `FLT_3V3` to `+ARDUINO_5V` | U1 TPS259814L FLT | Pulls open-drain fault output to Arduino logic. | Required if FLT_3V3 is used; DNP if fault status is unused | TI TPS25981 FLT/open-drain status usage. | Estimated standard pullup value. |
| R9 | 3.00 kOhm 1% | R_0805_2012Metric | `ILIM_5V` to `GND` | U2 TPS26631 | Sets 5 V eFuse current limit near 6 A. | Required | TI TPS2663 ILIM/current-limit programming. | User requirement; copied from requested value. |
| R10 | 249 kOhm | R_0603_1608Metric | `+5V_RAW` to `UVLO_5V` | U2 TPS26631 UVLO | Top resistor of 5 V UVLO divider. | Required, but value must be reviewed | TI TPS2663 UVLO divider guidance. | Estimated starting value; flag for recalculation. |
| R11 | 100 kOhm | R_0603_1608Metric | `UVLO_5V` to `GND` | U2 TPS26631 UVLO | Bottom resistor of 5 V UVLO divider. | Required, but value must be reviewed | TI TPS2663 UVLO divider guidance. | Estimated starting value; flag for recalculation. |
| R12 | 402 kOhm | R_0603_1608Metric | `+5V_RAW` to `OVP_5V` | U2 TPS26631 OVP | Top resistor of 5 V OVP divider. | Required, but value must be reviewed | TI TPS2663 OVP divider guidance. | Estimated starting value; flag for recalculation. |
| R13 | 100 kOhm | R_0603_1608Metric | `OVP_5V` to `GND` | U2 TPS26631 OVP | Bottom resistor of 5 V OVP divider. | Required, but value must be reviewed | TI TPS2663 OVP divider guidance. | Estimated starting value; flag for recalculation. |
| R14 | 330 Ohm | R_0603_1608Metric | `ARD_RESET_5V` to `GATE_5V` | Q2 2N7002 / U2 SHDN | Arduino-to-gate series resistor for 5 V reset pull-down. | Required if Arduino reset control is populated | GPIO protection/gate damping design practice. | Estimated standard value. |
| R15 | 100 kOhm | R_0603_1608Metric | `GATE_5V` to `GND` | Q2 2N7002 / U2 SHDN | Holds reset MOSFET off while Arduino is reset/unpowered. | Required | Gate pulldown design practice. | Estimated standard value. |
| R16 | 10 kOhm | R_0603_1608Metric | `FLT_5V` to `+ARDUINO_5V` | U2 TPS26631 FLT | Pulls open-drain fault output to Arduino logic. | Required if FLT_5V is used; DNP if fault status is unused | TI TPS2663 FLT/open-drain status usage. | Estimated standard pullup value. |
| R17 | 3.00 kOhm 1% | R_0805_2012Metric | `ILIM_12V` to `GND` | U3 TPS26631 | Sets 12 V eFuse current limit near 6 A. | Required | TI TPS2663 ILIM/current-limit programming. | User requirement; copied from requested value. |
| R18 | 649 kOhm | R_0603_1608Metric | `+12V_RAW` to `UVLO_12V` | U3 TPS26631 UVLO | Top resistor of 12 V UVLO divider. | Required, but value must be reviewed | TI TPS2663 UVLO divider guidance. | Estimated starting value; flag for recalculation. |
| R19 | 100 kOhm | R_0603_1608Metric | `UVLO_12V` to `GND` | U3 TPS26631 UVLO | Bottom resistor of 12 V UVLO divider. | Required, but value must be reviewed | TI TPS2663 UVLO divider guidance. | Estimated starting value; flag for recalculation. |
| R20 | 1.15 MOhm | R_0603_1608Metric | `+12V_RAW` to `OVP_12V` | U3 TPS26631 OVP | Top resistor of 12 V OVP divider. | Required, but value must be reviewed | TI TPS2663 OVP divider guidance. | Estimated starting value; flag for recalculation. |
| R21 | 100 kOhm | R_0603_1608Metric | `OVP_12V` to `GND` | U3 TPS26631 OVP | Bottom resistor of 12 V OVP divider. | Required, but value must be reviewed | TI TPS2663 OVP divider guidance. | Estimated starting value; flag for recalculation. |
| R22 | 330 Ohm | R_0603_1608Metric | `ARD_RESET_12V` to `GATE_12V` | Q3 2N7002 / U3 SHDN | Arduino-to-gate series resistor for 12 V reset pull-down. | Required if Arduino reset control is populated | GPIO protection/gate damping design practice. | Estimated standard value. |
| R23 | 100 kOhm | R_0603_1608Metric | `GATE_12V` to `GND` | Q3 2N7002 / U3 SHDN | Holds reset MOSFET off while Arduino is reset/unpowered. | Required | Gate pulldown design practice. | Estimated standard value. |
| R24 | 10 kOhm | R_0603_1608Metric | `FLT_12V` to `+ARDUINO_5V` | U3 TPS26631 FLT | Pulls open-drain fault output to Arduino logic. | Required if FLT_12V is used; DNP if fault status is unused | TI TPS2663 FLT/open-drain status usage. | Estimated standard pullup value. |
| R25 | 3.00 kOhm 1% | R_0805_2012Metric | `ILIM_16V8` to `GND` | U4 TPS26631 | Sets 16.8 V eFuse current limit near 6 A. | Required | TI TPS2663 ILIM/current-limit programming. | User requirement; copied from requested value. |
| R26 | 976 kOhm | R_0603_1608Metric | `+16V8_RAW` to `UVLO_16V8` | U4 TPS26631 UVLO | Top resistor of 16.8 V UVLO divider. | Required, but value must be reviewed | TI TPS2663 UVLO divider guidance. | Estimated starting value; flag for recalculation. |
| R27 | 100 kOhm | R_0603_1608Metric | `UVLO_16V8` to `GND` | U4 TPS26631 UVLO | Bottom resistor of 16.8 V UVLO divider. | Required, but value must be reviewed | TI TPS2663 UVLO divider guidance. | Estimated starting value; flag for recalculation. |
| R28 | 1.50 MOhm | R_0603_1608Metric | `+16V8_RAW` to `OVP_16V8` | U4 TPS26631 OVP | Top resistor of 16.8 V OVP divider. | Required, but value must be reviewed | TI TPS2663 OVP divider guidance. | Estimated starting value; flag for recalculation. |
| R29 | 100 kOhm | R_0603_1608Metric | `OVP_16V8` to `GND` | U4 TPS26631 OVP | Bottom resistor of 16.8 V OVP divider. | Required, but value must be reviewed | TI TPS2663 OVP divider guidance. | Estimated starting value; flag for recalculation. |
| R30 | 330 Ohm | R_0603_1608Metric | `ARD_RESET_16V8` to `GATE_16V8` | Q4 2N7002 / U4 SHDN | Arduino-to-gate series resistor for 16.8 V reset pull-down. | Required if Arduino reset control is populated | GPIO protection/gate damping design practice. | Estimated standard value. |
| R31 | 100 kOhm | R_0603_1608Metric | `GATE_16V8` to `GND` | Q4 2N7002 / U4 SHDN | Holds reset MOSFET off while Arduino is reset/unpowered. | Required | Gate pulldown design practice. | Estimated standard value. |
| R32 | 10 kOhm | R_0603_1608Metric | `FLT_16V8` to `+ARDUINO_5V` | U4 TPS26631 FLT | Pulls open-drain fault output to Arduino logic. | Required if FLT_16V8 is used; DNP if fault status is unused | TI TPS2663 FLT/open-drain status usage. | Estimated standard pullup value. |
| R33 | 330 Ohm | R_0603_1608Metric | `ATX_PS_ON_CTL` to `GATE_PS_ON` | Q5 2N7002 / ATX PS_ON# | Arduino-to-gate series resistor for ATX PS_ON# open-drain pull-down. | Required if Arduino PS_ON control is populated | GPIO protection/gate damping design practice. | Estimated standard value. |
| R34 | 100 kOhm | R_0603_1608Metric | `GATE_PS_ON` to `GND` | Q5 2N7002 / ATX PS_ON# | Holds ATX PS_ON MOSFET off while Arduino is reset/unpowered. | Required | Gate pulldown design practice. | Estimated standard value. |

## Flagged Guesses / Values To Recalculate

The following were added as estimated starting values and should be reviewed before fabrication:

- TPS26631 UVLO and OVP dividers: R10-R13, R18-R21, R26-R29.
- eFuse input/output capacitor values: C1-C8.
- MOSFET gate series resistors and pulldowns: R6-R7, R14-R15, R22-R23, R30-R31, R33-R34.
- FLT pullups: R8, R16, R24, R32.

The current-limit resistors are not 8 A settings:

- U1 TPS259814L: R1 = 1.10 kOhm for about 6 A.
- U2/U3/U4 TPS26631: R9/R17/R25 = 3.00 kOhm 1% for about 6 A.

## Design Checks Before Routing/Fabrication

| Check | Result |
|---|---|
| Rail order on every rail | Confirmed in PCB net assignment: RAW -> eFuse -> INA260 VIN+ -> INA260 VIN- -> protected node. |
| eFuse before INA260 | Confirmed for +3.3 V, +5 V, +12 V, and +16.8 V. |
| INA260 measures protected load power | Confirmed: dedicated outputs and EPS/header pins use only the `+RAIL_PROTECTED` nets after INA260 VIN-. |
| INA260 VIN- never tied to GND | Confirmed: U5-U8 pad 8 nets are `+3V3_PROTECTED`, `+5V_PROTECTED`, `+12V_PROTECTED`, and `+16V8_PROTECTED`. |
| Dedicated output and EPS/header included in measurement | Confirmed: J4 and H1/H2 selected power pins branch from protected post-INA260 nets. |
| Common ground | Confirmed by shared `GND` net for ATX, Arduino, INA260 modules, eFuses, boost module, and outputs. |
| Current-limit target | Confirmed near 6 A by R1/R9/R17/R25; board copper/connectors still need 8 A to 10 A routing margin. |
| ATX input connector style | Confirmed screw terminals J1/J2, not a 24-pin ATX motherboard connector. |
| ATX PS_ON# control | Confirmed: green-wire `ATX_PS_ON_N` enters J2, external switch J3 shorts it to GND, Arduino pulls low through Q5 only. |
| Reset buttons | Confirmed SW1-SW4 are momentary through-hole buttons on an edge row, pulling each reset/control node low. |
| Arduino Nano orientation | Confirmed: A1 uses `Module:Arduino_Nano`, is header-mounted, rotated 90 degrees; KiCad USB marker is placed toward the left board edge. |
| Modularity | Confirmed for Arduino headers, INA260 module headers, verified boost module footprint, ATX terminals, output terminals, EPS headers, and through-hole buttons. |
| SMD eFuse serviceability | Manufacturer-assembled SMD; placed on main PCB with nearby passives/test points, not under the plug-in modules. |
| High-current layout | Not complete. Must be routed with wide pours/traces, 2 oz copper preferred, via arrays for layer changes, solid GND plane, short eFuse-to-INA260 current path, and thermal via stitching. |
| Test points | Confirmed TP1-TP29 cover all requested rail states, GND, I2C, ATX control/status, reset, FLT, and boost input/output/GND. |
| Connector footprints | Present for ATX screw terminals, verified boost module, Adafruit INA260 modules, Arduino Nano, dedicated outputs, H1/H2 EPS headers, and reset buttons. Final physical current-rating review still required. |

## Test Point Map

| Net/function | Test point |
|---|---|
| `+3V3_RAW` | TP1 |
| `+3V3_EFUSE_OUT` | TP2 |
| `+3V3_PROTECTED` | TP3 |
| `+5V_RAW` | TP4 |
| `+5V_EFUSE_OUT` | TP5 |
| `+5V_PROTECTED` | TP6 |
| `+12V_RAW` | TP7 |
| `+12V_EFUSE_OUT` | TP8 |
| `+12V_PROTECTED` | TP9 |
| `+16V8_RAW` | TP10 |
| `+16V8_EFUSE_OUT` | TP11 |
| `+16V8_PROTECTED` | TP12 |
| `GND` | TP13 |
| `I2C_SDA` | TP14 |
| `I2C_SCL` | TP15 |
| `ATX_PS_ON_N` | TP16 |
| `ATX_PWR_OK` | TP17 |
| `+5VSB` | TP18 |
| `RESET_3V3` | TP19 |
| `RESET_5V` | TP20 |
| `RESET_12V` | TP21 |
| `RESET_16V8` | TP22 |
| `FLT_3V3` | TP23 |
| `FLT_5V` | TP24 |
| `FLT_12V` | TP25 |
| `FLT_16V8` | TP26 |
| `BOOST_IN+` / `+12V_RAW` | TP27 |
| `BOOST_OUT+` / `+16V8_RAW` | TP28 |
| `BOOST_GND` | TP29 |

## Assembly / BOM Notes

Manufacturer-assembled SMD:

- U1 TPS259814L eFuse.
- U2-U4 TPS26631RGE eFuses.
- Q1-Q5 2N7002 MOSFETs.
- R1-R34.
- C1-C8.
- SMD test pads are PCB features, not separate installed parts.

Manual / serviceable parts:

- A1 Arduino Nano installed on socket/header.
- U5-U8 Adafruit INA260 Product 4226 breakout boards installed on headers.
- U9 verified 60 mm x 42 mm boost converter module.
- J1/J2 ATX screw terminal inputs.
- J3 ATX external switch terminal.
- J4 dedicated rail output terminal block.
- JH1/JH2 EPS/header connectors.
- SW1-SW4 through-hole reset buttons.

## Current ERC/DRC Status

- ERC: 0 errors, 11 warnings. Warnings are isolated optional labels for PG, IMON, and ALERT signals.
- DRC: not fabrication-ready. Remaining issues are unrouted connections plus silkscreen overlap/clip warnings.
- Before Gerbers: finish high-current routing/pours, clean silkscreen, rerun ERC/DRC, and document any remaining warnings individually.

## Source References

- TI TPS2663 datasheet/product page: https://www.ti.com/lit/gpn/TPS2663
- TI TPS25981 datasheet: https://www.ti.com/lit/ds/symlink/tps25981.pdf
- Adafruit INA260 Product 4226: https://www.adafruit.com/product/4226
- Adafruit INA260 pinouts and onboard I2C pullups: https://learn.adafruit.com/adafruit-ina260-current-voltage-power-sensor-breakout/pinouts
