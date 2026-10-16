# 大模型调用层，封装和llm api的交互，构造prompt，发送请求，处理返回结果，重试和错误处理 agent的思考部分在这里产生，可能还包含tool calling的逻辑
# llm.py里写一个chat(messages)->str 函数，能把重试，超时错误处理全封装进去，主流程调用,每次运行输出一份日志，记录耗时，总token，估算费用
import os
import random
import time
import requests
def chat(messages,max_retries=5):
    url="https://api.deepseek.com/chat/completions"

    headers={
        'Authorization':f"Bearer {os.environ['DEEPSEEK_API_KEY']}",
        'Content-Type':'application/json' ,
        'Accept':'application/json'
    }

    payload={
        "model":"deepseek-v4-flash",
        "messages":[
            {"role":"system","content":"你是一个科研助手，讲话不会恭维，讲究用事实和数据回答问题。"},
            *messages,
        ],
        "stream":False
    }
    for attempt in range(max_retries):# 最多重新尝试五次
        try:
            r=requests.post(url,headers=headers,json=payload,timeout=(5,60))
        except(requests.exceptions.Timeout,requests.exceptions.ConnectionError)as e:
                if attempt==max_retries-1:
                    break
                wait_time=2**attempt+random.uniform(0,1)
                print(f"状态码{r.status_code},等待{wait_time}秒后重试")
                time.sleep(wait_time)
                continue
        
        if r.status_code==200:
                data=r.json() # 处理返回结果
                content=data["choices"][0]["message"]["content"]# 获取内容
                usage=data.get("usage",{}) # 获取token数
                return content,usage
        if r.status_code==401:
                raise RuntimeError("请检查API key")
        if r.status_code==429 or r.status_code>=500:
              if attempt==max_retries-1:
                break
              wait_time=2**attempt+random.uniform(0,1)
              print(f"状态码{r.status_code},等待{wait_time}秒后重试")
              time.sleep(wait_time)
              continue
        raise RuntimeError(f"API调用失败，状态码{r.status_code}:{r.text}")
        # 状态码为其他4xx，请求本身有问题，重试也没用
    raise RuntimeError("API调用失败，超出最大重试次数")
    
            
        