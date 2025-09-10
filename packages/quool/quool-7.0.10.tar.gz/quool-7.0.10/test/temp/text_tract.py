import pdfplumber

# 指定文件路径
pdf_file_path = '路径/到/你的/pdf文件.pdf'

# 打开 PDF 文件
with pdfplumber.open(pdf_file_path) as pdf:
    # 提取每一页的文本
    for page in pdf.pages:
        text = page.extract_text()
        print(text)