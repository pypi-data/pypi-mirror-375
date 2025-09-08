#!/usr/bin/env python
import ast
import os
import sys
import argparse
import pkg_resources
import platform
import sysconfig
import importlib.util
import logging
import requests
from collections import defaultdict
import subprocess

def prompt_install_packages(requirements):
    to_install = []
    for name, ver, src, origins in requirements:
        # 忽略无法识别的库
        if src.startswith("未知来源") or ver is None:
            continue
        # 来自 PyPI 且本地未安装的库才加入安装列表
        if src.startswith("来自 PyPI"):
            # 如果有版本号，附加 ==ver；否则直接模块名
            pkg_str = f"{name}=={ver}" if ver else name
            to_install.append(pkg_str)

    if not to_install:
        logger.info("🎉 本地依赖齐全，无需安装")
        return

    logger.info("\n⚡ 检测到部分依赖可能未安装:")
    for pkg in to_install:
        logger.info(f"  {pkg}")

    ans = input("\n是否现在通过 pip 安装缺失依赖？(y/n): ").strip().lower()
    if ans == "y":
        for pkg in to_install:
            try:
                logger.info(f"💻 安装 {pkg} ...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
                logger.info(f"✅ {pkg} 安装完成")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ 安装失败: {pkg} ({e})")
    else:
        logger.info("⚠️ 用户选择跳过依赖安装")

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

IGNORED_DIRS = {'venv', '.venv', '__pycache__', '.git', 'env', '.idea', '.vscode', 'node_modules', 'dist', 'build'}
IGNORED_FILES = {'__init__.py', 'setup.py'}
SUPPORTED_EXTENSIONS = {'.py', '.pyw', '.ipynb'}

MODULE_ALIASES = {
}

STDLIB_MODULES = {
}

def extract_imports(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            if not content.strip():
                return set()
            tree = ast.parse(content, filename=file_path)
    except Exception as e:
        logger.warning(f"解析文件失败 {file_path}: {str(e)}")
        return set()

    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                imported_modules.add(node.module.split('.')[0])
            elif node.level > 0:
                dir_path = os.path.dirname(file_path)
                package_name = os.path.basename(dir_path)
                if package_name and package_name not in IGNORED_DIRS:
                    imported_modules.add(package_name)
    return imported_modules

def get_installed_packages():
    installed = {}
    top_level_map = {}
    for dist in pkg_resources.working_set:
        key = dist.key.lower()
        installed[key] = dist.version
        project_name = dist.project_name.lower()
        if project_name != key:
            installed[project_name] = dist.version
        # top_level.txt
        try:
            if dist.has_metadata("top_level.txt"):
                for line in dist.get_metadata("top_level.txt").splitlines():
                    if line.strip():
                        top_level_map[line.strip().lower()] = dist.key
        except Exception:
            continue
    return installed, top_level_map

def is_stdlib(module_name):
    if module_name in STDLIB_MODULES or module_name in sys.builtin_module_names:
        return True
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False
        if spec.origin in ("built-in", None):
            return True
        if "frozen" in str(spec.origin):
            return True
        stdlib_paths = [sysconfig.get_path("stdlib"), sysconfig.get_path("platstdlib")]
        stdlib_paths = [p for p in stdlib_paths if p]
        if not stdlib_paths:
            return False
        origin_path = spec.origin
        for stdlib_path in stdlib_paths:
            if origin_path.startswith(stdlib_path):
                return True
    except Exception:
        pass
    return False

def query_pypi_version(pkg_name):
    try:
        url = f"https://pypi.org/pypi/{pkg_name}/json"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            version = data.get("info", {}).get("version")
            return version
    except Exception as e:
        logger.debug(f"PyPI 查询失败 {pkg_name}: {e}")
    return None

def match_imports_to_packages(imports):
    installed_map, top_level_map = get_installed_packages()
    found_map = {}

    logger.info(" 扫描到的模块列表:")
    logger.info(", ".join(sorted(imports)))

    for mod in imports:
        mod_low = mod.lower()
        logger.debug(f"\n--- 处理模块: {mod} ---")

        resolved_pkg = None
        resolved_ver = None
        source_note = None

        # 1️⃣ 先联网查询 PyPI
        pkg_name = mod
        ver = query_pypi_version(pkg_name)
        if ver:
            resolved_pkg = pkg_name
            resolved_ver = ver
            source_note = f"来自 PyPI (module-name) (from: {mod})"
            logger.debug(f"PyPI 查询成功: {resolved_pkg}=={resolved_ver}")

        # 2️⃣ 再查本地安装包覆盖（如果已安装）
        pkg_key = top_level_map.get(mod_low)
        if pkg_key and pkg_key in installed_map:
            resolved_pkg = pkg_key
            resolved_ver = installed_map[pkg_key]
            source_note = "已安装 (top_level)"
            #logger.debug(f"✅ 本地 top_level 匹配: {resolved_pkg}=={resolved_ver}")
        elif mod_low in installed_map:
            resolved_pkg = mod_low
            resolved_ver = installed_map[mod_low]
            source_note = "已安装"
            #logger.debug(f"✅ 本地直接匹配: {resolved_pkg}=={resolved_ver}")

        # 3️⃣ 如果既没有 PyPI 也没有本地，标记未知
        if not resolved_pkg:
            resolved_pkg = mod
            resolved_ver = None  # 不再写 unknown
            source_note = "未知来源"
            logger.warning(f"⚠️ 未解析模块: {mod}")

        # 4️⃣ 记录
        key = resolved_pkg.lower()
        prev = found_map.get(key)
        if prev:
            prev["origins"].add(mod)
            # 如果之前是 PyPI 信息，但本地存在，则覆盖为已安装
            if prev["source"].startswith("来自 PyPI") and source_note.startswith("已安装"):
                prev.update({"name": resolved_pkg, "version": resolved_ver, "source": source_note})
                logger.debug(f"覆盖之前 PyPI 信息为本地已安装版本")
        else:
            found_map[key] = {"name": resolved_pkg, "version": resolved_ver, "source": source_note, "origins": {mod}}
            logger.debug(f"记录模块: {resolved_pkg}=={resolved_ver}, 来源: {source_note}")

    # 构建结果列表
    result = []
    logger.info("\n 最终依赖列表:")
    for info in found_map.values():
        ver_str = f"=={info['version']}" if info['version'] else ""
        result.append((info["name"], info["version"], info["source"], sorted(info["origins"])))
        logger.info(f"{info['name']}{ver_str}    # {info['source']} (from: {', '.join(info['origins'])})")
    return result

def collect_all_files(path):
    all_files = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d.lower() not in [x.lower() for x in IGNORED_DIRS]]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in SUPPORTED_EXTENSIONS and file.lower() not in [f.lower() for f in IGNORED_FILES]:
                all_files.append(os.path.join(root, file))
    return all_files

def export_requirements(requirements, output_path):
    if not requirements:
        logger.warning("⚠️ 未找到有效依赖")
        return
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# 自动生成的依赖列表\n")
            for name, ver, src, origins in sorted(requirements, key=lambda x: x[0].lower()):
                origin_list = ", ".join(origins)
                if ver:  # 如果有版本号就写 ==
                    f.write(f"{name}=={ver}    # {src} (from: {origin_list})\n")
                else:  # 没版本号直接写模块名
                    f.write(f"{name}    # {src} (from: {origin_list})\n")
        logger.info(f"✅ requirements.txt 已写入: {output_path}")
    except Exception as e:
        logger.error(f"❌ 写入requirements.txt失败: {e}")

def export_pyproject_toml(requirements, output_path, name):
    if not requirements:
        logger.warning("未找到有效依赖，跳过pyproject.toml生成")
        return
    py_ver = f">={sys.version_info.major}.{sys.version_info.minor}"
    content = [
        "[project]",
        f'name = "{name}"',
        'version = "0.1.0"',
        'description = "自动生成的项目"',
        'readme = "README.md"',
        f'requires-python = "{py_ver}"',
        "",
        "dependencies = ["
    ]
    for name_pkg, ver, src, origins in sorted(requirements, key=lambda x: x[0].lower()):
        content.append(f'    "{name_pkg}=={ver}",')
    content.append("]")
    content.extend([
        "",
        "[build-system]",
        'requires = ["setuptools>=61.0.0", "wheel"]',
        'build-backend = "setuptools.build_meta"',
    ])
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
        logger.info(f"pyproject.toml 已写入: {output_path}")
    except Exception as e:
        logger.error(f"写入pyproject.toml失败: {e}")

def analyze_project(path):
    if os.path.isfile(path):
        logger.info(f"🔍 分析单个文件: {path}")
        imports = extract_imports(path)
        return match_imports_to_packages(imports)
    elif os.path.isdir(path):
        logger.info(f"🔍 扫描项目目录: {path}")
        all_files = collect_all_files(path)
        logger.info(f"找到 {len(all_files)} 个代码文件")
        all_imports = set()
        for file_path in all_files:
            all_imports.update(extract_imports(file_path))
        return match_imports_to_packages(all_imports)
    else:
        logger.error(f"无效路径: {path}")
        return []

def main():
    parser = argparse.ArgumentParser(description="智能Python依赖分析工具 - 从代码生成requirements.txt和pyproject.toml")
    parser.add_argument("target", help="Python脚本或项目目录路径")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细输出")
    parser.add_argument("-o", "--output", help="指定输出目录（默认为输入目录）")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    path = os.path.abspath(args.target)
    if not os.path.exists(path):
        logger.error(f"路径不存在: {path}")
        sys.exit(1)

    output_dir = args.output or os.path.dirname(path) if os.path.isfile(path) else path
    os.makedirs(output_dir, exist_ok=True)

    requirements = analyze_project(path)

    name = os.path.splitext(os.path.basename(path))[0] if os.path.isfile(path) else os.path.basename(os.path.abspath(path)) or "project"

    export_requirements(requirements, os.path.join(output_dir, "requirements.txt"))
    export_pyproject_toml(requirements, os.path.join(output_dir, "pyproject.toml"), name)

    logger.info("依赖分析完成")
    prompt_install_packages(requirements)

if __name__ == "__main__":
    main()
