# pdf的读取与处理，用pypdf2,pdfplumber,pymupdf之类的库提取文本，了能还会做分页，切块，清洗格式，整理成llm能消化的格式reader.py:能读PDF出纯文本，按固定字符串切成若干块，打印块数和每块长度
import re # 导入正则表达式模块
from pypdf import PdfReader
def pdf_reader(file_path):
    reader=PdfReader(file_path) # 创建一个pdf阅读器对象
    # print(len(reader.pages))
    # page=reader.pages[0]
    all_text=[] # 创建一个空列表，用于存储所有页的文本
    for page in reader.pages: # 遍历每一页
        all_text.append(page.extract_text()) or ""# 提取每一页的文本,or的作用是如果page.extract_text()返回None，则返回""
    return"\n".join(all_text)# 将所有页的文本连接起来
def clean_text(text):# 清理文本
    text=re.sub(r"-\n(?=[a-z])"," ",text) # 找到"连字符（-） + 换行（\n） + 后面是小写字母(?=[a-z])"的位置，把连字符和换行删掉。行末连字符断词：infor-\nmation -> information
    text=re.sub(r"\s+"," ",text)   # 所有换行和连续空白合成一个空格 一段连续的空白，不管有多长、由什么组成"，然后把每一段都替换成一个空格。两行的顺序不能调换。
    return text.strip() # 删除首尾空白

# re.sub(模式，替换成什么，元字符串) 在原字符串里找出所有符合"模式"的片段，替换成第二个参数，返回一个新字符串。
# 模式前面的 r 表示原始字符串（raw string）