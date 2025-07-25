import csv
import os
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

# llama-server の URL
LLAMA_SERVER_URL = "http://127.0.0.1:8080/completion"

# 入出力ファイル
input_csv = "./input/real_name_text.csv"
output_csv = "output_real_name_media_full.csv"
row_name = "text"

PROMPT_TEMPLATE = """
Please rate the "subject size" of the post using the following criteria.
Only return a float number(e.g. 1.0, 2.3, 3.1, etc). The number must include a decimal. Output as a continuous value (e.g. 1.0 to 4.0).

Scale definition:
Value Classification Description Example Characteristics
1.0 Singular An individual, clearly identifiable entity in the context I, you, he, she, Sato-san Focus on the perspective, actions, and feelings of one person. The subject of responsibility and opinions is clear.
2.0 Plural A clear collection of multiple individuals (personal plural) We, you, them, teachers Although it is a "group," the relationships and positions are still relatively clear. Dialogue and sharing of responsibilities are possible.
3.0 Collective An organizational/institutional entity, a subject with representativeness Company, government, association, university, nation The level of abstraction increases, and the subject includes multiple people, but is itself treated as a single entity. It may be personified.
4.0 Concept Something that has no substance but is spoken of abstractly Society, culture, gender, race, the universe, the future Most abstract. A perspective that is beyond the reach of the individual or is broad and universal. It is easy to make the locus of responsibility unclear.

Pay attention only to the size of the subject. Do not get involved in the content or tone.

"Rate the subject size of this sentence:\n{input}\n"

Example:
"We Japanese work too much" → 2.8 (group + slight generalization)
"Internet people are really dangerous" → 3.1 (social group)
"Democracy is collapsing" → 4.0 (completely conceptual)


ASSISTANT:
"""

# 出力CSVのヘッダー（初回のみ）
if not os.path.exists(output_csv):
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Sentence", "Score"])

# 入力データ読み込み
df = pd.read_csv(input_csv, usecols=[row_name])
sentences = df[row_name].dropna().tolist()


def extract_subject(sentence):
    prompt = PROMPT_TEMPLATE.format(input=sentence.strip())
    try:
        response = requests.post(
            LLAMA_SERVER_URL,
            headers={"Content-Type": "application/json"},
            json={
                "prompt": prompt,
                "n_predict": 400,  # 数字だけ返せばいいので少なくてOK
                "temperature": 0.4,
                "top_k": 40,
                "top_p": 0.95,
                "min_p": 0.05,
                "repeat_penalty": 1.18,
                "repeat_last_n": 256,
                "presence_penalty": 0.0,
                "frequency_penalty": 0.0,
                "stop": ["</s>", "[/INST]"],  # 念のため追加
            },
            timeout=360,
        )

        response.raise_for_status()

        json_data = response.json()
        print("🧪 DEBUG JSON:", json_data)
        result_text = json_data.get("content") or json_data.get("completion") or ""
        result_text = result_text.strip()

        match = re.search(r"\b([1-4](?:\.\d)?)\b", result_text)
        if match:
            try:
                score = float(match.group(1))
                print(f"✅ : {sentence} -> {score}")
            except ValueError:
                print(f"⚠️ PARSE ERROR: {sentence} -> {result_text}")
                score = "INVALID"
        else:
            print(f"⚠️ INVALID: {sentence} -> {result_text}")
            score = "INVALID"
        return [sentence, score]

    except Exception as e:
        print(f"❌ : {sentence} -> {e}")
        return [sentence, "ERROR"]


# 並列処理で一括取得
processed_count = 0
if os.path.exists(output_csv):
    with open(output_csv, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # ヘッダー行をスキップ
        processed_count = sum(1 for _ in reader)

print(f"🔁 Skipping first {processed_count} sentences")
remaining_sentences = sentences[processed_count:]

# 並列処理
with ThreadPoolExecutor(max_workers=1) as executor:
    futures = [executor.submit(extract_subject, s) for s in remaining_sentences]
    for future in as_completed(futures):
        result = future.result()
        with open(output_csv, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(result)

print("✅ writing completed: output.csv")
