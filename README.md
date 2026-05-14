# MiniArch-VM-py

A Python-based virtual machine for the MiniArch 16-bit CPU architecture. This virtual machine executes MiniArch binary programs (`.bin` files) produced by the MiniArch assembler, simulating the CPU, memory, and I/O devices.

## Features

- **Complete CPU emulation**: All MiniArch instructions, registers, and flags
- **Memory management**: 16-bit address space with segmentation
- **I/O devices**: UART console, programmable timers, disk controller, debug console
- **BIOS services**: High-level I/O routines
- **Debugging support**: Step-by-step execution, register inspection, memory dumps
- **Terminal interface**: Interactive console with terminal magic for enhanced display

## Installation

Requires Python 3.6+. No external dependencies.

Can only be used on POSIX-complaint system

Make symlink of the virtual machine to anywhere on your path as `ma-vm`

For example, at `~/.local/bin`:
```bash
ln -s ~/path/to/repo/main.py ~/.local/bin/ma-vm
```
replace `~/path/to/repo/main.py` with the absolute path to main.py

## Usage

```bash
ma-vm [options]
```

### Options

- `--rom <file>`: Load binary as ROM
- `--hda <file>`: Load binary as hard disk image (HDA)
- `-d, --debug`: Dump memory on halt
- `-t, --trace`: Dump instruction trace to `./.trace`
- `-h, --help`: Show help message

### Examples

Run a ROM program:

```bash
ma-vm --rom rom-examples/hello_world.bin
```

Run a disk image:

```bash
ma-vm --hda examples/disk.bin
```

Debug a program:

```bash
ma-vm --rom rom-examples/hello_world.bin -d -t
```

## Architecture Simulation

### CPU
- **Registers**: 17 registers including AX, BX, CX, DX, segment registers, stack pointers, and flags
- **Instruction Set**: Complete MiniArch ISA implementation
- **Execution**: Fetch-decode-execute cycle with proper flag handling

### Memory
- **Address Space**: 16-bit addressing (64KB)
- **Segmentation**: CS, DS, SS, ES segments

### I/O Devices
- **Disk Controller** (ports 0x0320-0x0327): Block device I/O
- **Debug Console** (port 0xFFFF): Asynchronous character I/O

## BIOS

The virtual machine includes a built-in BIOS (`./bios.asm`) that provides:

- Console I/O functions
- Disk operations
- Timer services
- Interrupt handling

Programs can use BIOS interrupts for high-level operations instead of direct hardware access.

## Debugging

In debug mode, the virtual machine provides:

- **Register dump**: View all register values
- **Memory inspection**: Examine memory contents
- **Trace logging**: Log execution flow

## Terminal Interface

Uses `termmagic.py` for enhanced terminal display:

Tests cover instruction execution, memory operations, and I/O functionality.

## Performance

The virtual machine is designed for educational use rather than high performance. Typical execution speeds allow for interactive debugging and testing.

## Contributing

If you actually want to contribute just make a pull request or something, i wont be too picky

## License

eventually?

default copyright law still apply for now
