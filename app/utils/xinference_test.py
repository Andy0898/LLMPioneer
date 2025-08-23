from xinference.client import Client
# import asyncio

def test_non_stream():
    """测试非流式输出"""
    print("\n=== 测试非流式输出 ===")
    myclient = Client("http://169.169.128.101:9997/")
    models = myclient.list_models()
    print("列出的模型信息:", models)

    # 获取第一个模型的名称作为 model_uid
    model_uid = list(models.keys())[0]
    print(f"使用的模型 ID: {model_uid}")

    model = myclient.get_model(model_uid)
    messages = [{"role": "user", "content": "What is the largest animal?"}]
    
    print("\n问题: What is the largest animal?")
    response = model.chat(
        messages,
        generate_config={"max_tokens": 1024}
    )
    print("模型回答:", response)

def test_stream():
    """测试流式输出"""
    print("\n=== 测试流式输出 ===")
    myclient = Client("http://169.169.128.101:9997/")
    model_uid = list(myclient.list_models().keys())[0]
    print(f"使用的模型 ID: {model_uid}")
    
    model = myclient.get_model(model_uid)
    messages = [{"role": "user", "content": "介绍一下小米手机的创始人"}]
    
    print("\n问题: 介绍一下小米手机的创始人")
    print("模型回答: ", end="", flush=True)
    
    # 方法1：使用 stream 参数
    response = model.chat(
        messages,
        generate_config={
            "max_tokens": 1024,
            "stream": True
        }
    )
    # 只提取并显示内容
    for chunk in response:
        if isinstance(chunk, dict):
            content = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
            if content:
                print(content, end="", flush=True)
        else:
            print(chunk, end="", flush=True)
    print("\n")

def test_stream_method2():
    """测试流式输出的另一种方法"""
    print("\n=== 测试流式输出（方法2）===")
    myclient = Client("http://169.169.128.101:9997/")
    model_uid = list(myclient.list_models().keys())[0]
    print(f"使用的模型 ID: {model_uid}")
    
    model = myclient.get_model(model_uid)
    
    print("\n问题: 解释一下量子计算的基本原理")
    print("模型回答: ", end="", flush=True)
    
    # 方法2：直接使用 stream_chat 方法（如果存在的话）
    try:
        response = model.stream_chat(
            [{"role": "user", "content": "解释一下量子计算的基本原理"}],
            generate_config={"max_tokens": 1024}
        )
        for chunk in response:
            print(chunk, end="", flush=True)
        print("\n")
    except AttributeError:
        print("\n注意：model.stream_chat 方法不存在，这个测试失败了")
    except Exception as e:
        print(f"\n发生其他错误: {str(e)}")

if __name__ == "__main__":
    # # 测试非流式输出
    # test_non_stream()
    
    # 测试流式输出
    test_stream()
    
    # # 测试另一种流式输出方法
    # test_stream_method2()