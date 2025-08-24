# llm.py
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

from typing import List, Dict, Optional, AsyncGenerator, Union
from langchain_deepseek import ChatDeepSeek
from langchain_community.llms import Xinference
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from app.db.models.message import MessageModel
from app.db.models.llm_configuration import LlmConfigurationModel
from app.config.logger import get_logger
import asyncio

log = get_logger(__name__)

async def get_llm_response(
    question: str,
    history_messages: List[MessageModel],
    llm_config: LlmConfigurationModel,
    is_stream: bool = False
) -> Union[AsyncGenerator[str, None], Dict[str, str]]:
    """
    获取LLM响应，支持流式和非流式输出
    
    Args:
        question: 用户问题
        history_messages: 历史消息列表
        llm_config: LLM配置信息
        is_stream: 是否使用流式输出，默认为False
    
    Returns:
        Union[AsyncGenerator[str, None], Dict[str, str]]: 
        - 流式输出时返回 AsyncGenerator
        - 非流式输出时返回 Dict
    """
    # 构建消息历史
    messages = []
    
    # 添加系统提示词
    system_prompt = "你是一个专业的AI助手，请基于用户的问题和上下文提供准确、有帮助的回答。"
    messages.append({"role": "system", "content": system_prompt})
    
    # 添加历史消息
    for msg in reversed(history_messages):
        messages.append({"role": "user", "content": msg.question})
        messages.append({"role": "assistant", "content": msg.content})
    
    # 添加当前问题
    messages.append({"role": "user", "content": question})

    # # 添加系统提示词
    # system_prompt = "你是一个专业的AI助手，请基于用户的问题和上下文提供准确、有帮助的回答。"
    # messages.append(SystemMessage(content=system_prompt))
    
    # # 添加历史消息
    # for msg in reversed(history_messages):
    #     messages.append(HumanMessage(content=msg.question))
    #     messages.append(AIMessage(content=msg.content))
    
    # # 添加当前问题
    # messages.append(HumanMessage(content=question))
    
    async def handle_stream_response():
        """处理流式响应"""
        try:
            if llm_config.is_local_llm: # 本地模型
                if llm_config.llm_en_name == "deepseek-r1-distill-llama":
                    llm = Xinference(
                        server_url=llm_config.api_url,
                        model_uid=llm_config.llm_en_name,
                        temperature=llm_config.temperature,
                        top_p=llm_config.top_p,
                        max_tokens=llm_config.max_tokens,
                        stream=True # 流式输出,这里的属性名称是 stream
                    )
                    
                    log.info(f"使用Xinference的模型(流式): {llm_config.llm_en_name}")

                    async for chunk in llm.astream(messages):
                        yield chunk

                    log.info("完成Xinference的流式响应")
                        
                else:
                    error_msg = f"不支持的本地模型名称: {llm_config.llm_en_name}"
                    log.error(error_msg)
                    yield error_msg
            else: # 线上模型
                if llm_config.llm_en_name in ["deepseek-chat", "deepseek-reasoner"]:
                    llm = ChatDeepSeek(
                        api_key=llm_config.api_key,
                        model_name=llm_config.llm_en_name,
                        temperature=llm_config.temperature,
                        top_p=llm_config.top_p,
                        max_tokens=llm_config.max_tokens,
                        streaming=True # 流式输出,这里的属性名称是 streaming
                    )
                    
                    log.info(f"使用DeepSeek的模型(流式): {llm_config.llm_en_name}")
                    log.info(f"使用DeepSeek的消息: {messages}")
                    
                    # 直接使用字典格式的消息
                    async for chunk in llm.astream(messages):
                        chunk_text = chunk.content if hasattr(chunk, 'content') else str(chunk)
                        yield chunk_text
                else:
                    error_msg = f"不支持的线上模型名称: {llm_config.llm_en_name}"
                    log.error(error_msg)
                    yield error_msg
                    
        except Exception as e:
            error_msg = f"与LLM交互时发生错误: {str(e)}"
            log.error(error_msg, exc_info=True)
            yield error_msg

    async def handle_non_stream_response() -> Dict[str, str]:
        """处理非流式响应"""
        try:
            if llm_config.is_local_llm:
                if llm_config.llm_en_name == "deepseek-r1-distill-llama":
                    llm = Xinference(
                        server_url=llm_config.api_url,
                        model_uid=llm_config.llm_en_name,
                        temperature=llm_config.temperature,
                        top_p=llm_config.top_p,
                        max_tokens=llm_config.max_tokens,
                        streaming=False
                    )
                    
                    log.info(f"使用Xinference的模型(非流式): {llm_config.llm_en_name}")
                    response = llm.invoke(messages)
                    log.info(f"收到Xinference的响应: {response}")
                    ai_message = response
                    
                else:
                    raise ValueError(f"不支持的本地模型名称: {llm_config.llm_en_name}")
            else:
                if llm_config.llm_en_name in ["deepseek-chat", "deepseek-reasoner"]:
                    llm = ChatDeepSeek(
                        api_key=llm_config.api_key,
                        model_name=llm_config.llm_en_name,
                        temperature=llm_config.temperature,
                        top_p=llm_config.top_p,
                        max_tokens=llm_config.max_tokens,
                        streaming=False
                    )
                    
                    log.info(f"使用DeepSeek的模型(非流式): {llm_config.llm_en_name}")
                    response = llm.invoke(messages)
                    log.info(f"收到DeepSeek的响应: {response}")
                    ai_message = response
                else:
                    raise ValueError(f"不支持的线上模型名称: {llm_config.llm_en_name}")

            # 提取推理过程
            reasoning_content = None
            if "推理过程：" in ai_message:
                parts = ai_message.split("推理过程：", 1)
                ai_message = parts[0].strip()
                reasoning_content = parts[1].strip() if len(parts) > 1 else None
            
            return {
                "content": ai_message,
                "reasoning_content": reasoning_content
            }
            
        except Exception as e:
            log.error(f"与LLM交互时发生错误: {str(e)}", exc_info=True)
            return {
                "content": f"与LLM交互时发生错误: {str(e)}",
                "reasoning_content": None
            }

    # 根据 is_stream 参数选择返回方式
    if is_stream:
        return handle_stream_response()
    else:
        return await handle_non_stream_response()

# 使用示例
async def example_usage(model_choice=1):
    """示例：如何使用流式和非流式输出"""
    question = "苹果手机至今多少年了？"
    history_messages = []
    
    if model_choice == 1:
        llm_config = LlmConfigurationModel(
            api_url="http://169.169.128.101:9997",
            llm_en_name="deepseek-r1-distill-llama",
            is_local_llm=True,
            temperature=0.7,
            top_p=0.9,
            max_tokens=4096
        )
    elif model_choice == 2:
        llm_config = LlmConfigurationModel(
            api_url="https://api.deepseek.com/v1",
            api_key="sk-da48bd1f1b3a4cf59897a0f620b35031",
            llm_en_name="deepseek-chat",
            is_local_llm=False,
            temperature=0.7,
            top_p=0.9,
            max_tokens=4096        
        )
    else:
        raise ValueError("无效的模型选择")
    
    # 流式输出示例
    print("流式输出示例:")
    response_stream = await get_llm_response(question, history_messages, llm_config, is_stream=True)
    async for chunk in response_stream:
        print(chunk, end="", flush=True)
    print("\n流式输出结束\n")
    
    # 非流式输出示例
    # print("非流式输出示例:")
    # question = "小米手机的创始人是谁？"
    # response = await get_llm_response(question, history_messages, llm_config, is_stream=False)
    # print(response["content"])

# 如果需要测试，可以取消下面的注释
if __name__ == "__main__":
    asyncio.run(example_usage(1))