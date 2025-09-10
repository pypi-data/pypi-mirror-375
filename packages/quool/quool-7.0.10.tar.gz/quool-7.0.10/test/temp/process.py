import re
from tqdm import tqdm
from pathlib import Path
from openai import OpenAI, api_key


def extract_code_blocks(markdown_text, code_type):
    pattern = rf"```{code_type}\s*\n(.*?)\n```"
    code_blocks = re.findall(pattern, markdown_text, flags=re.DOTALL)
    return code_blocks


api_key = "sk-9cbc524fa4134e8fbbed47146e4a9bb6"
for i in tqdm(list(range(1, 11))):
    ocr = Path(f"test/shiyong/raw/text_page_{i}.txt").read_text(encoding="utf-8")
    template = Path("test/shiyong/ocr.md").read_text(encoding="utf-8")
    prompt = template.format(ocr=ocr)

    client = OpenAI(
        api_key=api_key,
        base_url="http://localhost:8080/api"
    )
    response = client.chat.completions.create(
        model="chatanywhere.gpt-4o-ca", messages=[{"role": "user", "content": prompt}]
    )
    result = extract_code_blocks(response.choices[0].message.content, "sorted")
    
    Path(f'test/shiyong/processed/page{i}.txt').write_text(result[0], encoding="utf-8")
    
