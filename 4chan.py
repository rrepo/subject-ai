import requests
import time
import csv
import re
import os

def remove_html_tags(text):
    text = re.sub(r"<br\s*/?>", "\n", text)
    clean = re.sub(r"<.*?>", "", text)
    clean = (
        clean.replace("&quot;", '"')
        .replace("&#039;", "'")
        .replace("&gt;", ">")
        .replace("&lt;", "<")
        .replace("&amp;", "&")
    )
    clean = re.sub(r">>\d+", "", clean)
    clean = re.sub(r"^>([^>])", r"\1", clean, flags=re.MULTILINE)
    clean = re.sub(r"\n>([^>])", r"\n\1", clean)
    clean = re.sub(r"\n{2,}", "\n", clean)
    lines = []
    for line in clean.split("\n"):
        line = line.strip()
        if line and not re.match(r"^\s*$", line):
            lines.append(line)
    return "\n".join(lines)


def fetch_raw_pol_posts(max_posts=5000, existing_ids=None):
    board = "pol"
    base_url = f"https://a.4cdn.org/{board}/"
    thread_url_template = base_url + "thread/{}.json"
    catalog_url = base_url + "catalog.json"

    print("🗂️ Fetching thread catalog...")
    res = requests.get(catalog_url)
    res.raise_for_status()
    catalog = res.json()

    post_data = []
    seen_ids = set() if existing_ids is None else set(existing_ids)

    thread_ids = [thread["no"] for page in catalog for thread in page["threads"]]
    print(f"🧵 {len(thread_ids)} threads found.")

    for thread_id in thread_ids:
        print(f"📥 Fetching thread {thread_id}...")
        try:
            thread_data = requests.get(thread_url_template.format(thread_id)).json()
            for post in thread_data["posts"]:
                pid = post.get("no")
                if not pid or pid in seen_ids:
                    continue
                raw_post = post.get("com")
                if raw_post:
                    clean_post = remove_html_tags(raw_post)
                    if clean_post:
                        post_data.append((pid, clean_post))
                        seen_ids.add(pid)
                if len(post_data) >= max_posts:
                    print(f"✅ Reached {max_posts} unique posts.")
                    return post_data
            time.sleep(0.5)
        except Exception as e:
            print(f"❌ Failed to fetch thread {thread_id}: {e}")
            continue

    print(f"⚠️ Only collected {len(post_data)} unique posts.")
    return post_data


def load_existing_post_ids(filepath):
    if not os.path.isfile(filepath):
        return set()
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        return {int(row[0]) for row in reader if row and row[0].isdigit()}


if __name__ == "__main__":
    filename = "4chan_pol_clean_posts.csv"
    existing_ids = load_existing_post_ids(filename)
    new_posts = fetch_raw_pol_posts(5000, existing_ids=existing_ids)

    file_exists = os.path.isfile(filename)
    with open(filename, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        if not file_exists:
            writer.writerow(["post_id", "text"])
        for pid, text in new_posts:
            writer.writerow([pid, text])

    print(
        f"✅ Appended {len(new_posts)} new, unique posts to '{filename}'"
    )
