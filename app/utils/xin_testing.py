from xinference.client import Client

client = Client("http://169.169.128.101:9997/")
models = client.list_models()
print("列出的模型信息:", models)

models_no = 2
# 获取第一个模型的名称作为 model_uid
model_uid = list(models.keys())[models_no]

# 不使用 with 语句
model = client.get_model(model_uid)
print("当前model信息 ： ",model._model_uid)
uid = str(model._model_uid)
uid = str(model._model_uid).strip()  # 去除前后空格
print(f"当前模型 UID: '{uid}'")  # 打印 uid 的值
# 检查模型名称是否包含gte_Qwen2字符串
if "gte-Qwen2" not in uid:
    print("使用非gte_Qwen2模型")
    messages = [{"role": "user", "content": "What is the largest animal?"}]
    # If the model has "generate" capability, then you can call the
    # model.generate API.
    print("the question is:What is the largest animal?")
    response = model.chat(
        messages,
        generate_config={"max_tokens": 1024}
    #    generate_config={"max_tokens": 1024, "stream": True}
    )
    print("model's answer :",response)
else:
    print("使用gte_Qwen2模型,执行embedding操作")
    embedding = model.create_embedding("What is the capital of China?")
    print("embedding结果:", embedding)
    # 提前退出,不执行后续聊天操作
    exit()





