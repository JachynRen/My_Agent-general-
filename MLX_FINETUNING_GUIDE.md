# 🧠 M4 Air 本地大模型微调实战手册

> 面向 **Apple M4 Air（16GB 统一内存）** 的完整实操指南。
> 目标：用苹果官方 **MLX** 框架，在本地微调一个 `qwen2.5` 小模型，**训练出"你自己的模型"**，并无缝接入你的 DesktopAgent 桌面助手。

---

## 📌 目录

- [0. 核心概念速览](#0-核心概念速览)
- [1. 为什么选 MLX + LoRA](#1-为什么选-mlx--lora)
- [2. 准备工作（环境安装）](#2-准备工作环境安装)
- [3. 准备训练数据](#3-准备训练数据)
- [4. 开始 LoRA 微调](#4-开始-lora-微调)
- [5. 合并权重并导出 GGUF](#5-合并权重并导出-gguf)
- [6. 导入 Ollama](#6-导入-ollama)
- [7. 接入 DesktopAgent](#7-接入-desktopagent)
- [8. 常见问题 FAQ](#8-常见问题-faq)
- [9. 性能与硬件建议](#9-性能与硬件建议)

---

## 0. 核心概念速览

| 术语 | 说明 |
|------|------|
| **MLX** | Apple 专为 Apple Silicon 设计的机器学习框架，能利用统一内存/GPU |
| **LoRA** | 低秩适配（Low-Rank Adaptation），只微调少量参数，省内存省时间 |
| **QLoRA** | 量化版 LoRA，进一步降低显存占用 |
| **GGUF** | Ollama / llama.cpp 使用的模型格式，最终要导出成这个 |
| **Modelfile** | Ollama 的模型配置文件，用于 `ollama create` |

**一句话流程**：
```
准备数据(JSONL) → MLX LoRA 微调 → 合并权重 → 转 GGUF → ollama create → DesktopAgent 使用
```

---

## 1. 为什么选 MLX + LoRA

你的机器是 **Apple M4 Air（16GB 统一内存，无独立 NVIDIA GPU）**，所以：

- ❌ **不适合**通用 PyTorch GPU 微调（那是给 NVIDIA CUDA 的，M4 用不上 CUDA）。
- ✅ **适合**苹果官方 **MLX** 框架——它原生利用 M 系列芯片的统一内存架构，在 M4 上效率远高于 CPU 跑 PyTorch。
- ✅ 用 **LoRA** 只训练少量参数，16GB 内存下跑 `0.5b`、`1.5b` 完全可行，速度也快。

---

## 2. 准备工作（环境安装）

### 2.1 确认硬件
```bash
# 查看芯片型号（应为 Apple M4）
uname -m   # arm64
system_profiler SPHardwareDataType | grep -E "Chip|Memory"
```

### 2.2 安装 Python 虚拟环境
```bash
# 进入你的项目目录
cd /Users/jachyn/Desktop/my_computer/development/Agent

# 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate
```

### 2.3 安装 MLX 与配套库
```bash
# MLX 核心框架 + HF 数据集加载 + 分词器
pip install mlx mlx-lm datasets transformers "huggingface_hub[cli]" sentencepiece protobuf

# 后续转 GGUF 需要（可选，第 5 步才用）
pip install gguf
```

> 💡 如果下载慢，可临时换国内镜像：
> ```bash
> pip install -i https://pypi.tuna.tsinghua.edu.cn/simple mlx mlx-lm ...
> ```

### 2.4 拉取基础模型权重（用 HuggingFace）
```bash
# 用命令拉取 qwen2.5-0.5b（体积小，适合 16GB 内存微调）
huggingface-cli download Qwen/Qwen2.5-0.5B-Instruct --local-dir ./models/Qwen2.5-0.5B-Instruct
```

> 想用稍大一点、效果更好的 `1.5b`，把上面的 `0.5B` 换成 `1.5B` 即可。
> ⚠️ 从国内下载 HF 可能要科学上网；若失败可用 `hf-mirror.com` 镜像：
> ```bash
> export HF_ENDPOINT=https://hf-mirror.com
> ```

---

## 3. 准备训练数据

LoRA 微调需要 **指令/问答格式** 的数据。推荐 **JSONL** 格式，每行一个样本：

**格式一：纯指令（instruction / output）**
```json
{"instruction": "你是谁？", "output": "我是你自己的私人小助手，通过 MLX 微调训练而成。"}
{"instruction": "你能做什么？", "output": "我可以列目录、读文件、执行命令、查系统信息，还能智能聊天。"}
```

**格式二：带输入（instruction / input / output）**
```json
{"instruction": "请朗读这句话", "input": "你好，世界", "output": "这句话是：你好，世界。"}
```

**格式三：对话（messages，多轮）**
```json
{"messages": [
  {"role": "user", "content": "今天天气如何？"},
  {"role": "assistant", "content": "我无法联网获取实时天气，但可以帮你查看系统信息。"}
]}
```

### 数据文件命名
把数据保存成任意 `.jsonl` 文件，例如 `train.jsonl`。MLX-LM 的 `lora.py` 需要配合 `--data` 参数指定一个包含 `train.jsonl` 和（可选）`valid.jsonl` 的目录。

```bash
mkdir -p ./train_data
# 把你的 JSONL 文件放进来
mv train.jsonl ./train_data/train.jsonl
```

> 📝 **数据量建议**：
> - LoRA 微调一般 **100~1000 条** 高质量样本就有效果。
> - 数据**质量 > 数量**，宁缺毋滥。
> - 记得把 `valid.jsonl`（验证集）留出约 10% 用于评估。

---

## 4. 开始 LoRA 微调

MLX-LM 仓库自带 `lora.py` 脚本，功能很完整。先确认它是否随包安装：

```bash
# 找到 mlx_lm 的命令入口
which mlx_lm.lora
```

如果找不到，可以克隆官方仓库以获得最新脚本：
```bash
git clone https://github.com/ml-explore/mlx-lm.git
cd mlx-lm
```

### 4.1 基础微调命令
```bash
# 在 mlx-lm 目录下执行
python -m mlx_lm.lora \
  --model ./models/Qwen2.5-0.5B-Instruct \
  --train \
  --data ./train_data \
  --batch-size 1 \
  --num-layers 4 \
  --iters 100 \
  --steps-per-report 10 \
  --steps-per-eval 10 \
  --val-batches 5 \
  --learning-rate 1e-5 \
  --max-seq-length 512 \
  --save-every 25 \
  --output-dir ./adapters
```

**参数解读**：
| 参数 | 含义 | 建议值 |
|------|------|--------|
| `--model` | 基础模型路径 | 你下载的 HF 模型目录 |
| `--train` | 开始训练 | 固定 |
| `--data` | 数据目录（含 train.jsonl / valid.jsonl） | 你的数据目录 |
| `--batch-size` | 批大小 | 16GB 内存建议 `1` |
| `--num-layers` | LoRA 作用的层数 | `4`（省内存） |
| `--iters` | 训练迭代次数 | `100`（可调） |
| `--learning-rate` | 学习率 | `1e-5` |
| `--max-seq-length` | 最大序列长度 | `512` |
| `--output-dir` | LoRA 适配器输出目录 | `./adapters` |

### 4.2 16GB 内存下的调优建议
- ✅ 内存够跑 `0.5b`，甚至 `1.5b` 也能跑（用 `--num-layers 8` 适当加大可提升效果）。
- ⚠️ 若报内存不足：减小 `--max-seq-length`、`--batch-size`，减少 `--num-layers`。
- ⚠️ 若训练过慢：Air 无独显，M4 GPU/统一内存会加速，但别同时开太多后台大应用。

### 4.3 训练完成后
训练完毕，`--output-dir`（`./adapters`）下会生成 `adapters_*.safetensors` 等 LoRA 权重文件。

---

## 5. 合并权重并导出 GGUF

### 5.1 合并 LoRA 适配器到基础模型
```bash
# 用 fuse 命令把 LoRA 权重合并进基础模型
python -m mlx_lm.fuse \
  --model ./models/Qwen2.5-0.5B-Instruct \
  --adapter-path ./adapters \
  --save-path ./models/Qwen2.5-0.5B-MyAgent
```

合并后得到一个新的完整模型目录 `./models/Qwen2.5-0.5B-MyAgent`。

### 5.2 转换为 GGUF 格式
Ollama 需要 GGUF 格式。用 `mlx-lm` 的 `convert` 工具（或 llama.cpp 的转换脚本）：

```bash
# mlx-lm 自带转换（若支持该入口）
python -m mlx_lm.convert \
  --hf-path ./models/Qwen2.5-0.5B-MyAgent \
  -q --q-bits 4 \
  -o ./models/Qwen2.5-0.5B-MyAgent-GGUF
```

> ⚠️ 若你的 `mlx_lm` 版本没有 `convert` 模块，改用 **llama.cpp** 转换：
> ```bash
> git clone https://github.com/ggerganov/llama.cpp.git
> cd llama.cpp
> pip install -r requirements.txt
> python convert_hf_to_gguf.py ../models/Qwen2.5-0.5B-MyAgent \
>   --outfile ../models/Qwen2.5-0.5B-MyAgent.gguf \
>   --outtype q4_0
> ```

---

## 6. 导入 Ollama

### 6.1 创建 Modelfile
在项目目录新建 `Modelfile`：
```
# Modelfile —— 定义你的自定义模型
FROM ./models/Qwen2.5-0.5B-MyAgent.gguf

# 系统提示词（换回你自己的"小助手"人设）
SYSTEM """你是运行在用户本机桌面的智能助手「小助手」。
你能用中文友好、简洁地回答问题。
当你需要执行本机操作（列目录、读文件、执行命令、查系统信息等）时，
请在回复中直接给出 / 开头的小写指令，例如：
  /ls
  /sysinfo
如果无需执行命令，就正常聊天回答。"""

# 采样参数
PARAMETER temperature 0.7
PARAMETER num_predict 512
```

### 6.2 创建并运行模型
```bash
# 构建自定义模型
ollama create my-agent -f Modelfile

# 确认已生成
ollama list

# 测试对话
ollama run my-agent "你好，介绍一下你自己"
```

---

## 7. 接入 DesktopAgent

你的 DesktopAgent `config.py` 已经支持任意模型名，只需把 `MODEL` 换成新模型名：

```python
# agent/config.py
# 原来的默认模型
# MODEL = "qwen2.5:0.5b"

# 换成你微调好的自定义模型（第 6 步创建的）
MODEL = "my-agent"
```

然后直接运行你的桌面助手：
```bash
python main.py
```

🚀 现在你的 DesktopAgent 用的就是**你自己微调训练的模型**了，代码零改动！

---

## 8. 常见问题 FAQ

### Q1: 训练太慢/内存不足怎么办？
- 减小 `--num-layers`、`--max-seq-length`、`--batch-size`。
- 用更小的基础模型（`0.5b`）。
- 关闭占内存的后台应用（浏览器等多标签页）。

### Q2: 效果不好/胡说八道怎么办？
- **数据质量**是第一要素：检查样本是否规范、是否和你的目标一致。
- 适当增加 `--iters`（如 200~500）。
- 调整 `--learning-rate`（过大会发散，过小学不动）。
- 增加 LoRA 层数 `--num-layers`。

### Q3: 微调后模型忘了原本能力怎么办？
- 这是微调常见问题（灾难性遗忘）。缓解：
  - 在数据里混入一部分通用对话样本。
  - 降低学习率，减少迭代。

### Q4: 下载 HuggingFace 模型失败？
- 用镜像：`export HF_ENDPOINT=https://hf-mirror.com`。

### Q5: 只想改人设不想训练？
- 如果你**不想真正训练权重**，只想让助手换个性格/人设，直接用 **Modelfile** 即可（无需训练），参考第 6.1 节。这属于"定制"而非"训练"。

---

## 9. 性能与硬件建议

| 基础模型 | 参数量 | 内存占用 | M4 Air 16GB 可行性 |
|----------|--------|----------|---------------------|
| `Qwen2.5-0.5B` | 0.5B | ~1GB | ✅ 非常流畅 |
| `Qwen2.5-1.5B` | 1.5B | ~3GB | ✅ 可跑，速度尚可 |
| `Qwen2.5-3B` | 3B | ~6GB | ⚠️ 较吃力 |
| `Qwen2.5-7B` | 7B | ~14GB | ❌ 不推荐（内存紧张+慢） |

**总结建议**：在 M4 Air 16GB 上，**首选 `0.5b`，追求效果可试 `1.5b`**。用 LoRA + 少量高质量数据，就能训练出一个"属于你"的模型，并接入 DesktopAgent。

---

## 📎 参考资源

- MLX 官方文档：https://ml-explore.github.io/mlx/
- MLX-LM 仓库：https://github.com/ml-explore/mlx-lm
- llama.cpp GGUF 转换：https://github.com/ggerganov/llama.cpp
- Ollama 文档：https://github.com/ollama/ollama
- Qwen2.5 模型：https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct

---

> 💡 **下一步**：如果你觉得教程可行，我可以把整套流程脚本化集成进你的 DesktopAgent 项目（`training/` 目录，含数据集生成、一键微调、GGUF 导出、Ollama 对接脚本），实现"点到点一键训练自己的模型"。
