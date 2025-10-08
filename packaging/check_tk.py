#!/usr/bin/env python3
import tkinter, sys, sysconfig, os

try:
    t = tkinter.Tcl()
    print("TCL_LIBRARY:", t.eval('info library'))
except Exception as e:
    print("TCL eval error:", repr(e))

try:
    import _tkinter
    print("_tkinter:", getattr(_tkinter, '__file__', repr(_tkinter)))
except Exception as e:
    print("_tkinter error:", repr(e))

print("tkinter module:", getattr(tkinter, '__file__', None))
print("sys.executable:", sys.executable)
print("sys.prefix:", sys.prefix)
print("sys.version:", sys.version.replace('\n',' '))
for var in ['TCL_LIBRARY','TK_LIBRARY']:
    print(var, os.environ.get(var))

try:
    print('TKLIB sysconfig:', sysconfig.get_config_var('TKLIB'))
    print('TCLTK sysconfig:', sysconfig.get_config_var('TCLTK'))
except Exception as e:
    print('sysconfig error', repr(e))
