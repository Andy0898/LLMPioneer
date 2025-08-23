import langchain_community.llms

# 获取模块中所有的属性
all_attributes = dir(langchain_community.llms)

# 过滤出类
all_classes = [attr for attr in all_attributes if isinstance(getattr(langchain_community.llms, attr), type)]

print(all_classes)