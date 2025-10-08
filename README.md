SPHINCS+ bit_security web GUI

Files:
- spx_sec.py      -- core calculation used by scripts
- spx_gui_web.py  -- Flask web GUI (this file)
- requirements.txt -- recommended pip packages for web GUI

How to run (recommended):
1. Create a virtual environment (optional but recommended):

python3 -m venv .venv
source .venv/bin/activate

2. Install dependencies:

pip install -r requirements.txt

3. Start the web GUI:

python3 spx_gui_web.py

4. Open http://127.0.0.1:5000/ in your browser, enter parameters and click Compute.

Notes:
- If your Python is >= 3.11, `spx_sec.py` will use Decimal.ln(); otherwise it may use mpmath (installed via requirements).
- Computations may be slow for large parameter sets; the server runs locally and is not exposed remotely by default.
