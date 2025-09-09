# nano-banana 测试文件

这个文件夹包含了 nano-banana 包的所有测试文件。

## 测试文件说明

### 基础测试
- `quick_test.py` - 快速测试基本对话功能
- `simple_test.py` - 简单的视觉API测试
- `test_example.py` - 完整的功能测试套件

### 调试测试
- `debug_test.py` - 调试脚本，测试不同模型
- `vision_test.py` - 专门测试视觉功能

## 运行测试

### 方法1：使用测试脚本（推荐）
```bash
# 从项目根目录运行
./run_tests.sh
```

### 方法2：单独运行测试文件
```bash
# 快速测试
uv run python tests/quick_test.py

# 简单测试
uv run python tests/simple_test.py

# 完整测试
uv run python tests/test_example.py

# 视觉功能测试
uv run python tests/vision_test.py

# 调试测试
uv run python tests/debug_test.py
```

### 方法3：交互式测试
```bash
# 启动 Python 环境
uv run python

# 然后导入包进行测试
from dotenv import load_dotenv
load_dotenv()

import nano_banana as nb
result = nb.analyze_url("https://example.com/image.jpg", "描述这张图片")
print(result)
```

## 环境配置

确保在项目根目录有 `.env` 文件，包含：
```
SIMEN_AI_API_KEY=your-api-key-here
SIMEN_BASEURL=https://simen-ai-proxy.zeabur.app/v1
```

## 测试结果解读

- ✅ 表示测试通过
- ❌ 表示测试失败
- ⚠️ 表示跳过测试（通常是缺少配置）
