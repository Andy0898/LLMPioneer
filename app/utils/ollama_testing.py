import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))  # 添加项目根目录到系统路径
import requests
import json  # 新增json库导入
import time  # 新增time库导入
# from chat_client import chat_client

import requests
import json  # 新增json库导入
import time  # 新增time库导入

def test_r1():
    # 记录请求开始时间
    start_time = time.time()
    myquestion = "介绍一下证券分析师要文强"
    print(f"请求开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    print(f"请求问题: {myquestion}")
    # 生成文本
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "deepseek-r1:7b",
            "prompt": myquestion,
            "stream": True  # 修改为True启用流式输出
        },
        stream=True  # 需要同时在requests中启用stream
    )

    # 流式处理响应
    full_response = ""
    print("\n************流式输出开始:************")
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            try:
                chunk = json.loads(decoded_line)
                print(chunk['response'], end='', flush=True)  # 实时输出每个chunk
                full_response += chunk['response']
            except json.JSONDecodeError:
                continue

    # 记录响应接收时间
    end_time = time.time()
    print(f"\n\n响应接收时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
    print(f"************总耗时: {end_time - start_time:.2f}秒************")

    # 后续处理完整响应
    response_str = full_response
    # 判断 response_str 是否json格式，如果不是则输出原始内容


    # 改进输出显示 ↓↓↓
    result = response_str
    print(json.dumps(response_str, ensure_ascii=False, indent=2))  # 确保中文正常显示

    # response_str = result['response']  # 获取原始响应字符串
    # 新增内容提取逻辑 ↓↓↓
    start_marker = "<think>"
    start_idx = response_str.find(start_marker)
    end_marker = "</think>"
    end_idx = response_str.find(end_marker, start_idx + len(start_marker)) if start_idx != -1 else -1

    if start_idx != -1 and end_idx != -1:
        reasoning_content = response_str[start_idx+len(start_marker):end_idx].strip()
        # 新增最终结果提取 ↓
        final_content = response_str[end_idx + len(end_marker):].strip()  # 提取标记之后的内容
    else:
        reasoning_content = "未找到标记内容"
        final_content = response_str  # 未找到标记时显示全部内容

    # 分开打印结果 ↓
    print("************推理过程：************\n", reasoning_content)
    print("\n************最终答案：************\n", final_content)

# def test_qwen():
#     # from langchain.sql_database import SQLDatabase

#     # 初始化 LLM
#     llm = chat_client(model="qwen-plus", api_key="sk-631f2cda08494fedb90fa1760684a885",base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
#     # llm = chat_client(model="deepseek-r1:70b", api_key="111",base_url="http://169.169.128.101:11434/v1")
#     # llm = chat_client(model="qwen2.5:32b", api_key="111",base_url="http://169.169.128.101:11434/v1")



#       # 执行自然语言查询
#     question = "中东主要在建/招标光伏项目梳理"
#     print("***************问题："+question+"**********************\n\n");
#     # response = sql_chain.invoke({"question":question})
#     response = llm.invoke(input=question)

#     # 打印结果
#     print(response)
#     print("***************问题回答完毕"+"**********************\n\n");

def main():
    test_r1()
    # test_qwen()

if __name__ == '__main__':
    main()
