#!/usr/bin/env python3
"""
PyQt GUI for SPHINCS+ bit_security calculation.

This script prefers PyQt6, falls back to PyQt5 if necessary.
Run: python3 spx_gui_pyqt.py

"""
import sys
import threading
import ast
import operator as op

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
        # ast.Num is deprecated in newer Python; avoid direct reference to prevent DeprecationWarning.
        if n.__class__.__name__ == 'Num':
            return getattr(n, 'n')
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


# Try to import PyQt6, fallback to PyQt5
QT_VERSION = None
try:
    from PyQt6 import QtWidgets, QtCore
    QT_VERSION = 'PyQt6'
except Exception:
    try:
        from PyQt5 import QtWidgets, QtCore
        QT_VERSION = 'PyQt5'
    except Exception:
        QT_VERSION = None


if QT_VERSION is None:
    print("PyQt6 or PyQt5 not found. Install with: pip install PyQt6  # or PyQt5")
    sys.exit(1)


class SPXPyQtApp(QtWidgets.QWidget):
    # signal used to deliver results from worker thread to the GUI thread
    result_ready = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('SPHINCS+ bit_security (PyQt)')

        form = QtWidgets.QFormLayout()

        self.inputs = {}
        labels = [
            ('security parameter (bits)', 'tsec'),
            ('max_sigs', 'maxsigs'),
            ('h', 'h'),
            ('d', 'd'),
            ('b', 'b'),
            ('k', 'k'),
            ('w', 'w'),
        ]

        for label, key in labels:
            le = QtWidgets.QLineEdit()
            form.addRow(label, le)
            self.inputs[key] = le

        # sensible defaults
        self.inputs['tsec'].setText('256')
        self.inputs['maxsigs'].setText('2**64')
        self.inputs['h'].setText('68')
        self.inputs['d'].setText('17')
        self.inputs['b'].setText('9')
        self.inputs['k'].setText('35')
        self.inputs['w'].setText('16')

        self.compute_btn = QtWidgets.QPushButton('Compute')
        self.compute_btn.clicked.connect(self.on_compute)
        self.status_lbl = QtWidgets.QLabel('')

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.compute_btn)
        hbox.addWidget(self.status_lbl)
        form.addRow(hbox)

        self.result_text = QtWidgets.QPlainTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMinimumHeight(120)
        form.addRow('Result (bit security):', self.result_text)

        self.setLayout(form)

        # connect worker signal to slot
        self.result_ready.connect(self.on_done)

        if _import_error is not None:
            QtWidgets.QMessageBox.warning(self, 'Import warning',
                                          f'Failed to import bit_security from spx_sec.py:\n{_import_error}\nMake sure spx_sec.py is in the same folder and dependencies are available.')

    def on_compute(self):
        try:
            tsec = int(safe_eval(self.inputs['tsec'].text().strip()))
            maxsigs = int(safe_eval(self.inputs['maxsigs'].text().strip()))
            h = int(safe_eval(self.inputs['h'].text().strip()))
            d = int(safe_eval(self.inputs['d'].text().strip()))
            b = int(safe_eval(self.inputs['b'].text().strip()))
            k = int(safe_eval(self.inputs['k'].text().strip()))
            w = int(safe_eval(self.inputs['w'].text().strip()))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Input error', f'Invalid input: {e}')
            return

        if bit_security is None:
            QtWidgets.QMessageBox.critical(self, 'Missing function', f'bit_security not available: {_import_error}')
            return

        self.compute_btn.setEnabled(False)
        self.status_lbl.setText('Computing...')
        self.result_text.clear()

        def worker():
            try:
                res = bit_security(tsec, maxsigs, h, d, b, k, w)
                out = str(res)
            except Exception:
                import traceback, sys
                tb = traceback.format_exc()
                out = "ERROR:\n" + tb
                # print full traceback to stderr for terminal visibility
                print(tb, file=sys.stderr)

            # emit result via signal (thread-safe queued connection)
            self.result_ready.emit(out)

        threading.Thread(target=worker, daemon=True).start()

    def on_done(self, out: str):
        self.result_text.setPlainText(out)
        self.status_lbl.setText('Done')
        self.compute_btn.setEnabled(True)


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = SPXPyQtApp()
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
