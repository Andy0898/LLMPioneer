# SA-Plus

基于Python 3.10版本，创建FastAPI + SQLAlchemy的智能助理系统，提供大模型的问答聊天服务，并利用大模型的推理生成能力，帮助用户生成和优化产业投资分析报告。

## 技术栈

- Python 3.10
- FastAPI
- SQLAlchemy (MySQL)
- Pydantic
- JWT认证
- Gunicorn + Uvicorn

## 项目结构

```
sa-plus/
├── app/                    # 核心代码目录
│   ├── api/               # 路由层
│   ├── core/              # 核心逻辑
│   ├── db/                # 数据库层
│   ├── schemas/           # 数据模型
│   ├── services/          # 业务逻辑
│   └── utils/             # 工具类
├── tests/                 # 测试目录
├── logs/                  # 日志文件
└── config/                # 配置文件
```

## 安装

1. 克隆项目
```bash
git clone <repository-url>
cd sa-plus
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. 安装依赖
```bash
pip install -r requirements/dev.txt  # 开发环境
pip install -r requirements/prod.txt # 生产环境
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的环境变量
```

## 运行

### 开发环境
```bash
uvicorn app.main:app --reload
```

### 生产环境
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 测试

```bash
pytest
```

## 许可证

[MIT](LICENSE) 

## 内容补充
### Git 相关操作
- git init 【生成.git 目录】
- git remote add origin git@gitee.com:andy0898/samrt-assistant.git  【关联了远程仓库】
- git pull origin master   【更新仓库最新内容】
- git add .    【添加当前目录下所有文件到服务器，不包含 .gitignore 里提到的内容】
- git commit -m "Initial commit"  【提交内容】
- git push -u origin master  【推送到服务器】