# SmartBMS: 16S 100Ah 200A LiFePO4 Smart Battery Management System

[![Battery: 16S LiFePO4](https://img.shields.io/badge/Battery-16S%20LiFePO4%20(51.2V)-blue.svg?style=flat-square)](#system-specifications)
[![Current: 200A Continuous](https://img.shields.io/badge/Current-200A%20Continuous%20(16x%20IRFB4110)-red.svg?style=flat-square)](#high-power-solid-state-switch-stage)
[![AFE: TI BQ76952](https://img.shields.io/badge/AFE-TI%20BQ76952%20(16S%20Hardware%20Monitor)-darkgreen.svg?style=flat-square)](#analog-front-end-afe--battery-monitor)
[![Gate Drivers: Dual UCC27517](https://img.shields.io/badge/Gate%20Drivers-Dual%20TI%20UCC27517%20(4A%20Peak)-purple.svg?style=flat-square)](#high-power-solid-state-switch-stage)
[![Thermal: 32-Channel NTC](https://img.shields.io/badge/Thermal-32--Channel%20Dual%20CD74HC4067%20Multiplexed-orange.svg?style=flat-square)](#32-channel-temperature-sensing-matrix)
[![EDA: KiCad 9.0](https://img.shields.io/badge/EDA-KiCad%209.0-blueviolet.svg?style=flat-square)](#project-structure)

A high-current, modular, industrial-grade **16S 100Ah (200A continuous) LiFePO4 Smart Battery Management System (BMS)** engineered for stationary Home Energy Storage Systems (HESS), off-grid solar arrays, and high-capacity inverter battery banks.

Designed in KiCad 9.0 with a fully hierarchical architecture, this revision transitions the analog front-end to Texas Instruments' **BQ76952** 3S–16S autonomous battery monitor and protector IC, featuring a **16-MOSFET back-to-back common-source solid-state power stage** driven by **dual UCC27517 4A gate drivers** with optoisolated dual-control logic, and an expansive **32-channel multiplexed NTC thermal matrix** powered by dual **CD74HC4067** analog multiplexers.

---

## System Specifications

| Parameter | Operational Specification | Engineering Implementation Details |
| :--- | :--- | :--- |
| **Pack Chemistry & Configuration** | **16S LiFePO4** | 51.2 V nominal (40.0 V cutoff, 58.4 V absorption charging maximum) |
| **Continuous Current Rating** | **200 A Continuous** | Low-side bidirectional switching with 16x IRFB4110 N-FETs in parallel |
| **Analog Front-End (AFE)** | **TI BQ76952PFBR** | 48-pin TQFP autonomous battery monitor with hardware protections |
| **Voltage Acquisition** | **16 Differential Channels** | Individual RC filter networks ($20\ \Omega$ + $220\text{ nF}$) on taps 0–16 |
| **High-Power Switching** | **Back-to-Back Common-Source** | 8x parallel Charge FETs + 8x parallel Discharge FETs |
| **Gate Drive Stage** | **Dual TI UCC27517DBVR** | 4 A source / 4 A sink high-speed drivers with individual gate networks |
| **Switching Control Logic** | **Optoisolated Dual Control** | 4x EL817 optocouplers + BC817 BJTs for hardware trip & MCU overrides |
| **Current Measurement** | **Low-Side Kelvin Shunt** | Differential $100\ \Omega$ + $100\text{ pF}$ / $1.0\ \mu\text{F}$ filtering to BQ76952 SRP/SRN |
| **Thermal Monitoring** | **32 Multiplexed Channels** | 2x CD74HC4067 16:1 analog multiplexers with 32 dedicated NTC dividers |
| **Cell Temperature Sensing** | **16 Dedicated Cell Probes** | Individual surface temperature monitoring for every single cell in pack |
| **Auxiliary Temperature Sensing**| **16 System Probes** | FET banks, common-source bus, shunt, terminals, balancers, ambient |
| **Communications & Telemetry** | **I2C & Isolated CAN 2.0B** | BQ76952 I2C interface + ALERT line; dedicated MCU subsystem sheet |
| **Design Environment** | **KiCad 9.0 (20241221 / v9)** | Modular hierarchical schematic sheets with 3D component models |

---

## Subsystem Architecture

```mermaid
flowchart TD
    subgraph BatteryPack ["16S 100Ah LiFePO4 Battery Pack (40.0V - 58.4V)"]
        CELLS["16 Prismatic Cells (Taps 0 to 16)"]
        PACK_P["Pack Positive (P+)"]
        PACK_N["Pack Switched Return (P-)"]
        SHUNT["Low-Side Kelvin Shunt"]
    end

    subgraph Sheet01 ["Sheet 01: Analog Front End (TI BQ76952)"]
        RC_FILT["17x RC Low-Pass Filters\n(20Ω + 220nF per tap)"]
        AFE_IC["TI BQ76952PFBR (48-TQFP)\n• High-Accuracy 16-Cell ADC\n• Hardware OV/UV/OCD/SCD Protections"]
        HV_CLAMP["BAV21WS Diode Clamps (D1, D2)\nTop-Cell High-Voltage Transient Clamping"]
        AFE_REGS["BCX56-135 BJT Pre-Regulator (Q21)\nREG1 (3.3V/5V) & REG2 Rails"]
        SHUNT_FILT["Kelvin Shunt Filter\n(2x 100Ω + 100pF / 1µF)"]
        
        CELLS -->|17 Sense Taps| RC_FILT --> AFE_IC
        CELLS -->|Tap 16 Top Rail| HV_CLAMP --> AFE_IC
        AFE_IC --> AFE_REGS
        SHUNT --> SHUNT_FILT -->|SRP / SRN| AFE_IC
    end

    subgraph Sheet04 ["Sheet 04: Current Switching & Gate Drive (200A Cont)"]
        CHG_BANK["8x Parallel Charge N-FETs\nIRFB4110 (100V, 180A, Rds ≤ 4.5mΩ)\nR_bank ≈ 0.56 mΩ"]
        DSG_BANK["8x Parallel Discharge N-FETs\nIRFB4110 (100V, 180A, Rds ≤ 4.5mΩ)\nR_bank ≈ 0.56 mΩ"]
        DRV_CHG["UCC27517DBVR Gate Driver (4A)\n8x 27Ω Gate + 10kΩ Bleed Resistors"]
        DRV_DSG["UCC27517DBVR Gate Driver (4A)\n8x 27Ω Gate + 10kΩ Bleed Resistors"]
        OPTO_ISO["4x EL817 Optocouplers (U4-U7)\n+ 2x BC817 NPN Level Shifters (Q17-Q18)"]
        
        DRV_CHG --> CHG_BANK
        DRV_DSG --> DSG_BANK
        OPTO_ISO -->|Inverting Drive| DRV_CHG
        OPTO_ISO -->|Inverting Drive| DRV_DSG
        CHG_BANK <-->|FET_SOURCE_COMMON| DSG_BANK
        SHUNT -->|SHUNT_FET_SIDE| CHG_BANK
        DSG_BANK -->|PACK_MINUS| PACK_N
    end

    subgraph Sheet05 ["Sheet 05: 32-Channel Multiplexed Temperature Matrix"]
        MUX1["CD74HC4067SM Multiplexer 1\nChannels 0–15: 16x Cell Temperatures\n(CELL_TEMP_01 to CELL_TEMP_16)"]
        MUX2["CD74HC4067SM Multiplexer 2\nChannels 0–15: System Thermals\n(FETs, Busbars, Shunt, Lugs, Ambient)"]
        DIVIDERS["32x NTC Divider Sub-Sheets (05_1)\n(Precision 10kΩ 1% Lower Legs)"]
        
        DIVIDERS --> MUX1
        DIVIDERS --> MUX2
    end

    subgraph SystemControl ["Hierarchical System Control & Hierarchy Blocks"]
        AFE_IC -->|AFE_DCHG / AFE_DDSG| OPTO_ISO
        AFE_IC -->|AFE_REG1 (Pull-ups)| OPTO_ISO
        AFE_IC -->|I2C SCL/SDA + ALERT| SHEET_MCU["Sheet 03: MCU Control\n(CH32V203 / Isolated CAN)"]
        SHEET_MCU -->|CHG_ENABLE_MCU / DSG_ENABLE_MCU| OPTO_ISO
        SHEET_MCU -->|TEMP_MUX_S0..S3| MUX1 & MUX2
        MUX1 & MUX2 -->|TEMP_MUX1_COM / TEMP_MUX2_COM| SHEET_MCU
        SHEET_PWR["Sheet 02: Power Supply\n(High-Voltage Step-Down DC-DC)"]
    end
```

---

## Detailed Hardware Implementation

### 1. Analog Front End (AFE) & Battery Monitor (`01_Cell_AFE.kicad_sch`)

The core monitoring and autonomous hardware protection engine is built around the **Texas Instruments BQ76952PFBR** (48-pin TQFP, $9\times9\text{ mm}$):

* **Cell Input Filtering**:
  * 17 cell tap lines (`CELL_TAP_0` through `CELL_TAP_16`) route from the external cell balance harness.
  * Each tap passes through a low-pass RC network: $R = 20\ \Omega$ 1% 1206 resistor (`R1`–`R17`) and $C = 220\text{ nF}$ 1206 capacitor (`C1`–`C17`) directly feeding pins `VC0` to `VC16`.
  * The time constant ($\tau = 20\ \Omega \times 220\text{ nF} = 4.4\ \mu\text{s}$) suppresses inverter carrier spikes and inductive switching transients without degrading cell sampling throughput.
* **Top-Cell Transient Clamping**:
  * Connected across the top cell tap (`CELL_TAP_16`) to the chip power pin (`BAT`), dual high-voltage fast-switching diodes **BAV21WS** (`D1`, `D2`, 250V blocking, SOD-323) along with a $10\text{ k}\Omega$ 1206 resistor (`R23`) clamp high-voltage spikes and reverse-bias transients during full-load disconnects.
* **Kelvin Shunt Current Input**:
  * Low-side current shunt signals enter via `SHUNT_BAT_SIDE` and `SHUNT_FET_SIDE`.
  * Symmetrical filtering uses two $100\ \Omega$ 1206 series resistors (`R21`, `R22`), a $100\text{ pF}$ 0805 high-frequency differential ceramic capacitor (`C19`), and a $1.0\ \mu\text{F}$ 1812 bulk filter capacitor (`C20`) into inputs `SRP` (pin 17) and `SRN` (pin 18).
* **On-Chip & Auxiliary Regulators**:
  * `REG1` (pin 35): Generates a regulated logic supply filtered with a $1.0\ \mu\text{F}$ 0805 capacitor (`C24`), brought out as `AFE_REG1` to power optocoupler pull-ups and communication lines.
  * `REG2` / `REG18` Pre-Regulator: An external **BCX56-135** NPN bipolar power transistor (`Q21`, SOT-89) driven by `REGIN` with $300\ \Omega$ base resistor (`R69`), $10\text{ M}\Omega$ bleeder (`R70`), and capacitors $22\text{ nF}$ (`C23`), $2.2\ \mu\text{F}$ (`C21`), and $100\text{ nF}$ (`C22`) offloads thermal dissipation from the AFE when powering auxiliary rails from pack voltage.
* **Host Communications**:
  * Dedicated `SCL` (pin 26), `SDA` (pin 27), and `ALERT` (pin 28) pins are pulled up to `AFE_REG1` via individual $10\text{ k}\Omega$ 1206 resistors (`R19`, `R20`, `R24`).
* **Direct High-Speed Drive Pins**:
  * `DCHG` (pin 31) and `DDSG` (pin 32) output hardware trip signals routed directly to the switching stage.

### 2. High-Power Solid-State Switch Stage (`04_Current_Switching.kicad_sch`)

The switching subsystem provides full solid-state charge and discharge cutoff for **200 A continuous** throughput:

* **16-MOSFET Back-to-Back Common-Source Topology**:
  * **Charge Bank (8x IRFB4110PBF)**: Transistors `Q1`, `Q2`, `Q3`, `Q4`, `Q5`, `Q6`, `Q7`, `Q8` (TO-220, 100V, 180A, $R_{\text{DS(on)}} \le 4.5\ \text{m}\Omega$). Drains are tied to `SHUNT_FET_SIDE`, sources are tied to internal node `FET_SOURCE_COMMON`. Combined bank resistance: $R_{\text{bank}} \approx 0.56\ \text{m}\Omega$.
  * **Discharge Bank (8x IRFB4110PBF)**: Transistors `Q9`, `Q10`, `Q11`, `Q12`, `Q13`, `Q14`, `Q15`, `Q16`. Sources are tied to `FET_SOURCE_COMMON`, drains are tied to `PACK_MINUS`. Combined bank resistance: $R_{\text{bank}} \approx 0.56\ \text{m}\Omega$.
  * **Total Conduction Resistance**: Both banks in series yield $R_{\text{total}} \approx 1.12\ \text{m}\Omega$.
  * **Static Thermal Dissipation at 200 A**:
    $$P = I^2 \cdot R_{\text{total}} = 200^2 \times 0.00112 = 44.8\text{ W total}$$
    Distributed evenly across 16 TO-220 packages, dissipation is only **$2.8\text{ W}$ per transistor**, easily manageable with extruded aluminum cooling.
* **High-Speed Gate Drivers (TI UCC27517DBVR)**:
  * Two single-channel **UCC27517DBVR** drivers (SOT-23-5) rated for **4 A peak source and 4 A peak sink**:
    * `U2`: Drives the 8 Charge MOSFET gates (`Q1`–`Q8`).
    * `U3`: Drives the 8 Discharge MOSFET gates (`Q9`–`Q16`).
  * Individual gate networks: Each transistor gate is equipped with a dedicated $27\ \Omega$ 1206 damping resistor (`R25`–`R40`) to prevent high-frequency parasitic ringing, and a $10\text{ k}\Omega$ 1206 gate-to-source pulldown resistor (`R41`–`R56`) to ensure fail-safe turn-off if gate drive power collapses.
  * Gate driver decoupling: Local high-frequency bypass is provided by $100\text{ nF}$ capacitors (`C_DRV1`, `C_DRV4`) paired with $4.7\ \mu\text{F}$ bulk ceramic reservoirs (`C_DRV2`, `C_DRV3`) located adjacent to each driver IC.
* **Optoisolated Dual Control Logic (Hardware AFE + MCU Control)**:
  * Four **EL817** optocouplers (`U4`, `U5`, `U6`, `U7`, SOP-4) decouple the floating common-source gate drive potential from the controller ground plane.
  * Two **BC817-40,215** NPN transistors (`Q17`, `Q18`, SOT-23) level-shift the AFE direct drive lines (`AFE_DCHG`, `AFE_DDSG`) through $2.2\text{ k}\Omega$ base resistors (`R59`, `R61`) with $100\text{ k}\Omega$ pulldowns (`R63`, `R65`).
  * Hardware inputs `AFE_DCHG` and `AFE_DDSG` drive optocouplers `U4` and `U5` through $330\ \Omega$ resistors (`R67`, `R68`) powered by `AFE_REG1`.
  * Secondary host controller inputs `CHG_ENABLE_MCU` and `DSG_ENABLE_MCU` drive optocouplers `U6` and `U7` through $330\ \Omega$ resistors (`R71`, `R72`).
  * The UCC27517 inverting inputs (`IN-`) are pulled up to `GATE_DRV_VDD` via $10\text{ k}\Omega$ resistors (`R57`, `R58`), achieving an autonomous hardware safety cut: either the BQ76952 AFE hardware trip or the MCU can independently force the driver output LOW to disconnect the pack.

### 3. 32-Channel Multiplexed Temperature Matrix (`05_Temperature_Sensing.kicad_sch`)

Thermal management features comprehensive multichannel monitoring via dual 16-channel analog multiplexers:

* **Dual CD74HC4067SM Multiplexers (`U8`, `U9`)**:
  * High-speed CMOS 16:1 analog multiplexers in SSOP-24 packages powered from `+3V3` with local $100\text{ nF}$ decoupling (`C25`, `C26`).
  * Addressed simultaneously via a 4-bit parallel bus (`TEMP_MUX_S0`, `TEMP_MUX_S1`, `TEMP_MUX_S2`, `TEMP_MUX_S3`), streaming out on two analog lines: `TEMP_MUX1_COM` and `TEMP_MUX2_COM`.
* **32 Individual Precision NTC Divider Sub-Sheets (`05_1_NTC_DIVIDER.kicad_sch`)**:
  * Each channel instantiates `05_1_NTC_DIVIDER.kicad_sch`, containing a precision $10\text{ k}\Omega$ 1% resistor (`R62`, `R64`, `R66`, `R73`–`R100`) to `GND`. When connected to an external 10k NTC thermistor pulled up to reference voltage, it provides clean, temperature-dependent voltage telemetry.
* **Thermal Channel Mapping**:

| Channel Index | MUX 1 Net (`U8` / `TEMP_MUX1_COM`) | MUX 2 Net (`U9` / `TEMP_MUX2_COM`) | Subsystem Function |
| :---: | :--- | :--- | :--- |
| **0** | `CELL_TEMP_01` | `SHUNT_TEMP` | Cell 1 Surface / Current Shunt Manganin Block |
| **1** | `CELL_TEMP_02` | `INTAKE_TEMP` | Cell 2 Surface / Air Intake Vent |
| **2** | `CELL_TEMP_03` | `ENCLOSURE_TEMP` | Cell 3 Surface / Enclosure Internal Ambient |
| **3** | `CELL_TEMP_04` | `CHG_FET_TEMP` | Cell 4 Surface / Charge MOSFET Bank Heatsink |
| **4** | `CELL_TEMP_05` | `DSG_FET_TEMP` | Cell 5 Surface / Discharge MOSFET Bank Heatsink |
| **5** | `CELL_TEMP_06` | `TERMINAL_1_TEMP` | Cell 6 Surface / High-Current Terminal 1 (P+) |
| **6** | `CELL_TEMP_07` | `TERMINAL_2_TEMP` | Cell 7 Surface / High-Current Terminal 2 (P-) |
| **7** | `CELL_TEMP_08` | `PCB_TEMP_01` | Cell 8 Surface / Main Board Zone 1 |
| **8** | `CELL_TEMP_09` | `PCB_TEMP_02` | Cell 9 Surface / Main Board Zone 2 |
| **9** | `CELL_TEMP_10` | `PCB_TEMP_03` | Cell 10 Surface / Main Board Zone 3 |
| **10** | `CELL_TEMP_11` | `COMMON_SOURCE_BUS_TEMP` | Cell 11 Surface / MOSFET Source Busbar Junction |
| **11** | `CELL_TEMP_12` | `BALANCER_INDUCTOR_TEMP` | Cell 12 Surface / Active Balancer Inductor Core |
| **12** | `CELL_TEMP_13` | `BALANCER_SWITCH_TEMP` | Cell 13 Surface / Active Balancer Switching FETs |
| **13** | `CELL_TEMP_14` | `RESERVED_TEMP_14` | Cell 14 Surface / Auxiliary Probe Expansion |
| **14** | `CELL_TEMP_15` | `RESERVED_TEMP_15` | Cell 15 Surface / Auxiliary Probe Expansion |
| **15** | `CELL_TEMP_16` | `RESERVED_TEMP_16` | Cell 16 Surface / Auxiliary Probe Expansion |

---

## Project Structure

```text
BMS/
├── 16s_BMS/                               # KiCad 9.0 EDA Project Root
│   ├── 16s_BMS.kicad_pro                 # KiCad project definition and BOM export settings
│   ├── 16s_BMS.kicad_sch                 # Root schematic sheet (hierarchical sheet symbols)
│   ├── 01_Cell_AFE.kicad_sch             # Sub-sheet: TI BQ76952 AFE, taps 0-16, shunt, regs
│   ├── 02_Power_Supply.kicad_sch         # Sub-sheet: Power supply subsystem (in development)
│   ├── 03_MCU_Control.kicad_sch          # Sub-sheet: MCU, CAN bus, host telemetry (in development)
│   ├── 04_Current_Switching.kicad_sch    # Sub-sheet: 16x IRFB4110 FETs, UCC27517 drivers, optos
│   ├── 05_Temperature_Sensing.kicad_sch  # Sub-sheet: 2x CD74HC4067 multiplexers & thermal bus
│   ├── 05_1_NTC_DIVIDER.kicad_sch        # Hierarchical module: 10kΩ NTC precision divider (32 inst.)
│   └── 16s_BMS.kicad_pcb                 # KiCad PCB layout file (KiCad 9.0 database)
├── Datasheets/
│   └── bq76952.pdf                       # Official Texas Instruments BQ76952 datasheet
├── footprints/                            # Custom hardware library assets
│   ├── BQ76952PFBR/                      # TI BQ76952 48-TQFP footprint, symbol, and 3D STEP
│   │   ├── BQ76952PFBR.kicad_sym
│   │   ├── BQ76952PFBR.step
│   │   ├── QFP50P900X900X120-48N.kicad_mod
│   │   └── how-to-import.htm
│   └── UCC27517DBVR/                     # TI UCC27517 SOT-23-5 footprint, symbol, and 3D STEP
│       ├── UCC27517DBVR.kicad_sym
│       ├── UCC27517DBVR.step
│       ├── SOT95P280X145-5N.kicad_mod
│       └── how-to-import.htm
├── .gitignore                            # KiCad EDA, lock files, and history exclusions
├── git_tracker.py                        # Automated background KiCad save & git synchronization tool
├── project_overview.txt                  # Consolidated engineering dossier and hardware notes
├── start_tracker.sh                      # Shell launcher for background tracker
├── stop_tracker.sh                       # Shell script to stop background tracker
└── README.md                             # Repository system documentation
```

---

## Development Status & Phased Implementation

```
+─────────────────────────────────────────────────────────────────────────────+
|                          HARDWARE REVISION ROADMAP                          |
+─────────────────────────────────────────────────────────────────────────────+
                                       │
                                       ▼
  [ PHASE 1: CORE SCHEMATIC DESIGN ] ──────── (CURRENT STATUS)
  • [COMPLETED] Sheet 01: BQ76952 AFE, 17-cell RC tap filters, shunt sense, and BCX56 regulator.
  • [COMPLETED] Sheet 04: 200A cutoff switch bank (16x IRFB4110), dual UCC27517 drivers & EL817 optos.
  • [COMPLETED] Sheet 05: 32-channel multiplexed NTC thermal network (dual CD74HC4067 + 32 dividers).
  • [IN PROGRESS] Sheet 02: Power supply subsystem (HV step-down buck & intermediate rails).
  • [IN PROGRESS] Sheet 03: MCU control, CAN 2.0B galvanic transceiver, and telemetry interfaces.
  • [PENDING] Sheet Interconnections: Route inter-sheet buses on root sheet 16s_BMS.kicad_sch.
                                       │
                                       ▼
  [ PHASE 2: ERC VALIDATION & NETLIST SYNC ]
  • Run KiCad Electrical Rules Check (ERC) across all hierarchical sheets.
  • Annotate all remaining reference designators and verify footprint associations.
  • Import schematic netlist into 16s_BMS.kicad_pcb.
                                       │
                                       ▼
  [ PHASE 3: PCB LAYOUT & POWER ROUTING ]
  • Define 4-layer / 6-layer high-copper board stackup.
  • Route high-current copper busbars for 200A continuous path (B- -> Shunt -> FETs -> P-).
  • Kelvin-route current sense differential pair (SRP/SRN) directly from shunt pads.
  • Isolate high-voltage battery tap traces and thermal sensor routing from power switching loops.
                                       │
                                       ▼
  [ PHASE 4: PROTOTYPE ASSEMBLY & VALIDATION ]
  • Assemble bench test rig with 16-cell resistive simulator.
  • Validate BQ76952 I2C communication and autonomous hardware trip thresholds.
  • Measure gate driver switching waveforms (rise/fall times) under load.
  • Thermal soak test at 100A, 150A, and 200A continuous on a load bank.
```

---

## Automated Git Save Tracker

For continuous change tracking during KiCad schematic and layout sessions, a background watchdog daemon is included:

```bash
# Launch background save tracker
./start_tracker.sh

# Monitor active tracker logs
tail -f tracker.log

# Terminate tracker
./stop_tracker.sh
```

The tracker monitors file modification events, applies a 2.5-second debounce window across multi-sheet saves, strictly ignores lock files (`*.lck`), autosaves, and backup archives (`*-backups/`, `.history/`), and automatically commits and pushes clean changes to GitHub.

---

## Author & License

* **Lead Engineer**: Kausthubh Viswanath ([@koko69420](https://github.com/koko69420))
* **Repository**: [koko69420/SmartBMS_Active-balancing](https://github.com/koko69420/SmartBMS_Active-balancing)
* **Status**: Active Hardware Development
* **License**: Hardware schematics, PCB designs, and documentation are maintained under private academic/engineering copyright. All rights reserved.
