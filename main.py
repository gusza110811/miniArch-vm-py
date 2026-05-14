#!/usr/bin/python3
from memory import Memory, IO
import termmagic
from execute import Executor, OpcodeFault
from instructions import Instructions
import argparse
import os, sys

AX, BX, CX, DX, CS, DS, SS, ES, SP, BP,   AH, BH, CH, DH = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,   12, 13, 14, 15

Z, C, N, O, I = 0, 1, 2, 3, 4

class Emulator:
    def __init__(self):
        self.io = IO()
        self.executor = Executor(self)

        self.pc = 0 # not accessible from software

        self.registers = [
            0,0,0,0, # ax, bx, cx, dx
            0xffff,0,0,0, # cs, ds, ss, es
            0,0    # sp, bp
        ]

        self.ip = 0

        self.flags = [
            False, # zero
            False, # carry
            False, # negative
            False, # sign overflow
            False, # interrupt enable
        ]

        self.running = True
        self.doTrace = True

        self.trace = []
        self.jumped = False

        self.params = []
    
    def check(self,reg:int):
        res = self.registers[reg]
        prevCarry = self.flags[C]
        if res == 0:
            self.flags[Z] = True
        else:
            self.flags[Z] = False

        if res > 0xFFFF:
            self.flags[C] = True
            self.registers[reg] &= 0xFFFF
        else:

            self.flags[C] = False
        if prevCarry != self.flags[C]:
            self.flags[O] = True
        else:
            self.flags[O] = False

        if res < 0:
            self.flags[N] = True
            self.registers[reg] &= 0xFFFF
        else:
            self.flags[N] = False
    def get(self,reg:int) -> int:
        if reg < 0xC:
            return self.registers[reg]
        else:
            reg = reg-0xC
            return self.registers[reg] >> 8
    def set(self,reg:int,val:int):
        if reg < 0xC:
            self.registers[reg] = val
        else:
            reg = reg-0xC
            self.registers[reg] = ((self.registers[reg]&0xff) | (val << 8)) &0xffff
    
    def fetch(self):
        val = self.memory.loadb(self.registers[CS], self.pc)
        self.pc += 1
        return val
    
    def fetchs(self, count:int, signed=False):
        tmp = bytearray()
        for idx in range(count):
            tmp.append(self.fetch())
        val = int.from_bytes(tmp,"little",signed=signed)
        self.params.append(val)
        return val
    
    def pushb(self, value:int):
        self.registers[SP] -= 1
        self.check(SP)
        self.memory.storeb(self.registers[SS],self.registers[SP],value)
    def pushw(self, value:int):
        self.registers[SP] -= 2
        self.check(SP)
        self.memory.storew(self.registers[SS],self.registers[SP],value)
    def popb(self):
        val = self.memory.loadb(self.registers[SS],self.registers[SP])
        self.registers[SP] += 1
        self.check(SP)
        return val
    def popw(self):
        val = self.memory.loadw(self.registers[SS],self.registers[SP])
        self.registers[SP] += 2
        self.check(SP)
        return val

    def main(self,initcode:bytearray):
        self.memory = Memory(initcode)
        doTrace = self.doTrace

        while self.running:
            self.ip = self.pc
            try:
                inst = Instructions(self.fetch())
            except ValueError as e:
                print(self.ip, e)
                self.running == False
            if doTrace:
                self.trace.append((
                    (self.registers[CS],self.ip),
                    self.jumped,
                    inst,
                    self.params,
                    self.registers.copy(),
                    self.flags.copy(),
                    #self.memory.lastAccess() if inst in memAccess else None
                ))
            self.executor.execute(inst)

            self.params = []
    
    def dump(self):
        names = ["ax","bx","cx","dx",
                 "cs","ds","ss","es",
                 "sp","bp"]
        
        for idx,val in enumerate(self.registers):
            print(f"{names[idx]}: {val:4x}")

        itemperline = 8
        items = 0
        
        print("\nRam:")
        
        for val in self.truncate_memory(self.memory.ram):
            print(val,end="  ")
            items += 1
            if items == itemperline:
                print()
                items = 0
        items = 0
        print()

    def truncate_memory(self, mem, start: int = 0, end: int = None):
        result = []
        if end is None:
            end = len(mem.values)

        prev_value = None
        repeat_count = 0
        printed = False

        for i in range(start, end):
            value = mem.values[i]

            if value == prev_value:
                repeat_count += 1
                printed = False
            else:
                if repeat_count > 0:
                    if not printed:
                        if repeat_count > 1:
                            result.append(f"{repeat_count:5} times")
                        else:
                            result.append("repeated   ")
                        printed = True
                    repeat_count = 0

                result.append(f"{i:05X}: x{value:02X} ")
                prev_value = value

        if repeat_count > 0:
            result.append(f"...repeated to {(end-1):04X}")
        
        return result

def writeTrace(filename:str, trace:list):
    file = open(filename,"w")
    registerNames = [
        "ax", "bx", "cx", "dx",
        "cs", "ds", "ss", "es",
        "sp", "bp"
    ]
    for item in trace[:10000]:
        file.write(
            (f"{item[0][0]:04X}:{item[0][1]:04X}" +
            (">" if item[1] else " ") +
            "{0}:{1:02X}".format(str(item[2]),item[3][0] if item[3] else 0).ljust(10) +
            "{0:<5}".format(", ".join([f"{item:4X}" for item in item[3][1:]])) + " " +
            (
                " ".join([f"{registerNames[idx]}={item[4][idx]:04X}" for idx in range(10)])
            ) + " " +
            (
                ('Z' if item[5][0] else "z") +
                ('C' if item[5][1] else "c") +
                ('N' if item[5][2] else 'n') +
                ('O' if item[5][3] else 'o') +
                ('I' if item[5][4] else 'i')
            ) + " " #+
            #("  " + f"{item[6][0]:05X} = {item[6][1]:X}" if item[6] else "")
            ).rstrip() + "\n"

        )
    if len(trace) > 10000:
        for item in trace[:10000]:
            file.write(
                (f"{item[0][0]:04X}:{item[0][1]:04X}" +
                (">" if item[1] else " ") +
                "{0}:{1:02X}".format(str(item[2]),item[3][0] if item[3] else 0).ljust(10) +
                "{0:<5}".format(", ".join([f"{item:4X}" for item in item[3][1:]])) + " " +
                (
                    " ".join([f"{registerNames[idx]}={item[4][idx]:04X}" for idx in range(10)])
                ) + " " +
                (
                    ('Z' if item[5][0] else "z") +
                    ('C' if item[5][1] else "c") +
                    ('N' if item[5][2] else 'n') +
                    ('O' if item[5][3] else 'o') +
                    ('I' if item[5][4] else 'i')
                ) + " " #+
                #("  " + f"{item[6][0]:05X} = {item[6][1]:X}" if item[6] else "")
                ).rstrip() + "\n"
            )
        file.write("\n...truncated...\n\n")
        for item in trace[max(10000-len(trace),-10000):]:
            file.write(
                (f"{item[0][0]:04X}:{item[0][1]:04X}" +
                (">" if item[1] else " ") +
                "{0}:{1:02X}".format(str(item[2]),item[3][0] if item[3] else 0).ljust(10) +
                "{0:<5}".format(", ".join([f"{item:4X}" for item in item[3][1:]])) + " " +
                (
                    " ".join([f"{registerNames[idx]}={item[4][idx]:04X}" for idx in range(10)])
                ) + " " +
                (
                    ('Z' if item[5][0] else "z") +
                    ('C' if item[5][1] else "c") +
                    ('N' if item[5][2] else 'n') +
                    ('O' if item[5][3] else 'o') +
                    ('I' if item[5][4] else 'i')
                ) + " " #+
                #("  " + f"{item[6][0]:05X} = {item[6][1]:X}" if item[6] else "")
                ).rstrip() + "\n"
            )
    file.close()

if __name__ == "__main__":
    emulator = Emulator()
    if os.path.islink(__file__):
        link = os.path.dirname(os.readlink(__file__))
        if link.startswith("/"):
            __dir__ = link
        else:
            __dir__ = os.path.join(os.path.dirname(__file__),link)
    else:
        __dir__ = os.path.dirname(__file__)

    argparser = argparse.ArgumentParser(
        prog="MiniArch Emulator",
        description="Emulate MiniArch")
    argparser.add_argument("--rom",help="path to rom image")
    argparser.add_argument("--trace","-t",action="store_true",help="write trace log to .trace (first and last 10000 instructions only)")
    argparser.add_argument("--dump","-d",action="store_true",help="dump final state on halt")
    argparser.add_argument("--hda", help="path to disk image")

    args = argparser.parse_args()

    if args.rom:
        if os.path.exists(args.rom):
            code = open(args.rom,"rb").read()
        else:
            sys.exit(f"Rom not found: {args.rom}")
    else:
        attempts = [
            "main.bin", "rom.bin", "bios.bin",
            "main.img", "rom.img", "bios.img",
        ]
        name = None
        for attempt in attempts:
            if os.path.isfile(attempt):
                name = attempt
                break
            if os.path.isfile(os.path.join(__dir__,attempt)):
                name = os.path.join(__dir__,attempt)
                break
        if not name:
            sys.exit(f"No rom found, try passing a path to rom")

        code = open(name,"rb").read()

    if args.hda:
        if os.path.exists(args.hda):
            emulator.io.disk.disks[0] = open(args.hda,"rb+")
        else:
            sys.exit(f"Disk image not found: {args.hda}")

    dump = bool(args.dump)
    trace = bool(args.trace)
    emulator.doTrace = trace

    try:
        termmagic.disable_buffering()
        termmagic.disable_lfcrlf()
        emulator.main(code)
    except KeyboardInterrupt:
        pass
    except:
        termmagic.reset()
        import traceback
        traceback.print_exc()
    finally:
        while emulator.io.dbg.outbuffer:pass
        termmagic.reset()
    print("")

    if dump:
        emulator.dump()
    if trace:
        writeTrace(".trace",emulator.trace)
