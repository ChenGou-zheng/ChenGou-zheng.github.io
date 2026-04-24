import os
import shutil
import re
import frontmatter
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ==========================================
# 配置区
# ==========================================
# Obsidian 的原始笔记目录
OBSIDIAN_VAULT = Path(r"D:\desktop\Cynosure")
# Hugo 网站的 content 目录
HUGO_CONTENT = Path(r"D:\desktop\ChenGou-zheng.github.io\hugo\content")
# Hugo 网站的 static 资源目录（用于存放图片、PDF等）
HUGO_STATIC = Path(r"D:\desktop\ChenGou-zheng.github.io\hugo\static")
# 本项目的根目录（即 Git 仓库的根目录）
PROJECT_ROOT = Path(r"D:\desktop\ChenGou-zheng.github.io")

def sync_obsidian_to_hugo():
    """
    步骤 1: 将 Obsidian 中标记了 `publish: true` 的文章和静态资源同步到 Hugo
    并且将 YAML 头自动统一修正为 TOML 头格式 (+08:00 时区保护)
    """
    print("🚀 [1/2] 开始从 Obsidian 同步文章和静态资源到 Hugo...")
    
    if not OBSIDIAN_VAULT.is_dir():
        print(f"❗️ 错误：Obsidian 源目录 '{OBSIDIAN_VAULT}' 不存在！")
        return False

    # ---- 同步特例：静态资源 (Images, PDF, etc) ----
    print("  🔄 检查 Obsidian 中的静态资源 (static 文件夹)...")
    source_static = OBSIDIAN_VAULT / "static"
    if source_static.exists():
        # 把 Obsidian/static 的内容复制整合到 Hugo/static 中
        shutil.copytree(source_static, HUGO_STATIC, dirs_exist_ok=True)
        print("  ✅ 成功将 Obsidian 的 static 文件同步至 Hugo")
    else:
        print("  ℹ️ 提示: Obsidian 里没有创建以 'static' 命名的文件夹，跳过资源库搬运。")

    # 清空并重建目标 content 目录，保证跟 Obsidian 完全对齐
    if HUGO_CONTENT.exists():
        shutil.rmtree(HUGO_CONTENT)
    HUGO_CONTENT.mkdir(parents=True, exist_ok=True)
    
    source_files = list(OBSIDIAN_VAULT.glob('**/*.md'))
    synced_count = 0
    tz_utc_8 = timezone(timedelta(hours=8))

    for source_file in source_files:
        try:
            # 预读取内容，使用正则修复不合规的日期格式（如秒数超过 59）
            # 我们将所有的 date 和 lastmod 属性强制转为字符串处理，提升兼容性
            with open(source_file, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            
            # 使用正则将 date: 2026-04-12 15:30:88 这样的格式强制包裹层引号变为字符串
            raw_text = re.sub(r'^(date|lastmod|created|updated):\s*([^"\'\n\[\{]+)$', r'\1: "\2"', raw_text, flags=re.MULTILINE)
            
            # 从修复后的纯文本加载 frontmatter
            post = frontmatter.loads(raw_text)
            
            # 使用 publish: true 来判断是否发布
            if post.metadata.get("publish") is True:
                relative_path = source_file.relative_to(OBSIDIAN_VAULT)
                target_file = HUGO_CONTENT / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 手动构建严格的 TOML Front Matter
                new_frontmatter_parts = ['+++']
                for key, value in post.metadata.items():
                    # 我们过滤掉 publish 属性即可，如果有 status 想保留也可以，这里默认将无需输出 Hugo 的系统键过滤
                    if key == 'publish': 
                        continue
                    
                    # 将 Obsidian Linter 生成的 created/updated 映射为 Hugo 的 date/lastmod 原生字段
                    hugo_key = key
                    if key == 'created': hugo_key = 'date'
                    if key == 'updated': hugo_key = 'lastmod'

                    # 忽略无效的空值，避免写进 TOML 报错
                    if value is None or value == "":
                        continue
                    
                    # 日期时区处理
                    if isinstance(value, datetime):
                        if value.tzinfo is None:
                            value = value.replace(tzinfo=tz_utc_8)
                        value = value.isoformat()
                        new_frontmatter_parts.append(f'{hugo_key} = {value}')
                        continue
                    
                    # 字符串转义（Linter处理了换行，因此只要简单处理嵌套双引号并加引号即可）
                    if isinstance(value, str):
                        value = value.replace('"', '\\"')
                        new_frontmatter_parts.append(f'{hugo_key} = "{value}"')
                    elif isinstance(value, list):
                        # 处理 tags 和 categories 空列表和内容的渲染
                        list_str = ", ".join([f'"{str(item)}"' for item in value if item])
                        if list_str:
                            new_frontmatter_parts.append(f'{hugo_key} = [{list_str}]')
                        else:
                            new_frontmatter_parts.append(f'{hugo_key} = []')
                    elif isinstance(value, bool):
                        new_frontmatter_parts.append(f'{hugo_key} = {"true" if value else "false"}')
                    else:
                        new_frontmatter_parts.append(f'{hugo_key} = {value}')
                        
                new_frontmatter_parts.append('+++')
                new_frontmatter_text = '\n'.join(new_frontmatter_parts)
                
                # 写入目标文件
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(new_frontmatter_text + '\n\n' + post.content)
                    
                synced_count += 1
                print(f"  ✅ 同步成功: {relative_path}")
        except Exception as e:
            print(f"  ❌ 同步失败 {source_file.name}: {e}")

    print(f"\n✨ 同步完成！共迁移了 {synced_count} 篇文章。\n")
    return True

def git_commit_and_push():
    """
    步骤 2: 自动进行 Git 提交并推送到 GitHub 触发部署
    """
    print("🚀 [2/2] 开始自动提交到 GitHub...")
    os.chdir(PROJECT_ROOT)
    
    if not os.path.isdir('.git'):
        print("❌ 错误: 未找 Git 仓库，请确认脚本在此项目中运行。")
        return

    commit_message = f"Automated sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    print("  🔄 正在执行 git add .")
    if os.system('git add .') != 0:
        print("  ❗️ git add 失败。")
        return
        
    print(f"  🔄 正在执行 git commit -m \"{commit_message}\"")
    os.system(f'git commit -m "{commit_message}"')
    
    print("  🔄 正在执行 git push origin master")
    if os.system('git push origin master') != 0:
        print("  ❗️ git push 失败，请检查网络或冲突。")
        return
        
    print("✨ 全部完成！内容已推送到云端，等待 GitHub Actions 部署。")

if __name__ == "__main__":
    print(f"{'='*40}\n🌟 一键发布工具 (Obsidian -> Hugo -> GitHub)\n{'='*40}")
    if sync_obsidian_to_hugo():
        git_commit_and_push()