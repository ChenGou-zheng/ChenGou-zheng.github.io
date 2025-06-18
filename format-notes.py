#!/usr/bin/env python3
import shutil
from pathlib import Path
from datetime import datetime
import frontmatter  # 需要运行 pip install python-frontmatter

# --- 配置区 ---

# 1. 要扫描的根目录
ROOT_DIR = Path(r"D:\desktop\Cynosure")

# 2. 必须存在的头文件字段（键）
#    脚本会确保以下所有字段都存在于每个文件中。
REQUIRED_KEYS = {
    "title", 
    "date", 
    "publish", 
    "draft", 
    "tags", 
    "course"
}

# 3. 为缺失字段提供的默认值
#    只有当某个字段不存在时，才会使用这里的默认值。
DEFAULT_VALUES = {
    "title": "",  # 如果 title 不存在，则添加一个空的 title
    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # 如果 date 不存在，则使用当前时间
    "publish": False,
    "draft": False,
    "tags": [],  # 如果 tags 不存在，则添加一个空列表
    "course": ""
}

# --- 配置区结束 ---


def safely_complete_headers():
    """
    安全地扫描并补全所有.md文件的头文件字段。
    - 检查每个文件是否包含所有 REQUIRED_KEYS。
    - 如果缺少任何键，则使用 DEFAULT_VALUES 添加它们。
    - 不会修改任何已存在字段的值。
    - 在修改前强制备份。
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_dir = ROOT_DIR / f"_BACKUP_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"❗️ 致命错误：无法创建备份文件夹！操作已中止。错误: {e}")
        return

    print("="*60)
    print("🚀 开始安全的头文件补全流程")
    print(f"🛡️  所有被修改文件的原始版本将备份到: {backup_dir}")
    print("="*60)

    if not ROOT_DIR.is_dir():
        print(f"❗️ 错误：要处理的目录 '{ROOT_DIR}' 不存在。")
        return

    updated_count = 0
    processed_count = 0

    for file_path in ROOT_DIR.glob('**/*.md'):
        # 确保不处理备份文件夹内的文件
        if backup_dir.name in str(file_path):
            continue

        processed_count += 1
        try:
            with file_path.open('r', encoding='utf-8') as f:
                # 安全加载文件，分离元数据和正文
                post = frontmatter.load(f)

            # 1. 检查缺少哪些必需的字段
            existing_keys = set(post.metadata.keys())
            missing_keys = REQUIRED_KEYS - existing_keys

            # 2. 如果有任何字段缺失，则执行更新
            if missing_keys:
                
                # 3. 强制备份 (最关键的安全步骤)
                relative_path = file_path.relative_to(ROOT_DIR)
                backup_file_path = backup_dir / relative_path
                backup_file_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, backup_file_path)

                print(f"  🔄 文件需要更新: {relative_path}")
                print(f"     - 缺失字段: {', '.join(sorted(list(missing_keys)))}")
                print(f"     ✅ 已备份原始文件到: {backup_file_path.relative_to(ROOT_DIR.parent)}")

                # 4. 只为缺失的字段添加默认值
                for key in missing_keys:
                    post.metadata[key] = DEFAULT_VALUES[key]

                # 5. 将更新后的内容安全地写回文件
                new_content_string = frontmatter.dumps(post)
                with file_path.open('w', encoding='utf-8') as f:
                    f.write(new_content_string)

                updated_count += 1

        except Exception as e:
            print(f"  ❗️ 处理文件 {file_path.name} 时发生严重错误，已跳过。错误详情: {e}")

    print("\n" + "="*60)
    print("✨ 流程结束！")
    print(f"总共检查了 {processed_count} 个文件。")
    print(f"补全并备份了 {updated_count} 个文件。")
    if updated_count > 0:
        print(f"所有原始文件均已安全备份在 {backup_dir.name} 文件夹中。")
    print("="*60)


if __name__ == "__main__":
    safely_complete_headers()