"""
Simple tkinter GUI for SPHINCS+ security computation.

This GUI calls bit_security from spx_sec.py (assumed to be in the same folder).

Usage: python3 spx_gui.py

Notes:
- "security parameter" field expects bits (e.g. 128 -> pass 128, or use 16*8 as integer expression)
- "max_sigs" accepts integer expressions like 2**64 (safe subset supported)

"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import ast
import operator as op

# safe eval for integer arithmetic expressions (supports + - * / // ** and parentheses)
# based on ast, only numeric literals and allowed operators permitted
_allowed_operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def safe_eval(expr: str):
    """Evaluate a simple arithmetic expression safely and return an int or float.
    Allowed operators: + - * / // ** and parentheses, integer/float literals.
    """
    try:
        node = ast.parse(expr, mode='eval')
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")

    def _eval(n):
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.Constant):
            if isinstance(n.value, (int, float)):
                return n.value
            raise ValueError("Only int/float literals allowed")
        if isinstance(n, ast.Num):
            return n.n
        if isinstance(n, ast.BinOp):
            if type(n.op) not in _allowed_operators:
                raise ValueError(f"Operator {type(n.op)} not allowed")
            left = _eval(n.left)
            right = _eval(n.right)
            return _allowed_operators[type(n.op)](left, right)
        if isinstance(n, ast.UnaryOp):
            if type(n.op) not in _allowed_operators:
                raise ValueError(f"Unary operator {type(n.op)} not allowed")
            return _allowed_operators[type(n.op)](_eval(n.operand))
        if isinstance(n, ast.Call):
            raise ValueError("Function calls not allowed")
        raise ValueError(f"Unsupported expression: {type(n)}")

    val = _eval(node)
    return val


# Try to import the calculation function
try:
    from spx_sec import bit_security
except Exception as e:
    bit_security = None
    _import_error = e
else:
    _import_error = None


class SPXGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SPHINCS+ bit_security calculator")
        self.resizable(False, False)

        main = ttk.Frame(self, padding=12)
        main.grid(column=0, row=0)

        # Input fields
        labels = [
            ("security parameter (bits)", "tsec"),
            ("max_sigs", "maxsigs"),
            ("h", "h"),
            ("d", "d"),
            ("b", "b"),
            ("k", "k"),
            ("w", "w"),
        ]
        self.vars = {}
        for i, (lab, key) in enumerate(labels):
            ttk.Label(main, text=lab).grid(column=0, row=i, sticky='w', pady=2)
            v = tk.StringVar()
            e = ttk.Entry(main, width=30, textvariable=v)
            e.grid(column=1, row=i, pady=2)
            self.vars[key] = v

        # sensible defaults similar to the script
        self.vars['tsec'].set('128')
        self.vars['maxsigs'].set('2**64')
        self.vars['h'].set('68')
        self.vars['d'].set('17')
        self.vars['b'].set('9')
        self.vars['k'].set('35')
        self.vars['w'].set('16')

        # compute button
        self.compute_btn = ttk.Button(main, text='Compute', command=self.on_compute)
        self.compute_btn.grid(column=0, row=len(labels), pady=(8,0))

        self.progress = ttk.Label(main, text='')
        self.progress.grid(column=1, row=len(labels), pady=(8,0), sticky='w')

        # output
        ttk.Label(main, text='Result (bit security):').grid(column=0, row=len(labels)+1, sticky='w', pady=(8,0))
        self.result_text = tk.Text(main, width=60, height=6, wrap='none')
        self.result_text.grid(column=0, row=len(labels)+2, columnspan=2, pady=(4,0))

        # import error show
        if _import_error is not None:
            message = f"Failed to import bit_security from spx_sec.py:\n{_import_error}\n\nMake sure spx_sec.py is in the same folder and dependencies (mpmath or Python 3.11+) are available."
            messagebox.showwarning("Import warning", message)

    def on_compute(self):
        # read and validate inputs
        try:
            tsec_raw = self.vars['tsec'].get().strip()
            maxsigs_raw = self.vars['maxsigs'].get().strip()
            h_raw = self.vars['h'].get().strip()
            d_raw = self.vars['d'].get().strip()
            b_raw = self.vars['b'].get().strip()
            k_raw = self.vars['k'].get().strip()
            w_raw = self.vars['w'].get().strip()

            tsec = int(safe_eval(tsec_raw))
            maxsigs_val = safe_eval(maxsigs_raw)
            maxsigs = int(maxsigs_val)
            h = int(safe_eval(h_raw))
            d = int(safe_eval(d_raw))
            b = int(safe_eval(b_raw))
            k = int(safe_eval(k_raw))
            w = int(safe_eval(w_raw))
        except Exception as e:
            messagebox.showerror("Input error", f"Invalid input: {e}")
            return

        if bit_security is None:
            messagebox.showerror("Missing function", f"bit_security not available: {_import_error}")
            return

        # disable UI while computing
        self.compute_btn.config(state='disabled')
        self.progress.config(text='Computing...')
        self.result_text.delete('1.0', tk.END)

        # run calculation in background thread
        def worker():
            try:
                res = bit_security(tsec, maxsigs, h, d, b, k, w)
                out = str(res)
            except Exception as e:
                out = f"ERROR: {e}"
            def on_done():
                self.result_text.insert('1.0', out)
                self.progress.config(text='Done')
                self.compute_btn.config(state='normal')
            self.after(0, on_done)

        threading.Thread(target=worker, daemon=True).start()


if __name__ == '__main__':
    app = SPXGui()
    app.mainloop()
