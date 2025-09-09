#!/usr/bin/env python3
"""
文生图 (Text-to-Image) 简单测试 - 使用 Chat 调用方式
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 导入我们的包
import nano_banana as nb

def main():
    print("🎨 nano-banana 文生图测试 (Chat 调用方式)")
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
    
    # 简单文生图测试
    prompt = "一只可爱的狐狸坐在雪地里，背景是冬日森林，阳光透过树枝洒下，高质量摄影风格"
    
    try:
        print("🎨 正在生成图片...")
        print(f"📝 提示词: {prompt}")
        print("⏳ 使用 gemini-2.5-flash-image 模型...")
        
        # 使用新的 text_to_image 函数
        result = nb.text_to_image(prompt)
        
        print(f"✅ API 调用成功!")
        print(f"📄 响应内容:")
        print("-" * 30)
        print(result)
        print("-" * 30)
        
        # 尝试从响应中提取图片URL (如果有的话)
        if "http" in result:
            print("🔗 检测到可能的图片URL:")
            lines = result.split('\n')
            for line in lines:
                if "http" in line:
                    print(f"   {line.strip()}")
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        print(f"   错误类型: {type(e).__name__}")
        import traceback
        print(f"   详细错误: {traceback.format_exc()}")
    
    print("\n💡 如果响应包含图片URL，您可以复制到浏览器查看")
    print("💡 如果没有URL，可能需要调整API响应解析逻辑")

if __name__ == "__main__":
    main()