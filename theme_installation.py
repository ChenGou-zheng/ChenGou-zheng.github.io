import os
import shutil
import subprocess
import stat
import sys # 【新增】导入 sys 模块

# --- 【第一步：自动定位并切换工作目录】 ---
# 获取脚本文件自身所在的绝对路径
#  __file__ 是一个魔法变量，代表当前脚本的文件名
script_path = os.path.abspath(__file__)
# 获取该脚本所在的目录，也就是我们期望的项目根目录
project_root = os.path.dirname(script_path)
# 将当前工作目录切换到项目根目录
os.chdir(project_root)
print(f"✅ 工作目录已成功切换至: {os.getcwd()}")


# --- 【第二步：验证这是否是一个 Git 仓库】 ---
if not os.path.isdir('.git'):
    print("❌ 错误: 在当前目录中未找到 '.git' 文件夹。")
    print("   请确保此脚本位于您的 Git 仓库的根目录中。")
    sys.exit(1) # 使用 sys.exit() 退出脚本
print("✅ Git 仓库验证通过。")


# --- 错误处理函数 ---
def handle_remove_readonly(func, path, exc_info):
    """专门用于 shutil.rmtree 的错误处理器，解决 Windows 只读文件问题。"""
    exc_type, exc_value, exc_tb = exc_info
    if exc_type is PermissionError and os.path.exists(path):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    else:
        raise

# --- 配置 ---
THEMES_DIR = "themes"
THEME_NAME = "ananke"
THEME_URL = "https://github.com/theNewDynamic/gohugo-theme-ananke.git"
THEME_PATH = os.path.join(THEMES_DIR, THEME_NAME)

# --- 功能函数 ---

def run_command(command):
    """运行一个命令并打印其输出。"""
    try:
        print(f"⚙️  Running command: {' '.join(command)}")
        # 使用 shell=True 在 Windows 上可以更好地处理路径和命令
        result = subprocess.run(command, check=True, capture_output=True, text=True, shell=True)
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {' '.join(command)}")
        print(e.stderr)
        sys.exit(1)

def clean_theme():
    """如果存在，则删除主题目录。"""
    if os.path.exists(THEME_PATH):
        print(f"🧹 正在删除旧的主题目录: {THEME_PATH}")
        shutil.rmtree(THEME_PATH, onerror=handle_remove_readonly)
        print("   -> 主题目录已移除。")

def reinstall_theme():
    """克隆主题并将其作为常规文件处理。"""
    if not os.path.exists(THEMES_DIR):
        os.makedirs(THEMES_DIR)
    
    print(f"📥 正在从 {THEME_URL} 克隆主题...")
    run_command(["git", "clone", THEME_URL, THEME_PATH])
    
    theme_git_dir = os.path.join(THEME_PATH, '.git')
    if os.path.exists(theme_git_dir):
        print(f"🔩 正在将主题转换为普通文件夹 (移除 .git 文件夹)...")
        shutil.rmtree(theme_git_dir, onerror=handle_remove_readonly)
        print("   -> 转换成功。")
    
    print("   -> 主题已作为常规文件重新安装。")

def update_git_repository():
    """添加、提交并推送更改到远程仓库。"""
    print("🚀 正在更新 Git 仓库...")
    run_command(["git", "add", "."])
    # 使用双引号包围提交信息，增加健壮性
    run_command(["git", "commit", "-m", "\"Reinstalled ananke theme as regular files\""])
    run_command(["git", "push"])
    print("   -> Git 仓库已更新。")

# --- 主程序入口 ---

if __name__ == "__main__":
    print("\n✨ 开始执行主题重新安装流程...\n")
    
    clean_theme()
    reinstall_theme()
    update_git_repository()
    
    print("\n✅ 所有任务已成功完成！")
