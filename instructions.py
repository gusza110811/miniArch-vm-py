import enum

class Instructions(enum.Enum):
    # instruction format
    # opcode (1B)
    # dest descriptor and src descriptor (1B) for most instructions
    # parameter (1-2B) for some instructions
    # ending in # mean not implemented yet

    nop0 = 0x00 # do nothing on empty memory
    nop1 = 0x01 # intentional nop
    nopf = 0x0f # intentional nop + unused dest/src descriptor

    # transfer
    rmov = 0x10
    ldi4 = 0x11
    ldi8 = 0x12
    ldi16= 0x13
    stb  = 0x18
    ldb  = 0x19
    stw  = 0x1A
    ldw  = 0x1B
    inp  = 0x1C
    out  = 0x1D
    lea  = 0x1E

    # arithmetic & logic (updates Z/C/N flags)
    add  = 0x20
    addi4= 0x21
    addi8= 0x22
    addi = 0x23
    sub  = 0x24
    subi4= 0x25
    subi8= 0x26
    subi = 0x27
    # cmp is equivalent to sub but doesnt save the value
    cmp  = 0x28
    cmpi4= 0x29
    cmpi8= 0x2A
    cmpi = 0x2B
    neg_ = 0x2C
    sxtbw= 0x2D#

    and_ = 0x30
    andi = 0x31
    or_  = 0x32
    ori  = 0x33
    xor_ = 0x34
    xori = 0x35
    shr  = 0x36
    shri4= 0x37
    shl  = 0x38
    shli4= 0x39
    not_ = 0x3A

    # flow control
    # distance encoded in dest descriptor (in order): rel8, rel16, abs16
    # condition encoded in source descriptor (in order): On zero(0), On not zero, On carry, On not carry, On negative, On positive, On sign overflow, On no sign overflow(7), Always(F)
    jmp  = 0x40
    call = 0x41
    ret  = 0x42
    # cross segment flow control (no condition)
    jmpf = 0x48
    callf= 0x49
    retf = 0x4A
    int_ = 0x4B

    # stack
    pushw= 0x50
    pushb= 0x51
    popw = 0x52
    popb = 0x53
    pushf= 0x54 # flags
    popf = 0x55
    pusha= 0x5E
    popa = 0x5F

    # flags
    # : Zero, Carry, Negative, Overflow, Interrupt enable
    clz  = 0x60
    clc  = 0x61
    cln  = 0x62
    clo  = 0x63
    cli  = 0x64
    cla  = 0x67
    stz  = 0x68
    stc  = 0x69
    stn  = 0x6A
    sto  = 0x6B
    sti  = 0x6C
    sta  = 0x6F

    halt = 0xFF # pseudo-instruction for debugging

    def __str__(self):
        return self.name
