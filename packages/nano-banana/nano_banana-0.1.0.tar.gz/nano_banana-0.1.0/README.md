# nano-banana 🍌

基于 Google Gemini 2.5 Flash Image 的简单 Python 包装器，提供文本生成图片、图片到图片转换和图片分析功能。

## 功能特性

- 🎨 **文本生成图片**: 使用 `gemini-2.5-flash-image` 模型从文本描述生成图片
- 🔄 **图片到图片**: 基于参考图片和提示词进行图片编辑和创作
- 🔍 **图片分析**: 使用 `gemini-2.5-flash` 模型理解和分析图片内容
- 🖼️ **多种输入格式**: 支持图片URL、本地文件路径
- 🚀 **简单易用**: 提供类接口和便捷函数两种使用方式
- 🔧 **灵活配置**: 支持自定义API密钥和基础URL

## Installation

```bash
# Using uv (recommended)
uv add nano-banana

# Using pip
pip install nano-banana
```

## Quick Start

### 设置 API 密钥

```bash
# 设置 SIMEN AI API 密钥 (推荐)
export SIMEN_AI_API_KEY="your-simen-ai-api-key"
export SIMEN_BASEURL="https://api.simen.ai/v1"


```

### 基本用法

```python
import nano_banana as nb

# 1. 文本生成图片
result = nb.text_to_image("一只可爱的橙色小猫坐在花园里")
print(result)

# 2. 图片分析
result = nb.analyze(
    "https://example.com/image.jpg", 
    "这张图片里有什么物体？"
)
print(result)

# 3. 图片到图片转换
result = nb.image_to_image(
    "把这张图片转换成卡通风格", 
    "path/to/your/image.jpg"
)
print(result)
```

### 使用 NanoBanana 类

```python
from nano_banana import NanoBanana

# 初始化客户端
client = NanoBanana(api_key="your-api-key")  # 或使用环境变量

# 1. 文本生成图片
result = client.text_to_image("一只在彩虹桥上跳舞的独角兽")
print(result)

# 2. 图片分析 - 单张图片
analysis = client.analyze(
    "https://example.com/image.jpg",
    "详细描述这张图片的内容和风格"
)
print(analysis)

# 3. 图片分析 - 多张图片
analysis = client.analyze(
    ["image1.jpg", "image2.jpg"],
    "比较这些图片的相似点和不同点"
)
print(analysis)

# 4. 图片到图片 - 单张参考图片
new_image = client.image_to_image(
    "将这张图片转换成梵高的星夜风格",
    "reference_image.jpg"
)
print(new_image)

# 5. 图片到图片 - 多张参考图片
new_image = client.image_to_image(
    "结合这些图片的元素，创作一张新的艺术作品",
    ["style_ref.jpg", "content_ref.jpg"]
)
print(new_image)
```

## API 参考

### NanoBanana 类

主要的客户端类，提供所有图片生成和分析功能。

#### 构造函数

```python
NanoBanana(api_key: Optional[str] = None, base_url: Optional[str] = None)
```

**参数:**
- `api_key` (可选): API密钥。如果未提供，将从环境变量 `SIMEN_AI_API_KEY` 或 `OPENAI_API_KEY` 获取
- `base_url` (可选): API基础URL。如果未提供，将从环境变量 `SIMEN_BASEURL` 获取

#### 方法

##### text_to_image(prompt: str) -> str

从文本描述生成图片。

**参数:**
- `prompt`: 图片描述文本

**返回:** 生成的图片内容（通常包含图片URL或base64数据）

**示例:**
```python
client = NanoBanana()
result = client.text_to_image("一只穿着太空服的猫在月球上漫步")
```

##### image_to_image(prompt: str, reference_images: Union[str, Path, List[Union[str, Path]]]) -> str

基于参考图片和提示词进行图片编辑和创作。

**参数:**
- `prompt`: 转换或编辑指令
- `reference_images`: 参考图片，可以是：
  - 单个图片URL字符串
  - 单个本地文件路径
  - 图片URL和文件路径的列表

**返回:** 生成的新图片内容

**示例:**
```python
# 单张参考图片
result = client.image_to_image("转换成水彩画风格", "photo.jpg")

# 多张参考图片
result = client.image_to_image(
    "结合这些图片的风格创作新作品", 
    ["style1.jpg", "https://example.com/style2.jpg"]
)
```

##### analyze(image: Union[str, Path, List[Union[str, Path]]], question: str = "描述图片") -> str

分析图片内容。

**参数:**
- `image`: 要分析的图片，可以是：
  - 单个图片URL字符串
  - 单个本地文件路径
  - 图片URL和文件路径的列表
- `question`: 分析问题或指令（默认："描述图片"）

**返回:** 图片分析结果文本

**示例:**
```python
# 分析单张图片
result = client.analyze("image.jpg", "这张图片的主要内容是什么？")

# 分析多张图片
result = client.analyze(
    ["image1.jpg", "image2.jpg"], 
    "比较这两张图片的差异"
)
```

### 便捷函数

这些函数使用全局客户端实例，无需手动创建 NanoBanana 对象。

#### text_to_image(prompt: str) -> str

**参数和返回值与类方法相同**

```python
import nano_banana as nb
result = nb.text_to_image("夕阳下的海滩")
```

#### image_to_image(prompt: str, reference_images: Union[str, Path, List[Union[str, Path]]]) -> str

**参数和返回值与类方法相同**

```python
import nano_banana as nb
result = nb.image_to_image("转换成油画风格", "photo.jpg")
```

#### analyze(image: Union[str, Path, List[Union[str, Path]]], question: str = "描述图片") -> str

**参数和返回值与类方法相同**

```python
import nano_banana as nb
result = nb.analyze("image.jpg", "图片中有多少人？")
```

## 实际应用示例

### 真实使用场景 [[memory:8073042]]

**张小美，28岁，上海电商运营经理**
张小美需要为即将上线的新产品快速生成宣传图片和分析产品照片。面对紧迫的上线时间，她感到有些焦虑。

```python
import nano_banana as nb

# 1. 为新产品生成宣传图片
promo_image = nb.text_to_image(
    "时尚简约的蓝牙耳机产品图，白色背景，专业摄影lighting，电商主图风格"
)
print(f"生成的宣传图: {promo_image}")

# 2. 分析竞品图片获取灵感
competitor_analysis = nb.analyze(
    "https://competitor.com/product.jpg",
    "分析这个产品图片的构图、光线和视觉元素，为我们的产品拍摄提供建议"
)
print(f"竞品分析: {competitor_analysis}")

# 3. 批量优化现有产品图片
optimized_image = nb.image_to_image(
    "优化这张产品图片，增强色彩饱和度，添加更专业的背景",
    "current_product.jpg"
)
print(f"优化后的图片: {optimized_image}")
```

**李教授，45岁，北京医学影像研究专家**
李教授对使用AI辅助分析医学影像数据进行早期疾病检测研究感到兴奋。

```python
from nano_banana import NanoBanana

client = NanoBanana()

# 分析医学影像（仅用于研究，非诊断用途）
analysis = client.analyze(
    "/research/data/ct_scan_001.png",
    "识别此医学影像中的显著模式或异常区域，描述影像特征"
)
print(f"影像分析结果: {analysis}")

# 生成教学用的示例影像
teaching_image = client.text_to_image(
    "医学教学用的人体肺部CT扫描示意图，清晰显示正常肺部结构"
)
print(f"教学示例图: {teaching_image}")

# 对比分析多张影像
comparison = client.analyze(
    ["normal_scan.png", "abnormal_scan.png"],
    "比较这两张医学影像的差异，指出关键的不同之处"
)
print(f"对比分析: {comparison}")
```

**王小雨，34岁，广州旅行博主**
王小雨因为要管理大量的社交媒体内容而感到压力山大，急需快速为她的旅行照片生成吸引人的内容。

```python
import nano_banana as nb

# 1. 分析旅行照片生成文案
travel_photos = [
    "/photos/guilin_landscape.jpg",
    "/photos/local_food.jpg", 
    "/photos/sunset_beach.jpg"
]

for photo in travel_photos:
    caption = nb.analyze(
        photo,
        "为这张旅行照片创作一段吸引人的小红书文案，包含相关话题标签和情感描述"
    )
    print(f"{photo} 的文案: {caption}")

# 2. 基于现有照片生成新的创意图片
creative_image = nb.image_to_image(
    "将这张风景照转换成梦幻的插画风格，适合做封面图",
    "/photos/mountain_view.jpg"
)
print(f"创意封面图: {creative_image}")

# 3. 生成旅行攻略配图
guide_image = nb.text_to_image(
    "手绘风格的广州美食地图，标注热门餐厅和小吃街，温暖色调"
)
print(f"攻略配图: {guide_image}")
```

## 系统要求

- Python 3.8+
- SIMEN AI API密钥 或 OpenAI API密钥
- `openai>=1.106.1`

## 许可证

MIT License

## 贡献

欢迎贡献代码！请随时提交 Pull Request。

## 技术支持

如果遇到任何问题，请在 [GitHub Issues](https://github.com/yourusername/nano-banana/issues) 页面提交bug报告。
