import os, sys
if os.name != "posix":
    raise NotImplementedError("terminal magic does not work with non-posix system (yet)")
import tty, termios

if sys.stdin.isatty():
    tattr = termios.tcgetattr(sys.stdin.fileno()).copy()
if sys.stdout.isatty():
    tattro = termios.tcgetattr(sys.stdout.fileno()).copy()

def disable_buffering():
    if not sys.stdin.isatty():
        return
    stdinfd = sys.stdin.fileno()

    tty.setcbreak(stdinfd, termios.TCSANOW)

def disable_lfcrlf():
    if not sys.stdout.isatty():
        return
    newattr = termios.tcgetattr(sys.stdout.fileno())
    newattr[1] &= ~termios.ONLCR
    termios.tcsetattr(sys.stdout, termios.TCSANOW, newattr)

def reset():
    if sys.stdin.isatty():
        global tattr
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, tattr)
    if sys.stdout.isatty():
        global tattro
        termios.tcsetattr(sys.stdout.fileno(), termios.TCSANOW, tattro)
