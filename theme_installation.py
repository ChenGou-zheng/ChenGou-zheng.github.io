import os
import shutil
import subprocess
import stat
import sys

# --- 自动定位与验证 ---
# 1. 将工作目录确定为脚本所在的根目录
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)
print(f"✅ 工作目录已设定为项目根目录: {project_root}")

# 2. 验证 Git 仓库
if not os.path.isdir('.git'):
    print("❌ 错误: 未找到 '.git' 文件夹。请确保脚本位于 Git 仓库的根目录。")
    sys.exit(1)
print("✅ Git 仓库验证通过。")

# --- 【核心修改】定义 Hugo 项目的路径 ---
HUGO_DIR = os.path.join(project_root, "hugo")

# 3. 验证 hugo 文件夹是否存在
if not os.path.isdir(HUGO_DIR):
    print(f"❌ 错误: 未在 {project_root} 中找到 'hugo' 文件夹。")
    print("   请确认您的项目结构是否正确。")
    sys.exit(1)
print(f"✅ Hugo 目录验证通过: {HUGO_DIR}")

# --- 配置 (路径基于 hugo 文件夹) ---
THEMES_DIR = os.path.join(HUGO_DIR, "themes")
THEME_NAME = "ananke"
THEME_URL = "https://github.com/theNewDynamic/gohugo-theme-ananke.git"
THEME_PATH = os.path.join(THEMES_DIR, THEME_NAME)

# --- 错误处理函数 ---
def handle_remove_readonly(func, path, exc_info):
    """处理 Windows 只读文件导致的删除错误。"""
    exc_type, _, _ = exc_info
    if exc_type is PermissionError and os.path.exists(path):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    else:
        raise

# --- 功能函数 ---
def run_command(command):
    """运行一个命令。"""
    try:
        print(f"⚙️  Running command: {' '.join(command)}")
        subprocess.run(command, check=True, capture_output=True, text=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {' '.join(command)}")
        print(e.stderr)
        sys.exit(1)

def clean_theme():
    """如果存在，则删除 hugo/themes/ananke 文件夹。"""
    if os.path.exists(THEME_PATH):
        print(f"🧹 正在删除旧的主题目录: {THEME_PATH}")
        shutil.rmtree(THEME_PATH, onerror=handle_remove_readonly)
        print("   -> 主题目录已移除。")

def reinstall_theme():
    """在 hugo/themes 内克隆主题并将其作为常规文件处理。"""
    if not os.path.exists(THEMES_DIR):
        print(f"ℹ️  'themes' 目录不存在，正在创建: {THEMES_DIR}")
        os.makedirs(THEMES_DIR)
    
    print(f"📥 正在从 {THEME_URL} 克隆主题至 {THEME_PATH}...")
    run_command(["git", "clone", THEME_URL, THEME_PATH])
    
    theme_git_dir = os.path.join(THEME_PATH, '.git')
    if os.path.exists(theme_git_dir):
        print(f"🔩 正在将主题转换为普通文件夹 (移除 .git)...")
        shutil.rmtree(theme_git_dir, onerror=handle_remove_readonly)
        print("   -> 转换成功。")
    
    print("   -> 主题已作为常规文件重新安装。")

def update_git_repository():
    """添加、提交并推送更改到远程仓库。"""
    print("🚀 正在更新 Git 仓库...")
    run_command(["git", "add", "."])
    run_command(["git", "commit", "-m", "\"Reinstalled ananke theme inside hugo directory\""])
    run_command(["git", "push"])
    print("   -> Git 仓库已更新。")

# --- 主程序入口 ---
if __name__ == "__main__":
    print("\n✨ 开始执行主题重新安装流程 (目标: hugo 文件夹内部)...\n")
    
    clean_theme()
    reinstall_theme()
    update_git_repository()
    
    print("\n✅ 所有任务已成功完成！")
