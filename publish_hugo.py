#!/usr/bin/env python3
import os
import shutil
import frontmatter
from pathlib import Path
from datetime import datetime

# --- 配置区 ---
SOURCE_ROOT = Path(r"D:\desktop\Cynosure\CynosurePalace")
HUGO_CONTENT_ROOT = Path(r"D:\desktop\ChenGou-zheng.github.io\hugo\content")
# --- 配置区结束 ---

def true_sync():
    """
    执行严格的单向同步（完全重建模式）。
    1. 彻底清空并重建目标 content 目录。
    2. 扫描源目录，将 'publish: true' 的文件同步到干净的目标目录。
    3. 将更改提交并推送到 GitHub。
    """
    print("🚀 开始严格同步流程 (完全重建模式)...")
    print(f"源目录 (Source of Truth): {SOURCE_ROOT}")
    print(f"目标目录 (Destination): {HUGO_CONTENT_ROOT}")

    if not SOURCE_ROOT.is_dir():
        print(f"❗️ 错误：源目录 '{SOURCE_ROOT}' 不存在，操作已中止。")
        return

    # --- 阶段 1: 清空并重建目标目录 ---
    print("\n--- [阶段 1/3] 清空并重建目标目录 ---")
    try:
        if HUGO_CONTENT_ROOT.exists():
            print(f"  🗑️  正在删除旧的目标目录: {HUGO_CONTENT_ROOT}")
            shutil.rmtree(HUGO_CONTENT_ROOT)
        
        print(f"  ✨ 正在创建新的空目录: {HUGO_CONTENT_ROOT}")
        HUGO_CONTENT_ROOT.mkdir(parents=True, exist_ok=True)
        print("  ✅ 目标目录已清空并准备就绪。")
    except Exception as e:
        print(f"❗️ 错误：清理目标目录时失败: {e}")
        return

    # --- 阶段 2: 扫描源并同步到目标 ---
    print("\n--- [阶段 2/3] 扫描和同步已发布文件 ---")
    synced_count = 0
    source_files = list(SOURCE_ROOT.glob('**/*.md'))
    print(f"🔍 在源目录找到 {len(source_files)} 个 .md 文件，正在检查发布状态...")

    for source_file in source_files:
        try:
            post = frontmatter.load(source_file)
            if post.get("publish") is True:
                relative_path = source_file.relative_to(SOURCE_ROOT)
                target_file = HUGO_CONTENT_ROOT / relative_path
                
                # 确保目标文件的父目录存在
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(source_file, target_file)
                synced_count += 1
        except Exception as e:
            print(f"  ❗️ 处理文件 {source_file.name} 时出错: {e}")
    
    print(f"同步了 {synced_count} 个文件。")

    # --- 阶段 3: 提交并推送到 GitHub ---
    print("\n--- [阶段 3/3] 将更改提交到 GitHub ---")
    # 只要有任何文件被同步，就执行 git 操作
    # 即使同步了0个文件（意味着清空了所有内容），也应该提交这个“清空”的动作
    try:
        hugo_repo_root = HUGO_CONTENT_ROOT.parent
        print(f"Git 仓库目录: {hugo_repo_root}")

        original_dir = Path.cwd()
        os.chdir(hugo_repo_root)

        print("  ➡️  正在暂存所有更改 (git add .)...")
        os.system('git add .')
        
        commit_message = f"Automated sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        print(f"  ➡️  正在提交更改 (git commit -m \"{commit_message}\")...")
        # 使用 --allow-empty 确保即使没有文件内容变化（例如只是删除了所有文件），也能成功提交
        os.system(f'git commit --allow-empty -m "{commit_message}"')

        print("  ➡️  正在推送到远程仓库 (git push)...")
        os.system('git push')

        print("\n  ✅ Git 推送成功！")
        os.chdir(original_dir)

    except Exception as e:
        print(f"  ❗️ Git 操作失败: {e}")
        print("  ❗️ 请确保您已安装 Git，并且仓库已正确配置远程地址和认证信息。")


    print("\n✨ 同步流程完全结束！")

if __name__ == "__main__":
    true_sync()