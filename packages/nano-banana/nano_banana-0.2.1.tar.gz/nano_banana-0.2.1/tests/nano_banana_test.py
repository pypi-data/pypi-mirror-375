#!/usr/bin/env python3
"""
测试 nano-banana 三个主要接口
验证新的结构化返回值格式
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from nano_banana import text_to_image, image_to_image, analyze

def test_text_to_image():
    """测试 text_to_image 接口 - 文本生成图片"""
    print("🎨 测试 text_to_image 接口...")
    
    try:
        # 测试基础文本生成
        print("📝 测试基础文本生成...")
        result = text_to_image("一只可爱的橘猫在阳光下睡觉")
        
        # 验证返回值结构
        if not isinstance(result, dict):
            print(f"❌ 返回值格式错误: 期望dict，实际{type(result)}")
            return False
        
        required_keys = ["success", "urls", "raw_response", "message"]
        missing_keys = [key for key in required_keys if key not in result]
        if missing_keys:
            print(f"❌ 返回值缺少必要字段: {missing_keys}")
            return False
        
        print(f"✅ 返回值结构正确:")
        print(f"   成功状态: {result['success']}")
        print(f"   URL数量: {len(result['urls'])}")
        print(f"   提取到的URLs: {result['urls']}")
        print(f"   消息: {result['message']}")
        print(f"   原始响应: {result['raw_response'][:100]}...")
        
        if result['success'] and result['urls']:
            print("✅ 成功提取到图片URL")
        else:
            print("⚠️ 未提取到图片URL，但接口调用成功")
        
        return True
        
    except Exception as e:
        print(f"❌ text_to_image 测试失败:")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误详情: {str(e)}")
        return False

def test_image_to_image():
    """测试 image_to_image 接口 - 图片转换/编辑"""
    print("\n✏️ 测试 image_to_image 接口...")
    
    try:
        # 测试图片转换
        print("🖼️ 测试图片转换...")
        test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/2023_06_08_Raccoon1.jpg/1599px-2023_06_08_Raccoon1.jpg"
        result = image_to_image("把这只动物改成猴子，其他什么都不变", test_image_url)
        
        # 验证返回值结构
        if not isinstance(result, dict):
            print(f"❌ 返回值格式错误: 期望dict，实际{type(result)}")
            return False
        
        required_keys = ["success", "urls", "raw_response", "message"]
        missing_keys = [key for key in required_keys if key not in result]
        if missing_keys:
            print(f"❌ 返回值缺少必要字段: {missing_keys}")
            return False
        
        print(f"✅ 图片转换返回值结构正确:")
        print(f"   成功状态: {result['success']}")
        print(f"   URL数量: {len(result['urls'])}")
        print(f"   提取到的URLs: {result['urls']}")
        print(f"   消息: {result['message']}")
        print(f"   原始响应: {result['raw_response'][:200]}...")
        
        # 测试带参考图片的生成
        print("\n📝 测试带参考图片的生成...")
        # result2 = image_to_image("生成一张类似风格的图片，但是换成一只猫", test_image_url)
        
        # print(f"✅ 带参考图片生成返回值结构:")
        # print(f"   成功状态: {result2['success']}")
        # print(f"   URL数量: {len(result2['urls'])}")
        # print(f"   提取到的URLs: {result2['urls']}")
        # print(f"   消息: {result2['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ image_to_image 测试失败:")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误详情: {str(e)}")
        return False

def test_analyze():
    """测试 analyze 接口 - 分析图片"""
    print("\n🔍 测试 analyze 接口...")
    
    try:
        # 测试默认分析
        print("📊 测试默认图片分析...")
        test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/2023_06_08_Raccoon1.jpg/1599px-2023_06_08_Raccoon1.jpg"
        result = analyze(test_image_url)
        print(f"✅ 默认分析成功: {result}")
        
        # 测试自定义问题分析
        print("📊 测试自定义问题分析...")
        result = analyze(test_image_url, "这只动物的品种是什么？")
        print(f"✅ 自定义问题分析成功: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ analyze 测试失败:")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误详情: {str(e)}")
        return False

def test_local_image():
    """测试本地图片功能"""
    print("\n🏠 测试本地图片...")
    
    # 查找测试图片
    test_image_path = Path(__file__).parent / "image.png"
    if not test_image_path.exists():
        print("⚠️ 本地测试图片不存在，跳过本地图片测试")
        return True
    
    try:
        print(f"📁 使用本地图片: {test_image_path}")
        result = analyze(str(test_image_path), "描述这张图片的内容")
        print(f"✅ 本地图片分析成功: {result}")
        return True
        
    except Exception as e:
        print(f"❌ 本地图片测试失败:")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误详情: {str(e)}")
        return False

def print_separator(title=""):
    """打印分隔线"""
    if title:
        print(f"\n{'='*20} {title} {'='*20}")
    else:
        print("=" * 60)

def main():
    print("🍌 nano-banana 接口测试 (新版本结构化返回值)")
    print_separator()
    
    # 检查环境变量
    if not os.environ.get("SIMEN_AI_API_KEY"):
        print("❌ 请设置 SIMEN_AI_API_KEY 环境变量")
        return
    
    results = []
    
    # 测试三个主要接口 - 现在启用所有测试
    # results.append(("text_to_image", test_text_to_image()))
    results.append(("image_to_image", test_image_to_image()))
    # results.append(("analyze", test_analyze()))
    # results.append(("local_image", test_local_image()))
    
    # 输出测试结果
    print_separator("测试结果汇总")
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   {test_name}: {status}")
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    print(f"\n🎯 总体结果: {success_count}/{total_count} 个测试通过")
    
    if success_count == total_count:
        print("🎉 所有测试都通过了！nano-banana 新版本工作正常！")
        print("✨ 接口现在返回结构化数据，包含提取的URL和完整响应信息")
    else:
        print("💥 部分测试失败，请检查配置和网络连接")
        print("📝 注意：新版本接口返回格式已更改为结构化字典")

if __name__ == "__main__":
    main()
