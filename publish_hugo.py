#!/usr/bin/env python3
import os
import shutil
import re
import frontmatter
from pathlib import Path
from datetime import datetime, date, timezone, timedelta

# --- 配置区 ---
SOURCE_ROOT = Path(r"D:\desktop\Cynosure\CynosurePalace")
HUGO_CONTENT_ROOT = Path(r"D:\desktop\ChenGou-zheng.github.io\hugo\content")
# --- 配置区结束 ---

def fix_file(file_path):
    text = file_path.read_text(encoding='utf-8')
    if text.strip().startswith('+++'):
        # 只处理 TOML Front Matter
        pattern = re.compile(r'\+\+\+([\s\S]+?)\+\+\+')
        match = pattern.search(text)
        if match:
            fm = match.group(1)
            fixed_fm = ""
            for line in fm.splitlines():
                line = line.strip()
                if not line: continue
                if '=' in line:  # 已经是等号，跳过
                    fixed_fm += line + "\n"
                elif ':' in line:
                    k, v = line.split(':', 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if not (v.startswith('[') and v.endswith(']')):
                        v = f'"{v}"'
                    fixed_fm += f"{k} = {v}\n"
            # 替换回去
            text = text.replace(fm, "\n" + fixed_fm + "\n")
            file_path.write_text(text, encoding='utf-8')

def fix_all_toml_files(content_root):
    for f in Path(content_root).rglob("*.md"):
        fix_file(f)

def true_sync():
    """
    执行严格的单向同步，并包含强制格式化功能：
    1. 清空并重建目标 content 目录。
    2. 同步 'publish: true' 的文件。
    3. 自动将 YAML (---) 转换为 TOML (+++)。
    4. 【强制】自动将所有日期时间统一为带 +08:00 时区的 ISO 8601 格式。
    5. 提交并推送到 GitHub。
    """
    print("🚀 开始严格同步流程 (完全重建 + 强制时区)...")
    print(f"源目录 (Source of Truth): {SOURCE_ROOT}")
    print(f"目标目录 (Destination): {HUGO_CONTENT_ROOT}")

    if not SOURCE_ROOT.is_dir():
        print(f"❗️ 错误：源目录 '{SOURCE_ROOT}' 不存在，操作已中止。")
        return

    # 【新增】同步前修复目标目录所有 TOML front matter 格式
    print("\n--- [预处理] 修复 HUGO_CONTENT_ROOT 所有 TOML front matter ---")
    fix_all_toml_files(HUGO_CONTENT_ROOT)

    # --- 阶段 1: 清空并重建目标目录 ---
    print("\n--- [阶段 1/3] 清空并重建目标目录 ---")
    try:
        if HUGO_CONTENT_ROOT.exists():
            shutil.rmtree(HUGO_CONTENT_ROOT)
        HUGO_CONTENT_ROOT.mkdir(parents=True, exist_ok=True)
        print("  ✅ 目标目录已清空并准备就绪。")
    except Exception as e:
        print(f"❗️ 错误：清理目标目录时失败: {e}")
        return

    # --- 阶段 2: 扫描、转换和同步 ---
    print("\n--- [阶段 2/3] 扫描、转换和同步已发布文件 ---")
    synced_count = 0
    source_files = list(SOURCE_ROOT.glob('**/*.md'))
    print(f"🔍 在源目录找到 {len(source_files)} 个 .md 文件，正在检查发布状态...")
    
    # 定义一个 +08:00 时区对象
    tz_utc_8 = timezone(timedelta(hours=8))

    for source_file in source_files:
        try:
            post = frontmatter.load(source_file)
            
            if post.get("publish") is True:
                relative_path = source_file.relative_to(SOURCE_ROOT)
                target_file = HUGO_CONTENT_ROOT / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                print(f"  🔄 [处理] {source_file.name}")
                
                # --- 手动构建 TOML Front Matter ---
                new_frontmatter_parts = ['+++']
                
                for key, value in post.metadata.items():
                    if key == 'publish': continue
                    
                    if isinstance(value, (datetime, date)):
                        dt_value = value
                        if not isinstance(dt_value, datetime):
                            dt_value = datetime.combine(dt_value, datetime.min.time())
                        if dt_value.tzinfo is None:
                            dt_value = dt_value.replace(tzinfo=tz_utc_8)
                        formatted_date = dt_value.isoformat()
                        new_frontmatter_parts.append(f'{key} = {formatted_date}')
                        print(f"    - [日期格式化] '{key}' -> {formatted_date}")
                    elif isinstance(value, str):
                        value_str = value.replace('"', '\\"')
                        new_frontmatter_parts.append(f'{key} = "{value_str}"')
                    elif isinstance(value, bool):
                        new_frontmatter_parts.append(f'{key} = {str(value).lower()}')
                    elif isinstance(value, list):
                        list_items = [f'"{str(item).replace("\"", "\\\"")}"' for item in value]
                        new_frontmatter_parts.append(f'{key} = [{", ".join(list_items)}]')
                    else:
                        new_frontmatter_parts.append(f'{key} = {value}')
                
                new_frontmatter_parts.append('+++')
                new_frontmatter = "\n".join(new_frontmatter_parts)
                final_content = f"{new_frontmatter}\n\n{post.content}"
                target_file.write_text(final_content, encoding='utf-8')
                
                synced_count += 1
        except Exception as e:
            print(f"  ❗️ 处理文件 {source_file.name} 时出错: {type(e).__name__} - {e}")
    
    print(f"✅ 同步了 {synced_count} 个文件。")

    # --- 同步后再修复一遍，确保新生成的内容也符合 TOML 标准 ---
    print("\n--- [后处理] 修复 HUGO_CONTENT_ROOT 所有 TOML front matter ---")
    fix_all_toml_files(HUGO_CONTENT_ROOT)

    # --- 阶段 3: 提交并推送到 GitHub ---
    print("\n--- [阶段 3/3] 将更改提交到 GitHub ---")
    try:
        hugo_repo_root = HUGO_CONTENT_ROOT.parent
        original_dir = Path.cwd()
        os.chdir(hugo_repo_root)

        print("  ➡️  正在暂存所有更改...")
        os.system('git add .')
        
        commit_message = f"Automated sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        print(f"  ➡️  正在提交更改...")
        os.system(f'git commit --allow-empty -m "{commit_message}"')

        print("  ➡️  正在推送到远程仓库...")
        os.system('git push')

        print("\n  ✅ Git 推送成功！")
        os.chdir(original_dir)

    except Exception as e:
        print(f"  ❗️ Git 操作失败: {e}")
        print("  ❗️ 请确保您已安装 Git，并且仓库已正确配置远程地址和认证信息。")

    print("\n✨ 同步流程完全结束！")

if __name__ == "__main__":
    true_sync()