# AXI Interfacer

**Interfacer** is designed to extract and generate AXI based interfaces for wrapping partially reconfigurable Verilog modules.
The tool parses an RTL Verilog hierarchy, extracting the top module and generating a blackbox wrapper for it.
Additionally, it generates a `config.json` file that can be used by Xilinx TCL scripts to generate interconnects that support the various interfaces exposed by the wrapper.

## Commands

* `interfacer generate [wrapper-name]` - Generate Blackbox Wrapper.
* `interfacer -h` - Print help message and exit.

