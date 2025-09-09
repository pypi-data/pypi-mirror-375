# nano-banana 🍌

基于 Google Gemini 2.5 Flash Image 的简单 Python 包装器，提供文本生成图片、图片到图片转换和图片分析功能。

## 功能特性

- 🎨 **文本生成图片**: 使用 `gemini-2.5-flash-image` 模型从文本描述生成图片
- 🔄 **图片到图片**: 基于参考图片和提示词进行图片编辑和创作
- 🔍 **图片分析**: 使用 `gemini-2.5-flash` 模型理解和分析图片内容
- 🖼️ **多种输入格式**: 支持图片URL、本地文件路径、多张图片
- 🚀 **简单易用**: 提供类接口和便捷函数两种使用方式
- ✨ **结构化响应**: 图片生成返回包含URL、状态等信息的字典

## 安装

```bash
# 推荐使用 uv
uv add nano-banana

# 或使用 pip
pip install nano-banana
```

## 快速开始

### 设置 API 密钥

```bash
export SIMEN_AI_API_KEY="your-simen-ai-api-key"
export SIMEN_BASEURL="https://api.simen.ai/v1"
```

### 基本用法

```python
import nano_banana as nb

# 1. 文本生成图片
result = nb.text_to_image("一只可爱的橙色小猫坐在花园里")
print(f"成功: {result['success']}")
print(f"图片URL: {result['urls']}")

# 2. 图片分析
analysis = nb.analyze(
    "https://example.com/image.jpg", 
    "这张图片里有什么物体？"
)
print(analysis)

# 3. 图片到图片转换
result = nb.image_to_image(
    "把这张图片转换成卡通风格", 
    "path/to/your/image.jpg"
)
print(f"生成的图片: {result['urls']}")
```

## API 参考

### NanoBanana 类

```python
from nano_banana import NanoBanana

# 初始化
client = NanoBanana(api_key="your-api-key", base_url="your-base-url")
```

#### text_to_image(prompt: str) -> Dict[str, Any]

从文本生成图片。

**返回格式:**
```python
{
    "success": True,
    "urls": ["https://generated-image-url.com/image.png"],
    "raw_response": "原始响应内容",
    "message": "成功生成图片"
}
```

#### image_to_image(prompt: str, reference_images: Union[str, Path, List]) -> Dict[str, Any]

基于参考图片生成新图片。

**参数:**
- `prompt`: 生成指令
- `reference_images`: 单张或多张参考图片（支持URL和本地路径）

**返回格式与 `text_to_image` 相同**

#### analyze(image: Union[str, Path, List], question: str = "描述图片") -> str

分析图片内容，返回文本描述。

### 便捷函数

直接使用全局实例，无需创建客户端：

```python
import nano_banana as nb

# 所有函数签名与类方法相同
result = nb.text_to_image("prompt")
result = nb.image_to_image("prompt", "image.jpg")
analysis = nb.analyze("image.jpg", "question")
```

## 实际应用示例

### 电商产品图生成
```python
import nano_banana as nb

# 生成产品宣传图
result = nb.text_to_image(
    "时尚蓝牙耳机产品图，白色背景，专业摄影lighting"
)

if result['success']:
    print(f"生成的图片: {result['urls'][0]}")
else:
    print(f"生成失败: {result['message']}")
```

### 图片风格转换
```python
# 将照片转换为艺术风格
result = nb.image_to_image(
    "转换成梵高星夜风格的油画",
    "my_photo.jpg"
)

# 批量处理多张参考图
result = nb.image_to_image(
    "结合这些图片元素创作新作品",
    ["style_ref.jpg", "content_ref.jpg"]
)
```

### 智能图片分析
```python
# 分析单张图片
analysis = nb.analyze(
    "product_photo.jpg",
    "分析产品的设计特点和市场定位建议"
)

# 对比分析多张图片
comparison = nb.analyze(
    ["before.jpg", "after.jpg"],
    "比较这两张图片的差异和改进点"
)
```

## 系统要求

- Python 3.8+
- SIMEN AI API密钥 或 OpenAI API密钥
- `openai>=1.106.1`

## License

MIT License