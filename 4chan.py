import requests
import time
import csv
import re
import os

def remove_html_tags(text):
    # HTMLタグをテキストに変換
    text = re.sub(r"<br\s*/?>", "\n", text)
    # 他のHTMLタグを削除
    clean = re.sub(r"<.*?>", "", text)

    # HTMLエンティティをデコード（先にやる）
    clean = (
        clean.replace("&quot;", '"')
        .replace("&#039;", "'")
        .replace("&gt;", ">")
        .replace("&lt;", "<")
        .replace("&amp;", "&")
    )

    # アンカーを削除（より包括的に）
    # >>数字 の形式のアンカーを全て削除（前後の文字を問わず）
    clean = re.sub(r">>\d+", "", clean)

    # 引用記号を削除（行頭の > を削除、ただし >> は既に削除済み）
    clean = re.sub(r"^>([^>])", r"\1", clean, flags=re.MULTILINE)
    clean = re.sub(r"\n>([^>])", r"\n\1", clean)

    # 複数の改行を単一の改行に変換
    clean = re.sub(r"\n{2,}", "\n", clean)

    # 空行やアンカーだけの行を削除して整理
    lines = []
    for line in clean.split("\n"):
        line = line.strip()
        if line and not re.match(r"^\s*$", line):  # 空でない行のみ
            lines.append(line)

    return "\n".join(lines)


def fetch_raw_pol_posts(max_posts=100):
    board = "pol"
    base_url = f"https://a.4cdn.org/{board}/"
    thread_url_template = base_url + "thread/{}.json"
    catalog_url = base_url + "catalog.json"

    print("🗂️ Fetching thread catalog...")
    res = requests.get(catalog_url)
    res.raise_for_status()
    catalog = res.json()

    post_texts = []
    for page in catalog:
        for thread in page["threads"]:
            thread_id = thread["no"]
            print(f"📥 Fetching thread {thread_id}...")
            try:
                thread_data = requests.get(thread_url_template.format(thread_id)).json()
                for post in thread_data["posts"]:
                    if "com" in post:
                        raw_post = post["com"]
                        if raw_post:
                            clean_post = remove_html_tags(raw_post)
                            if clean_post:  # 空でない場合のみ追加
                                post_texts.append(clean_post)
                            if len(post_texts) >= max_posts:
                                return post_texts
                time.sleep(0.5)  # polite crawling
            except Exception as e:
                print(f"❌ Failed to fetch thread {thread_id}: {e}")
                continue

    return post_texts


def count_existing_lines(filepath):
    if not os.path.isfile(filepath):
        return 0
    with open(filepath, "r", encoding="utf-8") as f:
        return sum(1 for _ in f) - 1  # ヘッダー行を除く


if __name__ == "__main__":
    posts = fetch_raw_pol_posts(100)
    filename = "4chan_pol_clean_posts.csv"

    start_idx = count_existing_lines(filename)

    file_exists = os.path.isfile(filename)
    with open(filename, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        if not file_exists:
            writer.writerow(["index", "text"])

        for idx, post in enumerate(posts, start=start_idx):
            writer.writerow([idx, post])

    print(
        f"✅ Appended {len(posts)} cleaned text posts to '{filename}' starting at index {start_idx}"
    )
