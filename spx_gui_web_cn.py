"""
Flask 本地化（中文）Web GUI 用于 SPHINCS+ bit_security 计算。

运行：
  python3 spx_gui_web_cn.py
然后在浏览器打开 http://127.0.0.1:5000/ 查看中文界面。

该文件从 spx_gui_web.py 继承逻辑，仅将界面文本翻译为中文。
"""
from flask import Flask, request, render_template_string, redirect, url_for, flash
import threading
import ast
import operator as op
import math

app = Flask(__name__)
app.secret_key = 'spx-secret-key-for-flash'

# 用于解析简单算术表达式的安全 eval
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
        raise ValueError(f"无效的表达式: {e}")

    def _eval(n):
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.Constant):
            if isinstance(n.value, (int, float)):
                return n.value
            raise ValueError("只允许整数或浮点字面量")
        if isinstance(n, ast.Num):
            return n.n
        if isinstance(n, ast.BinOp):
            if type(n.op) not in _allowed_operators:
                raise ValueError(f"不允许的运算符: {type(n.op)}")
            left = _eval(n.left)
            right = _eval(n.right)
            return _allowed_operators[type(n.op)](left, right)
        if isinstance(n, ast.UnaryOp):
            if type(n.op) not in _allowed_operators:
                raise ValueError(f"不允许的一元运算符: {type(n.op)}")
            return _allowed_operators[type(n.op)](_eval(n.operand))
        raise ValueError(f"不支持的表达式类型: {type(n)}")

    return _eval(node)


# 尝试导入计算函数
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
    <title>SPHINCS+ 比特安全性计算器</title>
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
    <h2>SPHINCS+ 比特安全性计算器</h2>
    {% if import_error %}
      <div class="error">导入错误: {{ import_error }}<br/>请确保 <code>spx_sec.py</code> 在同一目录，且所需依赖（例如 mpmath 或 Python 3.11+）已安装。</div>
    {% endif %}
    <form method="post" action="{{ url_for('compute') }}">
      <label>安全参数（位） <input type="text" name="tsec" value="{{ tsec|default('256') }}"></label>
      <label>最大签名数（例如 2**64） <input type="text" name="maxsigs" value="{{ maxsigs|default('2**64') }}"></label>
      <label>超树高度（h） <input type="text" name="h" value="{{ h|default('68') }}"></label>
      <label>超树层数（d） <input type="text" name="d" value="{{ d|default('17') }}"></label>
      <label>FORS子树高度（b） <input type="text" name="b" value="{{ b|default('9') }}"></label>
      <label>FORS子树数量（k） <input type="text" name="k" value="{{ k|default('35') }}"></label>
      <label>一次签名参数（w） <input type="text" name="w" value="{{ w|default('16') }}"></label>
      <div class="btn"><button type="submit">计算</button></div>
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
      <h3>计算结果</h3>
      <pre>{{ result }}</pre>
    {% endif %}

    <hr/>
    <p>说明：对于较大参数，计算可能较慢。本服务仅在本地运行。</p>
  </body>
</html>
'''


@app.route('/', methods=['GET'])
def index():
  ctx = dict(import_error=import_error,
         tsec='256', maxsigs='2**64', h='68', d='17', b='9', k='35', w='16')
  return render_template_string(TEMPLATE, **ctx)


@app.route('/compute', methods=['POST'])
def compute():
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
      error=f"bit_security 不可用: {import_error}",
    )

  # 解析并校验输入
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
      error=f"无效的输入: {e}",
    )

  try:
    res = bit_security(tsec, maxsigs, h, d, b, k, w)
    result_str = "{:.3f}".format(res)
    # result_str = str(res)
  except Exception as e:
    result_str = f"错误: {e}"

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
    app.run(host='127.0.0.1', port=5000, debug=False)
