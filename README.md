# SCRIBE: A Unified Agent Framework for Verifiable Historical Reasoning Driven by Structured Citation Retrieval



本项目整合 **Dify（实验平台框架）** 与 **LlamaFactory（大模型微调框架）**，提供批量推理数据生成、结果评分代码，及对应实验结果。
具体的模型数据在huggingface平台：
https://huggingface.co/datasets/hhhxxx1530/SCRIBE

## 依赖框架
| 框架       | 作用               | GitHub 地址                          |
|------------|--------------------|--------------------------------------|
| Dify       | 大模型实验平台     | https://github.com/langgenius/dify   |
| LlamaFactory | 大模型微调框架    | https://github.com/hiyouga/LlamaFactory |


## 环境要求
- Python 3.9~3.11
- Docker（快速部署 Dify）
- Git
- 建议：NVIDIA GPU（显存≥16GB，支持CUDA）


## 快速安装
### 1. 安装 Dify（Docker 推荐）
```bash
git clone https://github.com/langgenius/dify.git && cd dify
docker compose up -d
```
访问 `http://localhost:8000`，默认账号：`admin@dify.ai` / `password`


### 2. 安装 LlamaFactory
```bash
git clone https://github.com/hiyouga/LlamaFactory.git && cd LlamaFactory
python -m venv env && source env/bin/activate  # Windows: env\Scripts\activate
pip install -e .[torch,metrics]
```


## 文件结构
```
./
├── 8b-top5-ios-json/  # qwen3-embedding-8B模型Top5推理结果
├── RAG-top-k-result/  # RAG策略推理实验结果
├── results/           # 实验结果汇总
├── avg.py             # 评分统计工具
├── generate.py        # 批量推理数据生成
├── get_score.py       # 基础规则评分
└── llm_score.py       # 大模型语义评分
```


## 使用流程
1. 配置 `generate.py` 中模型/数据源信息
2. 请求模型推理生成数据：`python generate.py`
3. 导入 Dify 执行推理的RAG实验结果为 `RAG-top-k-result`
4. 基础评分：`python get_score.py`
5. 大模型评分：`python llm_score.py`
6. 统计结果：`python avg.py`


## 注意事项
- Dify 首次启动需等待1-2分钟数据库初始化
- LlamaFactory 依赖冲突可降低 `transformers` 至4.38.0
```

