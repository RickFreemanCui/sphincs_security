"""
Flask web GUI for SPHINCS+ bit_security calculation.

Run:
  python3 spx_gui_web.py
Then open http://127.0.0.1:5000/ in your browser.

The app imports bit_security from spx_sec.py in the same folder and calls it.
"""
from flask import Flask, request, render_template_string, redirect, url_for, flash
import threading
import ast
import operator as op
import math

app = Flask(__name__)
app.secret_key = 'spx-secret-key-for-flash'

# safe eval for simple numeric expressions
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
        raise ValueError(f"Unsupported expression: {type(n)}")

    return _eval(node)

# Try to import the calculation function
try:
    from spx_sec import bit_security
except Exception as e:
    bit_security = None
    import_error = str(e)
else:
    import_error = None

TEMPLATE = '''
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>SPHINCS+ bit_security</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 24px; }
      label { display:block; margin-top:8px }
      input[type=text] { width: 320px }
      .btn { margin-top:12px }
      pre { background:#f7f7f7; padding:10px }
      .error { color: #a00 }
    </style>
  </head>
  <body>
    <h2>SPHINCS+ bit_security calculator</h2>
    {% if import_error %}
      <div class="error">Import error: {{ import_error }}<br/>Make sure <code>spx_sec.py</code> is present and dependencies (mpmath or Python 3.11+) are available.</div>
    {% endif %}
    <form method="post" action="{{ url_for('compute') }}">
      <label>security parameter (bits) <input type="text" name="tsec" value="{{ tsec|default('256') }}"></label>
      <label>max_sigs (e.g. 2**64) <input type="text" name="maxsigs" value="{{ maxsigs|default('2**64') }}"></label>
      <label>h <input type="text" name="h" value="{{ h|default('68') }}"></label>
      <label>d <input type="text" name="d" value="{{ d|default('17') }}"></label>
      <label>b <input type="text" name="b" value="{{ b|default('9') }}"></label>
      <label>k <input type="text" name="k" value="{{ k|default('35') }}"></label>
      <label>w <input type="text" name="w" value="{{ w|default('16') }}"></label>
      <div class="btn"><button type="submit">Compute</button></div>
    </form>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <ul>
          {% for m in messages %}
            <li class="error">{{ m }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}

    {% if error is defined and error %}
      <div class="error">{{ error }}</div>
    {% endif %}

    {% if result is defined %}
      <h3>Result</h3>
      <pre>{{ result }}</pre>
    {% endif %}

    <hr/>
    <p>Notes: Computation can be slow for large parameters. This server runs locally only.</p>
  </body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
  # default values
  ctx = dict(import_error=import_error,
         tsec='256', maxsigs='2**64', h='68', d='17', b='9', k='35', w='16')
  return render_template_string(TEMPLATE, **ctx)

@app.route('/compute', methods=['POST'])
def compute():
  # If the calculation function isn't available, show an error and keep inputs
  if bit_security is None:
    return render_template_string(
      TEMPLATE,
      import_error=import_error,
      tsec=request.form.get('tsec', ''),
      maxsigs=request.form.get('maxsigs', ''),
      h=request.form.get('h', ''),
      d=request.form.get('d', ''),
      b=request.form.get('b', ''),
      k=request.form.get('k', ''),
      w=request.form.get('w', ''),
      error=f"bit_security not available: {import_error}",
    )

  # Parse and validate inputs
  try:
    tsec = int(safe_eval(request.form.get('tsec', '').strip()))
    maxsigs = int(safe_eval(request.form.get('maxsigs', '').strip()))
    h = int(safe_eval(request.form.get('h', '').strip()))
    d = int(safe_eval(request.form.get('d', '').strip()))
    b = int(safe_eval(request.form.get('b', '').strip()))
    k = int(safe_eval(request.form.get('k', '').strip()))
    w = int(safe_eval(request.form.get('w', '').strip()))
  except Exception as e:
    return render_template_string(
      TEMPLATE,
      import_error=import_error,
      tsec=request.form.get('tsec', ''),
      maxsigs=request.form.get('maxsigs', ''),
      h=request.form.get('h', ''),
      d=request.form.get('d', ''),
      b=request.form.get('b', ''),
      k=request.form.get('k', ''),
      w=request.form.get('w', ''),
      error=f"Invalid input: {e}",
    )

  # run calculation synchronously (can take time); if desired we can make it async
  try:
    res = bit_security(tsec, maxsigs, h, d, b, k, w)
    result_str = str(res)
  except Exception as e:
    result_str = f"ERROR: {e}"

  return render_template_string(
    TEMPLATE,
    import_error=import_error,
    result=result_str,
    tsec=request.form.get('tsec', ''),
    maxsigs=request.form.get('maxsigs', ''),
    h=request.form.get('h', ''),
    d=request.form.get('d', ''),
    b=request.form.get('b', ''),
    k=request.form.get('k', ''),
    w=request.form.get('w', ''),
  )

if __name__ == '__main__':
    # Run local development server
    app.run(host='127.0.0.1', port=5000, debug=False)
