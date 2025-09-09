#!/usr/bin/env python3
"""
IU和特朗普白宫合影测试 - 使用真实图片文件进行图像合成
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 导入我们的包
import nano_banana as nb

def main():
    print("📸 nano-banana IU和特朗普白宫合影测试")
    print("=" * 50)
    
    # 检查环境变量
    api_key = os.environ.get("SIMEN_AI_API_KEY")
    base_url = os.environ.get("SIMEN_BASEURL")
    
    print(f"API Key: {'✅ 已设置' if api_key else '❌ 未设置'}")
    print(f"Base URL: {base_url if base_url else '使用默认'}")
    print()
    
    if not api_key:
        print("❌ 请在 .env 文件中设置 SIMEN_AI_API_KEY")
        return
    
    # 图片文件路径 (相对于项目根目录)
    project_root = Path(__file__).parent.parent.parent
    iu_image = project_root / "image copy.png"  # IU的照片
    trump_image = project_root / "image.png"    # 特朗普的照片
    
    print(f"📁 项目根目录: {project_root}")
    print(f"🎭 IU图片路径: {iu_image}")
    print(f"🏛️ 特朗普图片路径: {trump_image}")
    
    # 检查图片文件是否存在
    if not iu_image.exists():
        print(f"❌ IU图片文件不存在: {iu_image}")
        return
    
    if not trump_image.exists():
        print(f"❌ 特朗普图片文件不存在: {trump_image}")
        return
    
    print("✅ 图片文件检查通过")
    print()
    
    # 合影编辑提示词
    edit_prompt = """
    请将这两张照片中的人物合成为一张在美国白宫外面草地上的合影照片。
    
    具体要求：
    - 两个人都是半身照，站在一起合影
    - 背景是白宫外面的绿色草坪，可以看到白宫建筑
    - 光线自然，就像在户外拍摄的官方合影
    - 两人的表情保持友好和正式
    - 图片质量要高，像专业摄影师拍摄的效果
    - 构图要平衡，两人在画面中央
    
    请生成一张看起来真实自然的合影照片。
    """
    
    try:
        print("🎨 开始图片合成...")
        print(f"📝 编辑提示: {edit_prompt.strip()}")
        print("⏳ 使用 gemini-2.5-flash-image 模型...")
        print()
        
        # 使用 image_to_image 函数，传入两张图片进行合成
        image_inputs = [str(iu_image), str(trump_image)]
        result = nb.image_to_image(edit_prompt, image_inputs)
        
        print(f"✅ 图片合成API调用成功!")
        print(f"📄 响应内容:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
        # 尝试从响应中提取图片URL
        if "http" in result:
            print("🔗 检测到生成的合影图片URL:")
            lines = result.split('\n')
            for line in lines:
                if "http" in line:
                    print(f"   {line.strip()}")
        else:
            print("⚠️  响应中没有检测到图片URL")
            print("💡 这可能意味着模型返回了文本描述而不是图片链接")
            
        print()
        print("🔍 让我们尝试不同的方法 - 使用generate函数而不是edit函数:")
        
        # 尝试使用generate函数，将两张图片作为参考图片
        generate_prompt = """
        请生成一张IU和特朗普在美国白宫外草坪上的合影照片。
        
        要求：
        - 两人半身照，友好地站在一起
        - 背景是白宫外的绿色草坪，能看到白宫建筑
        - 专业摄影效果，光线自然
        - 构图平衡，两人在画面中央
        
        请直接生成图片，不要只是描述。
        """
        
        print("🎨 尝试使用image_to_image方法...")
        result2 = nb.image_to_image(generate_prompt, image_inputs)
        
        print(f"📄 Image_to_image方法响应:")
        print("-" * 50)
        print(result2)
        print("-" * 50)
        
        # 检查第二次尝试的结果
        if "http" in result2:
            print("🔗 Generate方法检测到图片URL:")
            lines = result2.split('\n')
            for line in lines:
                if "http" in line:
                    print(f"   {line.strip()}")
        else:
            print("⚠️  Generate方法也没有返回图片URL")
        
        print()
        print("🎉 测试完成!")
        print("💡 如果两次尝试都没有返回图片URL，可能需要检查模型配置或提示词格式")
        
    except Exception as e:
        print(f"❌ 图片合成失败: {e}")
        print(f"   错误类型: {type(e).__name__}")
        import traceback
        print(f"   详细错误: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
