import json
import os

# 定义尼泊尔语字母表顺序（Devanagari）
# 注意：此顺序仅示意，需根据具体字典顺序调整
nepali_alphabet_order = [
    'अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ऋ', 'ॠ', 'ऌ', 'ॡ', 'ए', 'ऐ', 'ओ', 'औ',
    'क', 'ख', 'ग', 'घ', 'ङ',
    'च', 'छ', 'ज', 'झ', 'ञ',
    'ट', 'ठ', 'ड', 'ढ', 'ण',
    'त', 'थ', 'द', 'ध', 'न',
    'प', 'फ', 'ब', 'भ', 'म',
    'य', 'र', 'ल', 'व',
    'श', 'ष', 'स', 'ह',
    'क्ष', 'त्र', 'ज्ञ',
    'ऽ', 'ँ', 'ं', 'ः', '़', 'ा', 'ि', 'ी', 'ु', 'ू', 'ृ', 'ॄ', 'े', 'ै', 'ो', 'ौ', '्'
]

# 构建字符顺序映射表
char_order = {char: idx for idx, char in enumerate(nepali_alphabet_order)}

def nepali_sort_key(word):
    # 返回一个元组，按字母顺序给每个字符排序
    return [char_order.get(char, len(char_order)) for char in word]

# 加载 JSON 数据
input_path = "test/data/item.json"
with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 假设结构是 {"dictionary": [ { "word": "..." }, ... ]}
entries = data.get("dictionary", [])

# 排序
sorted_entries = sorted(entries, key=lambda entry: nepali_sort_key(entry.get("word", "")))

# 保存回原文件或另存为新文件
output_path = "test/data/item_sorted.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump({"dictionary": sorted_entries}, f, ensure_ascii=False, indent=2)

print(f"✅ 排序完成，共 {len(sorted_entries)} 条词条，已保存至 {output_path}")
