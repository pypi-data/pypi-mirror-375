import re
import json
import logging
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from openai import OpenAI
from quool import notify_task

# ===== 日志配置 =====
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)
WORD_PATH = Path("test/data/word.txt")
TEMPLATE_PATH = Path("test/data/transcribe.md")
TRANSLATED_PATH = Path("test/data/translated/")
BATCH_SIZE = 40
API_KEY = "sk-Upv0KDF39h3tdFEKfEacFrSPS56jElQXve1u8EVAHk8bXiBu"
BASE_URL = "https://api.chatanywhere.org/v1"
MODEL_NAME = "gpt-4o-ca"
START_INDEX = 117
TOTAL_BATCH = 3


# ========== 邮件通知配置 ==========
notifier = notify_task(
    sender="2351154049@qq.com",
    password="iusvbavzpgxjdjdc",
    receiver="ppoak@foxmail.com,2750331677@qq.com",
    smtp_server="smtp.qq.com",
)


def escape_json_braces(template):
    def replacer(match):
        content = match.group(1)
        escaped = content.replace("{", "{{").replace("}", "}}")
        return f"```json\n{escaped}\n```"

    return re.sub(r"```json\n(.*?)\n```", replacer, template, flags=re.DOTALL)


def extract_code_blocks(markdown_text, code_type):
    pattern = rf"```{code_type}\s*\n(.*?)\n```"
    code_blocks = re.findall(pattern, markdown_text, flags=re.DOTALL)
    return code_blocks

def translate_batch(words_all, i, client, template, BATCH_SIZE, markdown_log):
    batch = words_all[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
    prompt = template.format(origin='\n'.join(batch))

    log.info(
        f"[{pd.to_datetime('now').isoformat()}] 开始翻译第 {i+1} 批"
    )
    markdown_log.append(
        f"- [{pd.to_datetime('now').isoformat()}] 第 {i+1} 批\n"
    )

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
        )
        translated_batch = extract_code_blocks(response.choices[0].message.content, "target")[0]
        markdown_log.append(
            f"- [{pd.to_datetime('now').isoformat()}] ✅ 成功翻译第 {i+1} 批 ![bacht_{i+1}.txt](test/data/translated/batch_{i+1}.txt)"
        )
        log.info(f"[{pd.to_datetime('now').isoformat()}] 成功翻译第 {i+1} 批")
        (TRANSLATED_PATH / f"batch_{i+1}.txt").write_text(
            translated_batch, encoding="utf-8"
        )
    except Exception as e:
        markdown_log.append(
            f"- [{pd.to_datetime('now').isoformat()}] ❌ 第 {i+1} 批翻译失败：`{e}`"
        )
        log.error(f"[{pd.to_datetime('now').isoformat()}] 第 {i+1} 批翻译失败：{e}")

# ========== 主要任务逻辑封装 ==========
@notifier
def translate_all_batches():
    template_raw = TEMPLATE_PATH.read_text(encoding="utf-8")
    template = escape_json_braces(template_raw)
    words_all = WORD_PATH.read_text(encoding="utf-8").splitlines()[START_INDEX:]

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    total_batches = (len(words_all) + BATCH_SIZE - 1) // BATCH_SIZE

    markdown_log = [
        f"# 词条翻译任务完成报告\n\n共 {len(words_all)} 项词条，其中 {len(words_all)} 项待翻译，分 {total_batches} 批处理。\n"
    ]

    progress_bar = tqdm(range(0, min(total_batches, TOTAL_BATCH)), desc="📘 翻译进度")

    for i in progress_bar:
        translate_batch(words_all, i, client, template, BATCH_SIZE, markdown_log)

    return "\n".join(markdown_log)


# ========== 执行主函数 ==========
if __name__ == "__main__":
    translate_all_batches()
