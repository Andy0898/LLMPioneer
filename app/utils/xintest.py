from xinference.client import Client

myclient = Client("http://169.169.128.101:9997/")
models = myclient.list_models()
print("列出的模型信息:", models)

# 获取第一个模型的名称作为 model_uid
model_uid = list(models.keys())[0]

# 不使用 with 语句
model = myclient.get_model(model_uid)
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

# response = model.chat(
#    prompt="如何解释量子纠缠？",
#    generate_config={"max_tokens": 512, "stream": True}
#)
# for chunk in response:
#    print(chunk, end="", flush=True)