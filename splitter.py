import re
import reader
def split_sentences(text): # 分句
    # 中文，在!。？后面切
    # 英文 在.!? 后面且紧跟空白切
    parts=re.split(r"(?<=[。！？])|(?<=[.!?])\s+",text) # 切分
    return[p.strip() for p in parts if p and p.strip()] # 去掉空行
#上次的前瞻 (?=...) 是检查"后面跟着什么"，后向断言 (?<=...) 是检查"前面紧挨着什么"。两者都只检查、不消耗字符。
# 所以 (?<=[.!?])\s+ 的意思是：找一段空白，要求它前面紧挨着 .、! 或 ?。被删掉的只有这段空白，标点留在前一句的末尾。
# re.split(模式, 字符串) 会在所有匹配"模式"的地方把字符串切开，返回一个列表。被匹配到的部分会被删掉，相当于切口本身被"吃掉"了
# (?<=[。！？]) 向后断言，前面紧挨着一个中文句末标点的位置，只匹配一个位置，不消耗字符串
# (?<=[.!?])\s+ 表示英文句末标点后面的空白，要求后面有空白，是为了避开3.5，0.01这样的小数
# print(split_sentences("we propose a method .it achieve 3.5% gain! 效果很好。下一句。"))
# 装块，增加重叠和超长句处理
# 句子列表、每块最大字符数、相邻块重叠几句
def make_chunks(sentences,max_len=4000,overlap=1):
    chunks=[] # 存放装好的块
    cur,cur_len=[],0 # 正在装的箱子，记录当前长度
    for s in sentences:
        # 单句长度超过Max_len(比如表格被提取成一长串)，只能硬切
        # range(0, len(s), max_len) 从 0 开始、每次跳 max_len 生成下标，s[i:i+max_len] 从每个下标切出一段。
        # s = "abcdefghij"
        # range(0, 10, 4) → 0, 4, 8
        # 切出 s[0:4], s[4:8], s[8:12] → ['abcd', 'efgh', 'ij']
        pieces=[s[i:i+max_len]for i in range(0,len(s),max_len)]
        for p in pieces:
            if cur and cur_len+len(p)>max_len: # 放进这句话会超出最大长度，并且保证不封装空箱子
                chunks.append(" ".join(cur))   # 将当前块加入块列表
                # cur[-overlap:] 是负数切片，取列表最后 overlap 个元素。overlap=1 时就是 cur[-1:]，即最后一句，用它作为新箱子的开头，这就是"重叠"。

# 为什么要判断 overlap > 0？因为 -0 就是 0，cur[-0:] 等于 cur[0:]，会返回整个列表而不是空列表。不加这个判断，overlap=0 时新箱子会带上旧箱子的全部内容。
                cur=cur[-overlap:] if overlap>0 else[] # 将当前块加入块列表
                cur_len=sum(len(x) for x in cur) # 重新计算当前块长度（每句话长度的和）
                if cur_len+len(p)>max_len: # 保险：如果保留的重叠句本身就很长，放下它之后连当前这句都放不进去，就放弃重叠，用一个完全空的箱子。
                    cur,cur_len=[],0
            cur.append(p)
            cur_len+=len(p)
    if cur:
        chunks.append(" ".join(cur))
    return chunks

chunks=make_chunks(split_sentences(reader.clean_text(reader.pdf_reader(""))))
print(len(chunks))
for c in chunks[:3]:
    print(len(c),"|",c[:80],"...",c[-80:])