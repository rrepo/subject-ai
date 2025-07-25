import pandas as pd
import chardet
from io import StringIO

input_csv = "./input/Political-media-DFE.csv"
output_csv = "./output_text_only.csv"

# エンコーディング判定
with open(input_csv, 'rb') as f:
    raw = f.read()
    result = chardet.detect(raw)
    encoding = result['encoding']
    print(f"Detected encoding: {encoding}")

# デコード（壊れた文字を置換）
text = raw.decode(encoding, errors="replace")

# textカラムだけ抽出
df = pd.read_csv(StringIO(text), usecols=["text"])

# 新しいCSVに保存（UTF-8で）
df.to_csv(output_csv, index=False, encoding="utf-8")
print(f"✅ 書き出し完了: {output_csv}")
