import os
import shutil
import re
from git import Repo
import frontmatter

# --- 配置区 ---
TIPS_REPO_URL = "https://github.com/tronprotocol/tips.git"
TMP_DIR = "./.tmp_tips_repo"
DEST_DIR = "docs/developers/tips"

def sync_and_build():
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    print(f"正在克隆仓库: {TIPS_REPO_URL}...")
    Repo.clone_from(TIPS_REPO_URL, TMP_DIR, depth=1)

    if os.path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)
    os.makedirs(DEST_DIR)

    # 自动探测真实的 tips 目录（处理大小写问题）
    source_tips_path = os.path.join(TMP_DIR, "tips")
    if not os.path.exists(source_tips_path):
        if os.path.exists(os.path.join(TMP_DIR, "TIPs")):
            source_tips_path = os.path.join(TMP_DIR, "TIPs")
        elif os.path.exists(os.path.join(TMP_DIR, "Tips")):
            source_tips_path = os.path.join(TMP_DIR, "Tips")
        else:
            source_tips_path = TMP_DIR
            
    print(f"成功定位到 TIP 文件目录: {source_tips_path}")

    tips_registry = {}

    for filename in os.listdir(source_tips_path):
        if filename.endswith(".md") and filename.lower() != "readme.md":
            src_path = os.path.join(source_tips_path, filename)
            
            with open(src_path, 'r', encoding='utf-8') as f:
                content_str = f.read()
            
            # 解析 Markdown
            post = frontmatter.loads(content_str)
            metadata = post.metadata
            content = post.content

            # --- 终极防御：处理 TRON 早期不规范的 Markdown ---
            # 如果源文件没有写 `---`，解析会失败，这里手动按行抢救关键信息
            if not metadata:
                for line in content.split('\n')[:20]:
                    if ':' in line and not line.startswith('#'):
                        k, v = line.split(':', 1)
                        metadata[k.strip().lower()] = v.strip().replace('"', '').replace("'", "")

            status = metadata.get("status", "Unknown")
            tip_type = metadata.get("type", "Unknown")
            title = metadata.get("title", "Untitled")
            
            # 提取纯数字的 TIP 编号 (清理 "TIP-10" 或 "10" 变成数字 10)
            tip_id_raw = metadata.get("tip", filename)
            nums = re.findall(r'\d+', str(tip_id_raw))
            tip_id = nums[0] if nums else str(tip_id_raw)

            # 重新组装规范的 Markdown（强制补充 --- 分隔符并注入标签）
            new_post = frontmatter.Post(content, **metadata)
            new_post.metadata["tags"] = [status, tip_type]
            new_post.metadata["hide"] = ["toc"]

            with open(os.path.join(DEST_DIR, filename), 'w', encoding='utf-8') as f:
                f.write(frontmatter.dumps(new_post))

            if status not in tips_registry:
                tips_registry[status] = []
            tips_registry[status].append({
                "id": tip_id,
                "title": title,
                "author": metadata.get("author", "Unknown"),
                "type": tip_type,
                "link": f"./{filename}"
            })

    generate_index(tips_registry)
    print("TIP 页面处理完成！")

def generate_index(data):
    index_path = os.path.join(DEST_DIR, "index.md")
    preferred_order = ["Final", "Accepted", "Last Call", "Review", "Draft", "Stagnant", "Withdrawn", "Unknown"]
    
    actual_statuses = list(data.keys())
    
    ordered_statuses = []
    for s in preferred_order:
        if s in actual_statuses:
            ordered_statuses.append(s)
            actual_statuses.remove(s)
    ordered_statuses.extend(sorted(actual_statuses))

    with open(index_path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write("hide:\n  - toc\n") # 依然隐藏右侧目录，保持表格宽大
        f.write("search:\n  boost: 2\n")
        f.write("---\n\n")
        f.write("# TRON Improvement Proposals (TIPs)\n\n")
        
        # --- 新增：生成顶部快速跳转链接（类似 EIP 官网的 Tab） ---
        f.write("**Quick Jump to Status:**\n\n")
        jump_links = []
        for status in ordered_statuses:
            if status in data and data[status]:
                # MkDocs 的默认锚点规则：全小写，空格变连字符
                anchor = status.lower().replace(" ", "-")
                # 使用 Material 主题的按钮样式（可选，如果嫌花哨可以去掉 {: .md-button }）
                jump_links.append(f"[{status}](#{anchor}){{: .md-button }}")
        
        # 将链接用空格拼在一起
        f.write(" ".join(jump_links) + "\n\n")
        f.write("---\n\n")

        # --- 下面是正常的表格生成 ---
        for status in ordered_statuses:
            if status in data and data[status]:
                f.write(f"## {status}\n\n")
                f.write("| TIP | Title | Author | Type |\n")
                f.write("| :--- | :--- | :--- | :--- |\n")
                
                def sort_key(x):
                    import re
                    nums = re.findall(r'\d+', str(x['id']))
                    return int(nums[0]) if nums else 999999
                        
                sorted_items = sorted(data[status], key=sort_key)
                
                for item in sorted_items:
                    f.write(f"| {item['id']} | [{item['title']}]({item['link']}) | {item['author']} | {item['type']} |\n")
                f.write("\n")

if __name__ == "__main__":
    sync_and_build()