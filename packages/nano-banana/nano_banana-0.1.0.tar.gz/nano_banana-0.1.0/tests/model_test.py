#!/usr/bin/env python3
"""
测试 gpt-4o-mini 视觉功能
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 文件
load_dotenv()

def test_gpt4o_mini_vision():
    """测试 gpt-4o-mini 视觉功能"""
    print("👁️ 测试 gpt-4o-mini 视觉功能...")
    
    api_key = os.environ.get("SIMEN_AI_API_KEY")
    base_url = os.environ.get("SIMEN_BASEURL")
    
    # 创建客户端
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # 测试图片URL
    test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/2023_06_08_Raccoon1.jpg/1599px-2023_06_08_Raccoon1.jpg"
    
    try:
        print("🔍 发送图片分析请求...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "这张图片里有什么动物？请用中文简短回答。"},
                        {"type": "image_url", "image_url": {"url": test_image_url}},
                    ],
                }
            ],
            max_tokens=200,
        )
        
        result = response.choices[0].message.content
        print(f"✅ gpt-4o-mini 视觉分析成功:")
        print(f"📝 分析结果: {result}")
        return True
        
    except Exception as e:
        print(f"❌ gpt-4o-mini 视觉分析失败:")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误详情: {str(e)}")
        return False

def test_other_models():
    """测试其他可能的模型"""
    print("\n🔄 测试其他模型的视觉功能...")
    
    api_key = os.environ.get("SIMEN_AI_API_KEY")
    base_url = os.environ.get("SIMEN_BASEURL")
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # 要测试的模型列表
    models = [
        "gpt-4o",
        "gemini-1.5-flash",
        "gemini-2.0-flash-exp",
        "claude-3-haiku"
    ]
    
    test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/2023_06_08_Raccoon1.jpg/1599px-2023_06_08_Raccoon1.jpg"
    
    for model in models:
        print(f"\n🧪 测试模型: {model}")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "这张图片里有什么？"},
                            {"type": "image_url", "image_url": {"url": test_image_url}},
                        ],
                    }
                ],
                max_tokens=100,
            )
            result = response.choices[0].message.content
            print(f"✅ {model}: {result}")
            
        except Exception as e:
            print(f"❌ {model}: {str(e)}")

def main():
    print("👁️ 测试视觉功能")
    print("=" * 30)
    
    # 先测试 gpt-4o-mini
    success = test_gpt4o_mini_vision()
    
    if success:
        print("\n🎉 gpt-4o-mini 视觉功能正常！")
        print("可以将 nano-banana 包的模型改为 gpt-4o-mini")
    else:
        print("\n💥 gpt-4o-mini 视觉功能失败，尝试其他模型...")
        test_other_models()

if __name__ == "__main__":
    main()
