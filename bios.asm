main {
    ; set up segment
    mov ax, 0xE800
    mov ds, ax
    mov ax, 0x1000
    mov ss, ax
    mov ax, 0
    mov es, ax

    ; startup message
    mov bx, start_msg
    call print

    ; check for disks
    mov bx, 0x0320
    mov ax, 0x03
    out bx, ax
    mov bx, 0x0327
    in ax, bx
    cmp ax, 0
    jz no_disks

    ; add interrupt services
    mov ax, disk_srv
    mov [es:0x13 * 4], ax
    mov [es:0x13 * 4 + 2], cs
    mov ax, serial_port_srv
    mov [es:0x14 * 4], ax
    mov [es:0x14 * 4 + 2], cs

    call read

    ; reset segments
    mov ds, 0
    mov es, 0
    mov ss, 0

    jmpf 0, 0x7c00
}

no_disks {
    mov bx, nodisk_err
    call print
    hlt
}

; 0x13 service
; dx = command
disk_srv {

    cmp dx, 0
    jz status
    cmp dx, 1
    jz read
    cmp dx, 2
    jz write

    cmp dx, 4
    jz sector

    retf

    ; ax -> status
    status {
        push bx
        mov bx, 0x321
        in ax, bx
        pop bx
        retf
    }

    ; bx <- start of 512 bytes region in memory to write to
    ; ax -> status (0 = success. 1 = fail)
    read {
        push dx

        ; wait
        wait1:
            mov dx, 0x321
            in ax, dx
            cmp ax, 1
        jz wait1

        mov dx, 0x320
        mov ax, 1
        out dx, ax

        ; wait
        wait2:
            mov dx, 0x321
            in ax, dx
            cmp ax, 1
        jz wait2

        cmp ax, 0
        jnz fail

        ; read buffer
        mov dx, 0x0327
        mov cx, 512
        read_loop:
            in ax, dx
            mov [b bx], ax
            add bx, 1
            sub cx, 1
        jnz read_loop

        pop dx
        mov ax, 0
        retf

        fail:
            mov ax, 1
            pop dx
        retf
    }

    ; bx <- start of 512 bytes region in memory to read from
    ; ax -> status (0 = success. 1 = fail)
    write {
        push dx

        ; wait
        wait:
            mov dx, 0x321
            in ax, dx
            cmp ax, 1
        jz wait

        mov dx, 0x320
        mov ax, 2
        out dx, ax

        cmp ax, 0
        jnz fail

        ; write buffer
        mov dx, 0x0327
        mov cx, 512
        write_loop:
            mov ax, [b bx]
            out dx, ax
            add bx, 1
            sub cx, 1
        jnz write_loop

        pop dx
        mov ax, 0
        retf

        fail:
            mov ax, 1
        retf
    }

    ; ax = sector (lower word)
    ; cx = sector (upper word)
    sector {
        push bx

        mov bx, 0x322
        out bx, ax
        mov bx, 0x323
        out bx, ah
        mov bx, 0x324
        out bx, cx
        mov bx, 0x325
        out bx, ch

        pop bx
        retf
    }
}

; 0x14 service
; dx = command
serial_port_srv {
    cmp dx, 1
    jz sput_char
    cmp dx, 2
    jz sget_char
    retf

    sput_char {
        push bx
        mov bx, 0xFFFF
        out bx, ax
        pop bx
        retf
    }

    sget_char {
        push bx
        mov bx, 0xFFFF
        in ax, bx
        pop bx
        retf
    }

}

read {
    mov bx, 0x0320
    mov ax, 0x05
    out bx, ax
    mov ax, 0x01
    out bx, ax

    ; wait
    wait:
    mov bx, 0x321
    in ax, bx
    cmp ax, 1
    jz wait

    ; check if success
    cmp ax, 0
    jnz fail

    ; read buffer
    mov dx, 0x0327
    mov bx, 0x7c00
    mov cx, 512
    read_loop:
        in ax, dx
        mov [b es:bx], ax
        add bx, 1
        sub cx, 1
    jnz read_loop

    ret

    fail:
        mov bx, diskfail_err
        call print
        hlt
}

; bx = pointer to message
print {
    pusha
    mov dx, 0xffff
    loop:
        mov ax, [b bx]
        cmp ax, 0
        jz done
        add bx, 1
        out dx, ax
    jmp loop

    done:
    popa
    ret
}

{
    .offset 0x8000
    ; if ds = E800
    ; 32k of space for rw data, and 32k for ro data
    export start_msg:
        .asciiz "MiniArch BIOS\r\n\r\n\r\n"
    export nodisk_err:
        .asciiz "Disk 0 not available\r\n"
    export diskfail_err:
        .asciiz "Failed to load boot sector\r\n"
}

.org 0xFFF0
reset {
    jmpf 0xf000, main
}
