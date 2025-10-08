# SPHINCS+ 安全性评估工具

## 简介

这个仓库包含用于评估 SPHINCS+ 签名方案“位安全性（bit security）”的计算脚本及几个简单的 GUI 前端（桌面与 Web）。项目目的是方便快速试算不同参数组合下的安全性值。

主要文件
- `spx_sec.py` — 核心计算函数 `bit_security` 的实现。
- `spx_gui.py` — 基于 tkinter 的桌面 GUI。
- `spx_gui_pyqt.py` — 基于 PyQt 的桌面 GUI（可选，优先使用 PyQt6，回退到 PyQt5）。
- `spx_gui_web.py` — 英文版的 Flask Web GUI。
- `spx_gui_web_cn.py` — 中文版的 Flask Web GUI（本地化界面）。
- `packaging/` — 包含打包脚本与说明：`build_pyinstaller.sh`、README 等。
- `requirements.txt` — 推荐的 Python 包依赖（例如 Flask、mpmath）。

## 快速开始（推荐）
1) 创建并激活虚拟环境（可选但推荐）：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) 安装依赖：

```bash
pip install -r requirements.txt
```

3) 运行 Web GUI（英文）：

```bash
python3 spx_gui_web.py
# 在浏览器打开 http://127.0.0.1:5000/
```

4) 运行 Web GUI（中文）：

```bash
python3 spx_gui_web_cn.py
# 在浏览器打开 http://127.0.0.1:5000/
```

5) 运行桌面 GUI：

tkinter 版本（无需额外安装 GUI 库，但打包时需注意本机 Python 是否包含 tkinter）
```bash
python3 spx_gui.py
```

PyQt 版本（需先安装 PyQt6 或 PyQt5）
```bash
pip install PyQt6   # 或 pip install PyQt5
python3 spx_gui_pyqt.py
```

打包（使用 PyInstaller）
仓库中提供了一个辅助脚本 `packaging/build_pyinstaller.sh`，可以一键创建虚拟环境、安装 PyInstaller 与依赖并打包不同的入口脚本。

用法（在项目根运行）：

```bash
chmod +x packaging/build_pyinstaller.sh
# 打包英文 Web GUI
packaging/build_pyinstaller.sh web
# 打包中文 Web GUI
packaging/build_pyinstaller.sh web_cn
# 打包 tkinter 桌面 GUI
packaging/build_pyinstaller.sh gui
# 打包 PyQt 桌面 GUI（脚本会尝试包含 Qt 插件）
packaging/build_pyinstaller.sh pyqt
```

构建产物将放到 `dist/` 目录下。对于 PyQt 应用，脚本会尝试自动包含 Qt 的 plugins 目录（如果检测到），但在某些 macOS 配置下可能仍需手动包含 `platforms` 插件或使用 `--onedir` 调试模式。

## 常见问题
- 如果运行 tkinter GUI 时出现 `_tkinter` 缺失：说明当前 Python 没有链接 Tcl/Tk，需使用 python.org 官方安装包或用 pyenv 编译并链接 Homebrew 的 tcl-tk。
- 如果 PyInstaller 打包后的可执行在启动时报缺某些库或插件：查看 `build/<name>/warn-<name>.txt`，通常按警告添加 `--add-data` 或 `--add-binary` 即可解决。

## 开发者与贡献
- 欢迎发 PR 或 issue

## 许可证
- 本仓库中的代码遵循原作者声明的许可（如果没有特别声明，请在提交前确认许可条款）。
