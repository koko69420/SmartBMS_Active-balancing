# Design Decisions Log

All default engineering decisions made during PCB partitioning, schematic remediation, interconnect definition, and PCB layout for the 16S LiFePO4 BMS and ESP32-C6 Gateway. Items requiring user sign-off prior to fabrication are also flagged in `FINAL_REPORT.md` under `NEEDS USER CONFIRMATION`.

## Phase 0: Toolchain, Copies, and Schematic Remediation

1. **Original Files Untouched**: All work operates strictly inside `16s_BMS_layout/` using copies of `16s_BMS/` (`reference_16s_BMS/`) and `esp32_gateway/`.
2. **Tasks 11, 12, 13 Verification**: Inspected original `16s_BMS` netlist and sheets; verified zero duplicate reference designators, renumbered Sheet 07 (`C80..C82, D50, J40, JP20, U16`) and Sheet 08 (`R150..R157`), Q22/Q23 high-side fan switch on Sheet 02, and J36/J37 CHG/DSG switches on Sheet 03 are already present.
3. **Sheet 02 Stray Trailing Blocks & Disconnected Inductors/Labels**:
   - Original `02_Power_Supply.kicad_sch` had two orphan symbol blocks (`Q_PMOS_GSD`, `2N7002`) appended after the root `(kicad_sch ...)` closing parenthesis, and 1.27 mm wire/label gaps leaving `L1`, `L2`, `L3` unconnected on one/both pins and `VPACK_F`, `+12V_EXT`, `FB12`, `FAN_12V` dangling.
   - Decision: On the layout copy `reference_16s_BMS/02_Power_Supply.kicad_sch`, truncated the stray trailing blocks, extended L1/L2/L3 endpoint wires by 1.27 mm to meet symbol pins, and snapped all 4 labels onto their wires. Net count cleanly converged from 253 to 246 with all 3 buck switchers (`U10`, `U11`, `U13`) wired properly.
4. **Sheet 08 Unnumbered Power Symbols**: Assigned `#PWR80`..`#PWR85` to the 6 `#PWR` symbols in `reference_16s_BMS/08_Precharge.kicad_sch` lines 2438-2499.
5. **Missing / Empty Footprints**:
   - `C_DRV1..C_DRV4` (`04_Current_Switching.kicad_sch`): Assigned `Capacitor_SMD:C_0805_2012Metric` (matching Sheet 04 decoupling capacitors).
   - `05_1_NTC_DIVIDER.kicad_sch`: Mapped legacy `HomeBus:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder` to standard `Resistor_SMD:R_0805_2012Metric`.
   - `J30` (`DD50_Female`, `16s_BMS.kicad_sch`): Created `custom_footprints:DD50_Placeholder` (standard 3-row 50-pin D-Sub spacing 2.77 x 2.84 mm, 1.0 mm drill / 1.70 mm pads, 2x 3.2 mm NPTH mounting holes at 61.11 mm spacing) clearly marked `PLACEHOLDER DD-50, REPLACE BEFORE FAB`.
   - `U1` (`esp32_gateway.kicad_sch`): Created `custom_footprints:ESP32-C6-DevKitC-1` with dual 1x16 headers spaced 22.86 mm apart at 2.54 mm pitch, 51.8 x 25.4 mm body outline, and antenna keepout marking. Verified pins 1..16 (left header J1, 3V3..NC) and pins 17..32 (right header J3, GND, TX, RX..NC) run top-to-bottom from antenna end to USB end per Espressif DevKitC-1 documentation.
   - `J3` (`esp32_gateway.kicad_sch`): Mapped `TerminalBlock:TerminalBlock_bornier-3_P5.08mm` to KiCad 10 standard `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal`.
   - `U4` (`B0509S-1WR3` in `esp32_gateway.kicad_sch`): Created `custom_footprints:Converter_DCDC_Mornsun_BxxxtS-1WR_THT` (SIP-4, 2.54 mm pitch, 11.6 x 6.0 mm body). Kept original schematic pin mapping unchanged and flagged the inverted pinout discrepancy (pins 1/2 and 3/4 swapped vs Mornsun B0509S-1WR3 datasheet) in `FINAL_REPORT.md` under `NEEDS USER CONFIRMATION`.
6. **MCU & Schematic Component Facts (Verified vs Assumptions)**:
   - Master BMS MCU `U20` is `CH32V203C8T6` (LQFP-48, RISC-V, WCH-LinkE debug `J10`), not STM32.
   - `U1` AFE (`BQ76952PFBR`) talks I2C (`/AFE_SCL`, `/AFE_SDA`, `/AFE_ALERT`) directly to MCU (`U20`) with pull-ups to `+3V3` (`R19`, `R20`, `R24`); there is no `ISO1640` IC in `16s_BMS`. Galvanic/ground-reference integrity is preserved by keeping `VSS` (star-tied via `NT2` to `SHUNT_BAT_SIDE` at Kelvin `J31`), `GND` (star-tied via `NT1` to `SHUNT_FET_SIDE` on `B2`), `FET_SOURCE_COMMON`, `ISO_GND`, and balancer opto inputs `BAL_*` strictly segregated (`>= 3 mm` clearance on shared PCBs).

## Phase 0B: Modular 6-Board Partition & Interconnects

7. **Root Component Placement**:
   - `J32` (`FROM SHUNT`), `J33` (`PACK MINUS`) assigned to **B1 (`bms_power`)** along with 2x M5 (5.3 mm drill, 10 mm pad) busbar terminals so either lug or busbar connection works.
   - `J34` (`PACK PLUS TAP`) assigned to **B2 (`bms_supply`)** so 58 V `/PACK_PLUS` feeds `F1` locally and never crosses any board-to-board cable.
   - `J30` (`DD50_Placeholder`), `J31` (`SHUNT KELVIN`), `NT2`, `NT3` assigned to **B4 (`bms_afe`)**.
8. **Interconnect Connectors (`INTERCONNECT.csv`)**:
   - Power & high-current reference ties (`X_SUP_PWR_GDRV` 1x02, `X_SUP_PWR_PWR` 2x02 with dual parallel `/SHUNT_FET_SIDE` pins for >= 4 A rating, `X_SUP_CTRL_PWR` 2x03 with dual `+3V3`/`GND`): `Molex Micro-Fit 3.0` vertical headers (3 A+ per pin).
   - Control, fan, I2C, AFE opto drive, isolated AFE logic power, mux control (`X_CTRL_SUP_FAN` 1x02, `X_CTRL_PWR_CTRL` 1x05, `X_AFE_PWR_CTRL` 1x04, `X_CTRL_AFE_PWR` 1x02, `X_AFE_CTRL_I2C` 1x04, `X_AFE_SENSE_PWR` 1x02, `X_CTRL_SENSE_MUX` 1x08): `JST XH` 2.50 mm vertical headers.
   - NTC analog harnesses (`X_AFE_SENSE_NTC1` 2x08, `X_AFE_SENSE_NTC2` 2x08): `IDC 2x08` 2.54 mm vertical headers.
9. **Layer Stack & Manufacturing Rules (All 6 Boards)**:
   - 2 layers (`F.Cu`, `B.Cu`), 1.6 mm FR4, 1 oz (35 um) copper, ENIG/HASL, 2.0 mm rounded outer corners, max 120 x 50 mm outline.
   - 4x M3 plated corner mounting holes (3.2 mm drill, 6.0 mm pad/keepout, left unnetted/mechanical) and 3x fiducials (1.0 mm copper, 2.0 mm solder mask opening) per side.
   - Isolation barriers `>= 3.0 mm` copper/silk keepout across all galvanic boundaries, with 1.0 mm milled `Edge.Cuts` slots only where pad geometry gives sufficient clearance (e.g. under `SOP-8_6.62x9.15mm` `ISO1050DUBR` on `G` and `B3`).
