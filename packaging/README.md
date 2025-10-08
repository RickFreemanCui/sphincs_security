打包说明（macOS / PyInstaller & py2app）

这是为本仓库提供的打包参考文档，包含使用 PyInstaller（跨平台）和 py2app（macOS 原生 .app）将 GUI 打包为独立可执行文件的步骤与注意事项。

可打包的入口脚本
- 桌面 GUI (tkinter)：`spx_gui.py`
- Web GUI (Flask)：`spx_gui_web.py`（运行后在本地启动一个 HTTP 服务器）

推荐方法 — PyInstaller（跨平台，常用）

1) 创建并激活虚拟环境（可选但推荐）

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) 安装依赖并构建（下面的 `build_pyinstaller.sh` 会做自动化）：

```bash
# 给脚本加可执行权限（第一次）
chmod +x packaging/build_pyinstaller.sh

# 打包桌面 GUI (tkinter)
packaging/build_pyinstaller.sh gui

# 打包 PyQt GUI (尝试包含 Qt 插件)
packaging/build_pyinstaller.sh pyqt

# 打包中文 Web GUI
packaging/build_pyinstaller.sh web_cn

# 打包 Web GUI (Flask)（生成一个可运行的可执行文件，运行后会启动本地 HTTP 服务）
packaging/build_pyinstaller.sh web
```

构建结果
- 可执行文件与/或 .app（取决于 PyInstaller 与平台）会放在 `dist/` 目录下。

注意事项
- `spx_sec.py` 在同一目录并被程序导入；PyInstaller 通常会自动发现此依赖。如果你有额外数据文件或模板，需要通过 `--add-data` 显式包含。
- 如果你的环境依赖 `mpmath`（见 `requirements.txt`），确保在构建环境中安装它。脚本会安装常见依赖与 PyInstaller。
- macOS 上若目标是生成带图标/签名的 `.app`，建议使用 `py2app` 或使用 PyInstaller 生成 `.app` 后再签名。签名/闸门（notarize）超出本说明范围。

备用方法 — py2app（macOS 原生 .app）

1) 在虚拟环境中安装 py2app：

```bash
pip install py2app
```

2) 新建 `setup.py`（示例）：

```python
from setuptools import setup

APP = ['spx_gui.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': [],
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

3) 运行 `python3 setup.py py2app`，输出在 `dist/` 下。

总结
- 对于简单、跨平台的打包，先尝试 PyInstaller（脚本已包含自动化步骤）。
- 如果需要 macOS 原生的 `.app`（并希望后续签名），可以使用 py2app。

如果你希望我现在在你的工程中运行一次构建（在工作区生成打包产物），告诉我你要打包哪一个入口（`gui` 或 `web`），我会尝试自动化运行并返回构建输出或错误信息。
