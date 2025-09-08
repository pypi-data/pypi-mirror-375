# 🔍 pyre_tools

`pyre_tools` 是一个轻量、高效的命令行工具，用于从 Python 脚本或项目目录中自动提取依赖并生成 `requirements.txt` 和 `pyproject.toml` 文件。

> 🚀 快速识别导入模块，匹配当前环境下已安装的包版本，自动输出兼容的依赖格式！

---

##  安装方式

###  从 PyPI 安装（推荐）
```bash
pip install pyre_tools
```

###  功能特性
        ✅ 支持 单个 Python 脚本 的依赖提取
        ✅ 支持 整个项目目录 的依赖扫描（自动递归查找 .py 文件）
        ✅ 自动过滤 .git, venv, __pycache__, .vscode 等无关目录
        ✅ 输出标准的 requirements.txt 和 pyproject.toml（兼容 pip / uv）
        ✅ 智能识别当前环境下实际安装的库及其版本
        ✅ 支持 Windows 和类 Unix 系统，零配置即可使用

###  使用方式
     提取项目目录依赖
        pyre /path/to/your/project or scripts.py
        支持.py, .pyw, .ipynb
        对于目录将自动扫描该路径下所有支持文件
        输出依赖到 /path/to/your/project/requirements.txt or /path/to/your/scripts.py同一目录
        生成 pyproject.toml 文件用于 uv / 构建工具

### 📝 License
    Copyright © 2025 yanghuaiyu  
    GitHub: [dawalishi122/SHZU](https://github.com/dawalishi122)
    This project is licensed under the terms of the [MIT License](LICENSE).