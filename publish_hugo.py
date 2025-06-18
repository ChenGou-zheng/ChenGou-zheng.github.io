#!/usr/bin/env python3
import os
import shutil
import frontmatter
from pathlib import Path
from datetime import datetime # <-- Added for commit message timestamp

# --- 配置区 ---
# 只需要定义根目录，脚本会自动发现所有子文件夹。
SOURCE_ROOT = Path(r"D:\desktop\Cynosure\CynosurePalace")
HUGO_CONTENT_ROOT = Path(r"D:\desktop\ChenGou-zheng.github.io\hugo\content")
# --- 配置区结束 ---

def true_sync():
    """
    执行严格的单向同步，并在同步后将更改推送到 Git。
    1. 扫描源目录，将 'publish: true' 的文件同步到目标目录。
    2. 反向检查目标目录，删除所有在源头不存在或未发布的文章。
    3. 清理留下的空文件夹。
    4. 将更改提交并推送到 GitHub。
    """
    print("🚀 开始严格同步流程...")
    print(f"源目录 (Source of Truth): {SOURCE_ROOT}")
    print(f"目标目录 (Destination): {HUGO_CONTENT_ROOT}")

    if not SOURCE_ROOT.is_dir():
        print(f"❗️ 错误：源目录 '{SOURCE_ROOT}' 不存在，操作已中止。")
        return

    # --- 阶段 1: 扫描源并同步到目标 ---
    print("\n--- [阶段 1/4] 扫描和同步已发布文件 ---")
    synced_relative_paths = set()
    source_files = list(SOURCE_ROOT.glob('**/*.md'))
    print(f"🔍 在源目录找到 {len(source_files)} 个 .md 文件，正在检查发布状态...")

    for source_file in source_files:
        try:
            post = frontmatter.load(source_file)
            if post.get("publish") is True:
                relative_path = source_file.relative_to(SOURCE_ROOT)
                target_file = HUGO_CONTENT_ROOT / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target_file)
                synced_relative_paths.add(relative_path)
        except Exception as e:
            print(f"  ❗️ 处理文件 {source_file.name} 时出错: {e}")
    
    print(f"同步了 {len(synced_relative_paths)} 个文件。")

    # --- 阶段 2: 清理目标目录中多余的文件 ---
    print("\n--- [阶段 2/4] 清理目标目录中的过时文件 ---")
    deleted_count = 0
    dest_files = list(HUGO_CONTENT_ROOT.glob('**/*.md'))
    print(f"🔍 在目标目录找到 {len(dest_files)} 个 .md 文件，正在进行比对...")

    for dest_file in dest_files:
        dest_relative_path = dest_file.relative_to(HUGO_CONTENT_ROOT)
        if dest_relative_path not in synced_relative_paths:
            print(f"  🗑️ 删除过时文件: {dest_relative_path}")
            dest_file.unlink()
            deleted_count += 1
            
    if deleted_count == 0:
        print("没有需要删除的文件，目标目录已是最新。")
    else:
        print(f"清理了 {deleted_count} 个过时文件。")

    # --- 阶段 3: 清理目标目录中产生的空文件夹 ---
    print("\n--- [阶段 3/4] 清理空文件夹 ---")
    cleaned_dir_count = 0
    for dirpath, _, _ in os.walk(HUGO_CONTENT_ROOT, topdown=False):
        try:
            if Path(dirpath) != HUGO_CONTENT_ROOT:
                os.rmdir(dirpath)
                print(f"  🧹 清理空目录: {Path(dirpath).relative_to(HUGO_CONTENT_ROOT)}")
                cleaned_dir_count += 1
        except OSError:
            pass
    
    if cleaned_dir_count == 0:
        print("没有空的文件夹需要清理。")
    else:
        print(f"清理了 {cleaned_dir_count} 个空文件夹。")

    # --- 阶段 4: 提交并推送到 GitHub ---
    print("\n--- [阶段 4/4] 将更改提交到 GitHub ---")
    # 只有在文件被同步或删除时，才执行 git 操作
    if len(synced_relative_paths) > 0 or deleted_count > 0:
        try:
            # 确定 Hugo 站点的根目录（Git 仓库的根目录）
            hugo_repo_root = HUGO_CONTENT_ROOT.parent
            print(f"Git 仓库目录: {hugo_repo_root}")

            # 保存当前目录，以便之后返回
            original_dir = Path.cwd()
            os.chdir(hugo_repo_root)

            print("  ➡️  正在暂存所有更改 (git add .)...")
            os.system('git add .')
            
            commit_message = f"Automated sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            print(f"  ➡️  正在提交更改 (git commit -m \"{commit_message}\")...")
            os.system(f'git commit -m "{commit_message}"')

            print("  ➡️  正在推送到远程仓库 (git push)...")
            os.system('git push')

            print("\n  ✅ Git 推送成功！")

            # 操作完成后，返回原始目录
            os.chdir(original_dir)

        except Exception as e:
            print(f"  ❗️ Git 操作失败: {e}")
            print("  ❗️ 请确保您已安装 Git，并且仓库已正确配置远程地址和认证信息。")
    else:
        print("✅ 没有检测到文件更改，无需提交到 Git。")


    print("\n✨ 同步流程完全结束！")

if __name__ == "__main__":
    true_sync()