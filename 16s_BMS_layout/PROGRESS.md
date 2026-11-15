# 16S BMS & ESP32-C6 Gateway Layout Progress

| Phase / Board | Description | Size (mm) | Comps | DRC Errors (Unconn / Short / Clear) | Status | Notes |
|---|---|---|---|---|---|---|
| Phase 0 | Toolchain, copies, schematic fixes, custom footprints | N/A | 299 + 32 | 0 GW err / 6 BMS metadata err | DONE | Fixed Sheet 02 L1-L3/FB12, Sheet 08 #PWR80..85, C_DRV1..4, DD50/ESP32/Mornsun footprints, netlist_reference.json |
| Phase 0B | INTERCONNECT.csv + 5 sub-board schematics & netlists | N/A | 5 sub-boards | Pending check | IN PROGRESS | Generating sub-board projects and verifying check_interconnect.py |
| Board G (`esp32_gateway`) | Isolated ESP32-C6 CAN-WiFi gateway | 90 x 50 | 32 | Pending | PENDING | Next after Phase 0B |
| Board B1 (`bms_power`) | 16 MOSFET high-current switching & precharge | 120 x 50 | 88 + X | Pending | PENDING | - |
| Board B4 (`bms_afe`) | BQ76952 AFE, cell filters, Kelvin shunt, DD-50 | 120 x 50 | 58 + X | Pending | PENDING | - |
| Board B2 (`bms_supply`) | 58V->12V/5V/3.3V bucks, isolated 12V gate supply, fan | 100 x 50 | 48 + X | Pending | PENDING | - |
| Board B3 (`bms_control`) | CH32V203C8T6 MCU, FRAM, isolated CAN `ISO1050DUBR` | 100 x 50 | 61 + X | Pending | PENDING | - |
| Board B5 (`bms_sense`) | 32 NTC dividers, dual 16-ch mux, 4x LTV-847S balancer optos | 110 x 50 | 44 + X | Pending | PENDING | - |
| Phase 8 | Cross-board verification, busbar calc, final report | N/A | All 6 | Pending | PENDING | - |
