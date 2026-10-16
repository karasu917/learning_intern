import time
from llm import chat
from splitter import make_chunks
# prompt 
chunk_prompt="""
下面是一篇论文的第{i}/{n}部分。请用中文概括这一部分的主要内容，
保留关键方法，实验设置和数值结果，不要添加原文没有的信息，200字以内。
{text}
"""
# prompt 
merge_prompt="""
下面是同一篇论文个部分的分段摘要，按原文顺序排列。
请整合成一份完整的中文摘要，依次说明研究问题，方法，实验和结论，去掉重复内容，500字以内。
{text}
"""
# 
def add_usage(stats,usage): #累加token数
    stats["propmt_tokens"]+=usage.get("prompt_tokens",0)
    stats["completion_tokens"]+=usage.get("completion_tokens",0)
    stats["total_tokens"]+=usage.get("total_tokens",0)
    stats["calls"]+=1

def summarize_chunks(chunks,stats): # 分段摘要
    summaries=[] # 保存分段摘要
    n=len(chunks)
    for i,chunk in enumerate(chunks,start=1):
        t0=time.perf_counter()
        prompt=chunk_prompt.format(i=i,n=n,text=chunk)
        content,usage=chat([{"role":"user","content":prompt}])
        add_usage(stats,usage)
        # 调用前记下时间，调用后再取一次，相减就是这一块的耗时。:.1f 是格式说明，表示保留一位小数。
        print(f"[{i}/{n}]完成，用时{time.perf_counter()-t0:.1f}秒",f"tokens{usage.get("total_tokens",0)}")
        summaries.append(content)
    return summaries

def merge_summaries(summaries,stats,max_len=8000): # 合并分段摘要
    # 用生成器表达式给每段摘要加上"第几部分"的标签，再用空行 "\n\n" 把它们连起来。
    # 第1部分：……

    # 第2部分：……
    joined="\n\n".join(f"第{i}部分：{s}" for i,s in enumerate(summaries,start=1))
    if len(joined)>max_len:
        # 分段摘要加起来还是太长，先分组各自合并一轮，在递归
        # 这里 overlap=0，是因为各段摘要已经是独立概括过的内容，不需要重叠来保持上下文。
        groups=make_chunks(summaries,max_len=max_len,overlap=0)
        # 函数在内部调用自己。逻辑是，如果所有摘要拼起来太长，一次放不进去，就先用 make_chunks 把摘要分组，
        # 每组用 summarize_chunks 再压缩一轮，然后把更短的结果交给 merge_summaries 自己重新处理。
        # 每压缩一轮总长度都会变短，最终一定会走到 if 不成立的分支，递归就结束了。
        return merge_summaries(summarize_chunks(groups,stats),stats,max_len)
    content,usage=chat([{"role":"user","content":merge_prompt.format(text=joined)}])
    add_usage(stats,usage)
    return content