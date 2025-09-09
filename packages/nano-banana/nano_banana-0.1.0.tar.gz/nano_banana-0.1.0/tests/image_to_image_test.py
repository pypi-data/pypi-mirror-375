#!/usr/bin/env python3
"""
图生图 (Image-to-Image) 编辑测试 - 将动物变成老虎
"""

import os
import requests
import tempfile
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 导入我们的包
import nano_banana as nb

def main():
    print("🐯 nano-banana 图生图编辑测试 - 动物变老虎")
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
    
    # 使用用户提供的图片
    image_url = "https://api.openai-next.com/fileSystem/response_images/3757/2025/09/08/1757329031438315086_3733.png"
    edit_prompt = "将这张图片中的动物替换成一只威猛的老虎，保持相同的姿势和背景环境，高质量摄影风格"
    
    try:
        print("📥 正在处理原图片...")
        print(f"🔗 原图URL: {image_url}")
        
        # 直接使用URL，不需要下载到本地
        print("🎨 正在编辑图片...")
        print(f"📝 编辑提示: {edit_prompt}")
        print("⏳ 使用 gemini-2.5-flash-image 模型...")
        
        # 使用修改后的 edit 函数 (支持URL输入)
        result = nb.image_to_image(edit_prompt, image_url)
        
        print(f"✅ 图片编辑API调用成功!")
        print(f"📄 完整响应内容:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
        # 尝试从响应中提取图片URL (如果有的话)
        if "http" in result:
            print("🔗 检测到可能的图片URL:")
            lines = result.split('\n')
            for line in lines:
                if "http" in line:
                    print(f"   {line.strip()}")
        else:
            print("ℹ️  响应中未检测到URL，可能是纯文字描述")
        
    except Exception as e:
        print(f"❌ 图片编辑失败: {e}")
        print(f"   错误类型: {type(e).__name__}")
        import traceback
        print(f"   详细错误: {traceback.format_exc()}")
    
    print("\n💡 如果响应包含图片URL，您可以复制到浏览器查看编辑结果")
    print("💡 原图中的动物应该被替换成老虎了")

if __name__ == "__main__":
    main()