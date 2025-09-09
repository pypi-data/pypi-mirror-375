#!/usr/bin/env python3
"""
快速测试 gpt-4o-mini 对话功能
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 文件
load_dotenv()

def test_gpt4o_mini_chat():
    """测试 gpt-4o-mini 对话"""
    print("💬 测试 gpt-4o-mini 对话功能...")
    
    api_key = os.environ.get("SIMEN_AI_API_KEY")
    base_url = os.environ.get("SIMEN_BASEURL")
    
    print(f"🔑 API Key: {'已设置' if api_key else '未设置'}")
    print(f"🌐 Base URL: {base_url}")
    print()
    
    if not api_key:
        print("❌ 未找到 SIMEN_AI_API_KEY")
        return False
    
    # 创建客户端
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    try:
        print("🔍 发送测试消息...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "你好！请简单介绍一下你自己，并告诉我1+1等于多少？"}
            ],
            max_tokens=200,
        )
        
        result = response.choices[0].message.content
        print(f"✅ gpt-4o-mini 回复成功:")
        print(f"📝 回复内容: {result}")
        print()
        return True
        
    except Exception as e:
        print(f"❌ gpt-4o-mini 对话失败:")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误详情: {str(e)}")
        return False

def main():
    print("🧪 快速测试 gpt-4o-mini")
    print("=" * 30)
    
    success = test_gpt4o_mini_chat()
    
    if success:
        print("🎉 gpt-4o-mini 对话测试成功！")
        print("接下来可以测试视觉功能...")
    else:
        print("💥 gpt-4o-mini 对话测试失败")
        print("请检查 API 配置")

if __name__ == "__main__":
    main()
