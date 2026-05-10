# Passive Component Purpose Table

Generated for the root KiCad design in `E:\Power-Testing-Board`.

## Status Summary

- Resistors in schematic: R1-R34.
- Capacitors in schematic: C1-C8.
- Current-limit target remains about 6 A, not 8 A.
- No extra main-board I2C pullups are fitted. The Adafruit INA260 Product 4226 breakouts include 10 kOhm pullups on SDA and SCL, so four installed modules make an effective pullup of about 2.5 kOhm to `+ARDUINO_5V`.
- No main-board passive parts are added at the INA260 breakout headers; the INA260 boards are treated as complete plug-in modules.
- TPS26631 `dVdT`, `MODE`, `B_GATE`, `DRV`, `PGTH`, and `IMON` support parts are not populated in this design state. `MODE` is intentionally open for latch-off behavior per the project requirement.
- TPS26631 `SHDN` is controlled only by reset button/open-drain MOSFET pulldown. Released `SHDN` is acceptable because the TPS2663 datasheet specifies an internal open-circuit SHDN voltage and a 2 V rising enable threshold.
- TPS259814L `DVDT` and `ITIMER` are intentionally open for fastest startup and fastest overcurrent response unless a delay is intentionally added later.
- TPS259814L `PG` and TPS26631 `PGOOD`/`IMON` labels remain optional one-pin status nets. `FLT` is pulled up to Arduino 5 V and routed/test-pointed.

## Calculation Notes

- TPS259814L current limit: TI gives `RILM = 6585 / ILIM`; at 6 A this is 1097.5 Ohm, so R1 = 1.10 kOhm 1%.
- TPS26631 current limit: TI electrical characteristics list RILIM = 3 kOhm for a 6 A typical overload current limit.
- UVLO/OVLO/OVP dividers use the 1.20 V typical rising threshold: `Vtrip = 1.20 V * (Rtop + Rbottom) / Rbottom`.
- TPS26631 UVLO/OVP is implemented here as two independent dividers instead of the datasheet's combined three-resistor ladder. The threshold equation is the same comparator ratio form; the divider currents remain well above pin leakage.
- MOSFET gate resistors are engineering-standard damping/current-limiting values. Gate pulldowns are engineering-standard fail-off bias values.
- eFuse capacitor values are explicitly accepted starting values, not load-transient calculations. They satisfy local bypass intent, but final transient/load validation should confirm whether larger bulk capacitance or TVS/Schottky protection is needed.

## Capacitors

| Ref | Value | Footprint/package | Connected nets | Supports | Purpose | Required / optional / DNP | Datasheet section or design reason | Value source |
|---|---:|---|---|---|---|---|---|---|
| C1 | 1 uF 25 V X7R | C_0805_2012Metric | `+3V3_RAW` to `GND` | U1 TPS259814L | Local input bypass at 3.3 V eFuse input. | Required | TPS25981 power-supply/transient guidance: local input ceramic bypass close to IN/GND. | Accepted starting value; voltage rating selected with margin. |
| C2 | 10 uF 25 V X7R | C_0805_2012Metric | `+3V3_EFUSE_OUT` to `GND` | U1 TPS259814L and U5 INA260 input side | Local OUT-side capacitance before the INA260 module. | Required | TPS25981 transient guidance calls for low-ESR capacitance close to OUT/GND for output transients. | Accepted starting value; verify with load transient testing. |
| C3 | 1 uF 25 V X7R | C_0805_2012Metric | `+5V_RAW` to `GND` | U2 TPS26631 | Local input bypass at 5 V eFuse input. | Required | TPS2663 recommends at least 0.1 uF IN_SYS-GND decoupling and at least 1 uF input capacitance for transient-prone applications. | Copied/accepted from TI guidance. |
| C4 | 10 uF 25 V X7R | C_0805_2012Metric | `+5V_EFUSE_OUT` to `GND` | U2 TPS26631 and U6 INA260 input side | Local OUT-side/load-side capacitance before the INA260 module. | Required | TPS2663 application figures include output capacitance; exact value depends on load/inrush. | Accepted starting value; verify inrush/transient behavior. |
| C5 | 1 uF 50 V X7R | C_0805_2012Metric | `+12V_RAW` to `GND` | U3 TPS26631 | Local input bypass at 12 V eFuse input. | Required | TPS2663 decoupling/transient guidance. | Copied/accepted from TI guidance; 50 V rating for derating. |
| C6 | 10 uF 50 V X7R | C_0805_2012Metric | `+12V_EFUSE_OUT` to `GND` | U3 TPS26631 and U7 INA260 input side | Local OUT-side/load-side capacitance before the INA260 module. | Required | TPS2663 application/output capacitance guidance. | Accepted starting value; verify inrush/transient behavior. |
| C7 | 1 uF 50 V X7R | C_0805_2012Metric | `+16V8_RAW` to `GND` | U4 TPS26631 | Local input bypass at 16.8 V eFuse input. | Required | TPS2663 decoupling/transient guidance. | Copied/accepted from TI guidance; 50 V rating for derating. |
| C8 | 10 uF 50 V X7R | C_0805_2012Metric | `+16V8_EFUSE_OUT` to `GND` | U4 TPS26631 and U8 INA260 input side | Local OUT-side/load-side capacitance before the INA260 module. | Required | TPS2663 application/output capacitance guidance. | Accepted starting value; verify inrush/transient behavior. |

## Resistors

| Ref | Value | Footprint/package | Connected nets | Supports | Purpose | Required / optional / DNP | Datasheet section or design reason | Value source |
|---|---:|---|---|---|---|---|---|---|
| R1 | 1.10 kOhm 1% | R_0805_2012Metric | `ILIM_3V3` to `GND` | U1 TPS259814L | Sets 3.3 V eFuse current limit near 6 A. | Required | TPS25981 ILM equation `RILM = 6585 / ILIM`. | Calculated: 6585 / 6 A = 1097.5 Ohm. |
| R2 | 100 kOhm 1% | R_0603_1608Metric | `+3V3_RAW` to `RESET_3V3` | U1 EN/UVLO | Top of EN/UVLO divider; normally enables U1. | Required | TPS25981 EN/UVLO divider equation. | Calculated/selected: with R3 gives 2.40 V rising UVLO. |
| R3 | 100 kOhm 1% | R_0603_1608Metric | `RESET_3V3` to `GND` | U1 EN/UVLO | Bottom of EN/UVLO divider and reset node bias. | Required | TPS25981 EN/UVLO divider equation. | Calculated/selected with R2. |
| R4 | 24.9 kOhm 1% | R_0603_1608Metric | `+3V3_RAW` to `OVLO_3V3` | U1 EN/OVLO | Top of 3.3 V OVLO divider. | Required | TPS25981 EN/OVLO divider equation. | Calculated: with R5 gives 4.19 V rising OVLO. |
| R5 | 10 kOhm 1% | R_0603_1608Metric | `OVLO_3V3` to `GND` | U1 EN/OVLO | Bottom of 3.3 V OVLO divider. | Required | TPS25981 EN/OVLO divider equation. | Calculated/selected with R4. |
| R6 | 330 Ohm | R_0603_1608Metric | `ARD_RESET_3V3` to `GATE_3V3` | Q1 / U1 reset | Arduino GPIO series gate resistor. | Required if Arduino reset is populated | Limits instantaneous GPIO/gate current and damps ringing. | Justified engineering-standard value. |
| R7 | 100 kOhm | R_0603_1608Metric | `GATE_3V3` to `GND` | Q1 / U1 reset | Holds reset MOSFET off while Arduino resets/unpowered. | Required | Fail-off MOSFET gate bias. | Justified engineering-standard value. |
| R8 | 10 kOhm | R_0603_1608Metric | `FLT_3V3` to `+ARDUINO_5V` | U1 FLT | Pulls open-drain fault output to Arduino logic. | Required if FLT is used; DNP if unused | TPS25981 FLT is open-drain; 10 kOhm gives about 0.5 mA sink at 5 V. | Justified/calculated pullup value. |
| R9 | 3.00 kOhm 1% | R_0805_2012Metric | `ILIM_5V` to `GND` | U2 TPS26631 | Sets 5 V current limit near 6 A. | Required | TPS2663 current-limit table: 3 kOhm gives 6 A typical. | Copied from datasheet/user requirement. |
| R10 | 261 kOhm 1% | R_0603_1608Metric | `+5V_RAW` to `UVLO_5V` | U2 UVLO | Top of 5 V UVLO divider. | Required | TPS2663 UVLO threshold 1.20 V typical. | Calculated: with R11 gives 4.33 V rising UVLO. |
| R11 | 100 kOhm 1% | R_0603_1608Metric | `UVLO_5V` to `GND` | U2 UVLO | Bottom of 5 V UVLO divider. | Required | TPS2663 UVLO divider design. | Calculated/selected with R10. |
| R12 | 383 kOhm 1% | R_0603_1608Metric | `+5V_RAW` to `OVP_5V` | U2 OVP | Top of 5 V OVP divider. | Required | TPS2663 OVP threshold 1.20 V typical. | Calculated: with R13 gives 5.80 V rising OVP. |
| R13 | 100 kOhm 1% | R_0603_1608Metric | `OVP_5V` to `GND` | U2 OVP | Bottom of 5 V OVP divider. | Required | TPS2663 OVP divider design. | Calculated/selected with R12. |
| R14 | 330 Ohm | R_0603_1608Metric | `ARD_RESET_5V` to `GATE_5V` | Q2 / U2 SHDN | Arduino GPIO series gate resistor. | Required if Arduino reset is populated | GPIO/gate damping and current limiting. | Justified engineering-standard value. |
| R15 | 100 kOhm | R_0603_1608Metric | `GATE_5V` to `GND` | Q2 / U2 SHDN | Holds reset MOSFET off while Arduino resets/unpowered. | Required | Fail-off MOSFET gate bias. | Justified engineering-standard value. |
| R16 | 10 kOhm | R_0603_1608Metric | `FLT_5V` to `+ARDUINO_5V` | U2 FLT | Pulls open-drain fault output to Arduino logic. | Required if FLT is used; DNP if unused | TPS2663 FLT is open-drain and may be left open if unused. | Justified/calculated: about 0.5 mA when asserted. |
| R17 | 3.00 kOhm 1% | R_0805_2012Metric | `ILIM_12V` to `GND` | U3 TPS26631 | Sets 12 V current limit near 6 A. | Required | TPS2663 current-limit table. | Copied from datasheet/user requirement. |
| R18 | 806 kOhm 1% | R_0603_1608Metric | `+12V_RAW` to `UVLO_12V` | U3 UVLO | Top of 12 V UVLO divider. | Required | TPS2663 UVLO threshold 1.20 V typical. | Calculated: with R19 gives 10.87 V rising UVLO. |
| R19 | 100 kOhm 1% | R_0603_1608Metric | `UVLO_12V` to `GND` | U3 UVLO | Bottom of 12 V UVLO divider. | Required | TPS2663 UVLO divider design. | Calculated/selected with R18. |
| R20 | 1.05 MOhm 1% | R_0603_1608Metric | `+12V_RAW` to `OVP_12V` | U3 OVP | Top of 12 V OVP divider. | Required | TPS2663 OVP threshold 1.20 V typical. | Calculated: with R21 gives 13.80 V rising OVP. |
| R21 | 100 kOhm 1% | R_0603_1608Metric | `OVP_12V` to `GND` | U3 OVP | Bottom of 12 V OVP divider. | Required | TPS2663 OVP divider design. | Calculated/selected with R20. |
| R22 | 330 Ohm | R_0603_1608Metric | `ARD_RESET_12V` to `GATE_12V` | Q3 / U3 SHDN | Arduino GPIO series gate resistor. | Required if Arduino reset is populated | GPIO/gate damping and current limiting. | Justified engineering-standard value. |
| R23 | 100 kOhm | R_0603_1608Metric | `GATE_12V` to `GND` | Q3 / U3 SHDN | Holds reset MOSFET off while Arduino resets/unpowered. | Required | Fail-off MOSFET gate bias. | Justified engineering-standard value. |
| R24 | 10 kOhm | R_0603_1608Metric | `FLT_12V` to `+ARDUINO_5V` | U3 FLT | Pulls open-drain fault output to Arduino logic. | Required if FLT is used; DNP if unused | TPS2663 FLT open-drain use. | Justified/calculated: about 0.5 mA when asserted. |
| R25 | 3.00 kOhm 1% | R_0805_2012Metric | `ILIM_16V8` to `GND` | U4 TPS26631 | Sets 16.8 V current limit near 6 A. | Required | TPS2663 current-limit table. | Copied from datasheet/user requirement. |
| R26 | 1.07 MOhm 1% | R_0603_1608Metric | `+16V8_RAW` to `UVLO_16V8` | U4 UVLO | Top of 16.8 V UVLO divider. | Required | TPS2663 UVLO threshold 1.20 V typical. | Calculated: with R27 gives 14.04 V rising UVLO. |
| R27 | 100 kOhm 1% | R_0603_1608Metric | `UVLO_16V8` to `GND` | U4 UVLO | Bottom of 16.8 V UVLO divider. | Required | TPS2663 UVLO divider design. | Calculated/selected with R26. |
| R28 | 1.40 MOhm 1% | R_0603_1608Metric | `+16V8_RAW` to `OVP_16V8` | U4 OVP | Top of 16.8 V OVP divider. | Required | TPS2663 OVP threshold 1.20 V typical. | Calculated: with R29 gives 18.00 V rising OVP. |
| R29 | 100 kOhm 1% | R_0603_1608Metric | `OVP_16V8` to `GND` | U4 OVP | Bottom of 16.8 V OVP divider. | Required | TPS2663 OVP divider design. | Calculated/selected with R28. |
| R30 | 330 Ohm | R_0603_1608Metric | `ARD_RESET_16V8` to `GATE_16V8` | Q4 / U4 SHDN | Arduino GPIO series gate resistor. | Required if Arduino reset is populated | GPIO/gate damping and current limiting. | Justified engineering-standard value. |
| R31 | 100 kOhm | R_0603_1608Metric | `GATE_16V8` to `GND` | Q4 / U4 SHDN | Holds reset MOSFET off while Arduino resets/unpowered. | Required | Fail-off MOSFET gate bias. | Justified engineering-standard value. |
| R32 | 10 kOhm | R_0603_1608Metric | `FLT_16V8` to `+ARDUINO_5V` | U4 FLT | Pulls open-drain fault output to Arduino logic. | Required if FLT is used; DNP if unused | TPS2663 FLT open-drain use. | Justified/calculated: about 0.5 mA when asserted. |
| R33 | 330 Ohm | R_0603_1608Metric | `ATX_PS_ON_CTL` to `GATE_PS_ON` | Q5 ATX PS_ON# | Arduino GPIO series gate resistor. | Required if Arduino PS_ON control is populated | GPIO/gate damping and current limiting. | Justified engineering-standard value. |
| R34 | 100 kOhm | R_0603_1608Metric | `GATE_PS_ON` to `GND` | Q5 ATX PS_ON# | Holds ATX PS_ON MOSFET off while Arduino resets/unpowered. | Required | Fail-off MOSFET gate bias. | Justified engineering-standard value. |

## Design Checks Before Routing/Fabrication

| Check | Result |
|---|---|
| Rail order on every rail | Confirmed in schematic/PCB net assignment: RAW -> eFuse -> INA260 VIN+ -> INA260 VIN- -> protected node. |
| eFuse before INA260 | Confirmed for +3.3 V, +5 V, +12 V, and +16.8 V. |
| INA260 measures protected load power | Confirmed: dedicated outputs and EPS/header pins use only the `+RAIL_PROTECTED` nets after INA260 VIN-. |
| INA260 VIN- never tied to GND | Confirmed: U5-U8 pad 8 nets are `+3V3_PROTECTED`, `+5V_PROTECTED`, `+12V_PROTECTED`, and `+16V8_PROTECTED`. |
| Dedicated output and EPS/header included in measurement | Confirmed: J4 and H1/H2 selected power pins branch from protected post-INA260 nets. |
| Common ground | Confirmed by shared `GND` net for ATX, Arduino, INA260 modules, eFuses, boost module, and outputs. |
| Current-limit target | Confirmed near 6 A by R1/R9/R17/R25; board copper/connectors still need 8 A to 10 A routing margin. |
| ATX input connector style | Confirmed screw terminals J1/J2, not a 24-pin ATX motherboard connector. |
| ATX PS_ON# control | Confirmed: green-wire `ATX_PS_ON_N` enters J2, external switch J3 shorts it to GND, Arduino pulls low through Q5 only. |
| Reset buttons | Confirmed SW1-SW4 are momentary through-hole buttons on an edge row, pulling each reset/control node low. |
| Arduino Nano orientation | Confirmed: A1 uses `Module:Arduino_Nano`, is header-mounted, rotated 90 degrees; USB is intended to face the left board edge. |
| Modularity | Confirmed for Arduino headers, INA260 module headers, verified boost module footprint, ATX terminals, output terminals, EPS headers, and through-hole buttons. |
| SMD eFuse serviceability | Manufacturer-assembled SMD; placed on main PCB with nearby passives/test points, not hidden under plug-in modules. |
| High-current layout | Not complete. Must be routed with wide pours/traces, 2 oz copper preferred, via arrays for layer changes, solid GND plane, short eFuse-to-INA260 current path, and thermal via stitching. |
| Test points | Confirmed TP1-TP29 cover requested rail states, GND, I2C, ATX control/status, reset, FLT, and boost input/output/GND. |
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

## Current ERC/DRC Status

- ERC: 0 errors, 11 warnings. Warnings are isolated optional labels for PG, IMON, and ALERT signals.
- DRC: 0 violations, 0 unconnected items after routing and copper-zone refill.
- Routing gate: passed. Final Gerbers/drills were generated after the clean DRC gate.

## Source References

- TI TPS2663 datasheet/product page: https://www.ti.com/lit/gpn/TPS2663
- TI TPS25981 datasheet: https://www.ti.com/lit/ds/symlink/tps25981.pdf
- Adafruit INA260 Product 4226: https://www.adafruit.com/product/4226
- Adafruit INA260 pinouts and onboard I2C pullups: https://learn.adafruit.com/adafruit-ina260-current-voltage-power-sensor-breakout/pinouts
