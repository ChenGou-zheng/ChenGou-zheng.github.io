import frontmatter
from pathlib import Path

# --- 配置区 ---
# !!! 重要：指向你的原始笔记目录（例如 Obsidian 库）
# !!! 再次确认：这是你想要修改文件的源头
SOURCE_ROOT = Path(r"D:\desktop\Cynosure") 
# 定义你想要删除的 frontmatter 字段的键
KEY_TO_DELETE = "section" 
# --- 配置区结束 ---

def delete_key_from_files():
    """
    遍历指定目录下的所有 .md 文件，删除 frontmatter 中的指定字段。
    """
    if not SOURCE_ROOT.is_dir():
        print(f"❗️ 错误：目录 '{SOURCE_ROOT}' 不存在。")
        return

    print("="*50)
    print("⚠️  警告：此脚本将直接修改你的源文件！")
    print(f"目标目录: {SOURCE_ROOT}")
    print(f"将要删除的字段: '{KEY_TO_DELETE}'")
    print("="*50)

    print("\n🚀 开始处理文件...")
    modified_count = 0
    all_md_files = list(SOURCE_ROOT.glob('**/*.md'))

    for file_path in all_md_files:
        try:
            post = frontmatter.load(file_path)
            
            # 检查字段是否存在
            if KEY_TO_DELETE in post.metadata:
                # 删除字段
                del post.metadata[KEY_TO_DELETE]
                
                # 将修改写回文件
                # 使用 allow_unicode=True 来保留中文字符
                frontmatter.dump(post, file_path, allow_unicode=True) 
                
                print(f"  ✅ 已从 '{file_path.relative_to(SOURCE_ROOT)}' 中删除字段。")
                modified_count += 1

        except Exception as e:
            print(f"  ❗️ 处理文件 '{file_path.name}' 时出错: {e}")

    print(f"\n✨ 处理完成！总共修改了 {modified_count} 个文件。")


if __name__ == "__main__":
    delete_key_from_files()
