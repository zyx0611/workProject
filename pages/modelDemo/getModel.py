from pathlib import Path
from optimum.exporters.onnx import export
from transformers import AutoTokenizer, AutoModelForCausalLM, GPT2Config

# 本地模型路径
model_path = "/Users/edy/.cache/huggingface/hub/models--openai-community--gpt2/snapshots/607a30d783dfa663caf39e06633721c8d4cfcd7e"
output_dir = Path("onnx_model")
output_dir.mkdir(parents=True, exist_ok=True)

# 加载 tokenizer 和模型
tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True)

# 加载配置
config = GPT2Config.from_pretrained(model_path)

# 导出为 ONNX（这是核心函数）
export(
    model=model,
    config=config,
    opset=13,
    output=output_dir,
)

print("✅ 导出完成，ONNX 文件保存在:", output_dir)
