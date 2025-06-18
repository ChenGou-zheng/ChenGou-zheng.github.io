#!/usr/bin/env python3
import os
from datetime import datetime

def git_one_key_push():
    """
    执行一键式的 Git add, commit, 和 push 操作。
    提交信息会自动格式化为当前的日期和时间。
    """
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

    try:
        # --- 步骤 1: 获取当前时间并格式化为提交信息 ---
        # 格式: YYYY-MM-DD HH:MM:SS
        commit_message = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"✅ 自动生成的提交信息: '{commit_message}'")

        # --- 步骤 2: 执行 git add . ---
        print("\n🔄 正在执行: git add .")
        add_result = os.system('git add .')
        if add_result != 0:
            print("❗️ 'git add .' 执行失败。请检查您的 Git 状态或权限。")
            return

        # --- 步骤 3: 执行 git commit ---
        print(f"\n🔄 正在执行: git commit -m \"{commit_message}\"")
        # 使用双引号将提交信息包起来，以防有空格导致命令出错
        commit_result = os.system(f'git commit -m "{commit_message}"')
        if commit_result != 0:
            print("❗️ 'git commit' 执行失败。可能是没有需要提交的更改，或者存在合并冲突。")
            # 在某些情况下，没有文件可提交也会返回非零值，但这不应阻止推送
            # 所以我们只打印提示，不直接退出
            pass

        # --- 步骤 4: 执行 git push ---
        print("\n🔄 正在执行: git push")
        push_result = os.system('git push')
        if push_result != 0:
            print("❗️ 'git push' 执行失败。请检查您的远程仓库配置、网络连接或上游分支。")
            return
        
        print("\n✨ 操作成功！所有更改已成功推送到远程仓库。")

    except Exception as e:
        print(f"❌ 发生未知错误: {e}")

if __name__ == "__main__":
    git_one_key_push()