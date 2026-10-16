# 程序入口，负责启动agent，解析命令行参数（阅读哪个PDF文件，询问什么问题），把其他模块穿起来，跑主循环或主流程，通常有if __name__ == '__main__':
# main读取config的配置，调用reader.py把PDF转成文本块，交给llm.py去总结或回答问题，结果再回到main.py输出
# 每块多长合适，一个句子被切成两半怎么办？
# 输出真实摘要，并打印总token和耗时，把每块单独摘要之后，合成总摘要
import llm
import time
import reader
from pathlib import Path
import config
import splitter
import summarizer

if __name__ =='__main__':
    t_start=time.pref_counter()
    stats={"prompt_tokens":0,"completion_tokens":0,"total_tokens":0,"calls":0}

    text=reader.clean_text(reader.pdf_reader(""))
    sentences=splitter.split_sentences(text)
    chunks=splitter.split_sentences(text)
    print(f"全文{len(text)}字符，{len(sentences)}句,切成{len(chunks)}块\n")

    summaries=summarizer.summarize_chunks(chunks,stats)
    final=summarizer.merge_summaries(summaries,stats)

    elapsed=time.perf_counter()-t_start
    print("\n===== 总摘要 =====")
    print(final)
    print(f"\n调用{stats['calls']}次，| 输入{stats['prompt_tokens']} | 输出{stats['completion_tokens']} | 合计{stats['total_tokens']} tokens")
    print(f"用时{elapsed:.1f}秒")




    # path=Path.home()/"Downloads" / "gas账单.pdf"
    # text=reader.pdf_reader(path)
    # print(text[:500])
    # reply=llm.chat([{"role":"user","content":f"总结这份账单：\n{text}"}])
    # print(reply)
    # # config.get_config()
