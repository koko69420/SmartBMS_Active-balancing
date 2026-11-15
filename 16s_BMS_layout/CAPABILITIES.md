# Capabilities & Toolchain Notes

- **KiCad Version**: 10.0.7 (`kicad-cli` and `pcbnew` Python 3.11 bindings invoked directly from the mounted AppImage at `/tmp/.mount_kicad*` for sub-second CLI execution).
- **GUI vs Native Headless Script**: KiCad GUI/MCP UI is not required; all schematic ERC, netlist exports, board creation, zone filling, DRC checks (`kicad-cli pcb drc --format json`), BOM CSV export, SVG export, and PNG rendering (`kicad-cli pcb render`) run deterministically via `pcbnew` and `kicad-cli`.
- **Autorouter**: Freerouting JAR (`/home/kaust/.kicad-mcp/freerouting.jar`) running on OpenJDK 25 (`-mt 1` single-threaded best-of-N seeds/passes via DSN export and SES import, using `FreeroutingCommands` net-name reconciliation).
- **Mechanical Verification**: Automated checks verify 0 unconnected items, 0 shorts, 0 clearance violations in KiCad DRC, exact netlist parity against `netlist_reference.json`, `>= 3.0 mm` isolation barriers across galvanic domains, board size <= 120 x 50 mm, and zero em/en dashes.
