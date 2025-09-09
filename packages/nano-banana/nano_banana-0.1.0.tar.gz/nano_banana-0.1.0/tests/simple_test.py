#!/usr/bin/env python3
"""
简单的 nano-banana 测试脚本
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 导入我们的包
import nano_banana as nb

def main():
    print("🍌 nano-banana 图片生成测试")
    print("=" * 40)
    
    # 检查环境变量
    api_key = os.environ.get("SIMEN_AI_API_KEY")
    base_url = os.environ.get("SIMEN_BASEURL")
    
    print(f"API Key: {'✅ 已设置' if api_key else '❌ 未设置'}")
    print(f"Base URL: {base_url if base_url else '使用默认'}")
    print()
    
    if not api_key:
        print("❌ 请在 .env 文件中设置 SIMEN_AI_API_KEY")
        return
    
    # 测试1: 文生图
    print("🎨 测试1: 文生图 (Text-to-Image)")
    print("-" * 30)
    prompt = "一只可爱的狐狸坐在雪地里，背景是冬日森林，阳光透过树枝洒下，高质量摄影风格"
    
    try:
        print("🎨 正在生成图片...")
        print(f"📝 提示词: {prompt}")
        
        image_url = nb.generate_image(
            prompt=prompt,
            size="1024x1024",
            quality="hd"
        )
        
        print(f"✅ 文生图成功!")
        print(f"🔗 图片URL: {image_url}")
        print()
        
    except Exception as e:
        print(f"❌ 文生图失败: {e}")
        print()
    
    # 测试2: 图生图变体 (使用浣熊图片)
    print("🖼️  测试2: 图生图 (Image-to-Image)")
    print("-" * 30)
    test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/2023_06_08_Raccoon1.jpg/1599px-2023_06_08_Raccoon1.jpg"
    
    try:
        print("📥 正在下载原图片...")
        import requests
        import tempfile
        
        # 下载图片到临时文件
        response = requests.get(test_image_url)
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_file.write(response.content)
            temp_image_path = temp_file.name
        
        print("🔄 正在基于原图生成变体...")
        variation_url = nb.create_variation(
            image_path=temp_image_path,
            size="1024x1024",
            n=1
        )
        
        print(f"✅ 图生图变体成功!")
        print(f"🔗 原图URL: {test_image_url}")
        print(f"🔗 变体URL: {variation_url}")
        print("\n💡 您可以对比查看原图和生成的变体")
        
        # 清理临时文件
        os.unlink(temp_image_path)
        
    except Exception as e:
        print(f"❌ 图生图失败: {e}")
        print("\n🔧 调试信息:")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误详情: {str(e)}")

if __name__ == "__main__":
    main()
