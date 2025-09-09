"""
nano-banana: Gemini 2.5 Flash Image 简单包装
Google最先进的图像生成和编辑模型
"""

import os
import re
import base64
from typing import Union, List, Optional, Dict, Any
from pathlib import Path
from openai import OpenAI


class NanoBanana:
    """Gemini 2.5 Flash Image 简单客户端"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """初始化客户端"""
        api_key = api_key or os.environ.get("SIMEN_AI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        base_url = base_url or os.environ.get("SIMEN_BASEURL")
        
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)
    
    def _prepare_images(self, image_inputs: Union[str, Path, List[Union[str, Path]]]) -> List[dict]:
        """准备图片输入，支持单张或多张图片"""
        if not isinstance(image_inputs, list):
            image_inputs = [image_inputs]
        
        image_content = []
        for image_input in image_inputs:
            if isinstance(image_input, str) and (image_input.startswith('http://') or image_input.startswith('https://')):
                # URL图片
                image_content.append({
                    "type": "image_url", 
                    "image_url": {"url": image_input}
                })
            else:
                # 本地文件
                image_path = Path(image_input)
                if not image_path.exists():
                    raise FileNotFoundError(f"图片文件未找到: {image_path}")
                
                with open(image_path, "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                    # 根据文件扩展名确定MIME类型
                    ext = image_path.suffix.lower()
                    mime_type = {
                        '.jpg': 'image/jpeg',
                        '.jpeg': 'image/jpeg', 
                        '.png': 'image/png',
                        '.gif': 'image/gif',
                        '.webp': 'image/webp'
                    }.get(ext, 'image/jpeg')
                    
                    image_content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{image_data}"}
                    })
        
        return image_content
    
    def _extract_image_urls(self, response_text: str) -> List[str]:
        """从响应文本中提取图片URL"""
        # 匹配markdown格式的图片链接: ![alt](url)
        markdown_pattern = r'!\[.*?\]\((https?://[^\)]+)\)'
        # 匹配直接的URL
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+\.(?:png|jpg|jpeg|gif|webp|svg)'
        
        urls = []
        # 提取markdown格式的URLs
        urls.extend(re.findall(markdown_pattern, response_text))
        # 提取直接的URLs
        urls.extend(re.findall(url_pattern, response_text, re.IGNORECASE))
        
        return list(set(urls))  # 去重
    
    def _format_image_response(self, response_text: str) -> Dict[str, Any]:
        """格式化图片生成/编辑的响应"""
        urls = self._extract_image_urls(response_text)
        
        return {
            "success": len(urls) > 0,
            "urls": urls,
            "raw_response": response_text,
            "message": "成功生成图片" if urls else "未找到图片URL，请检查响应内容"
        }
    
    def text_to_image(self, prompt: str) -> Dict[str, Any]:
        """文本生成图片"""
        
        # 构建消息内容
        content = [{"type": "text", "text": f"作为世界最顶尖的图片生成模型，请按照要求：{prompt}, 生成一张图片"}]
        
        response = self.client.chat.completions.create(
            model="gemini-2.5-flash-image",
            messages=[
                {
                    "role": "user", 
                    "content": content
                }
            ],
            max_tokens=500,
        )
        # 格式化返回结构化响应
        result = response.choices[0].message.content
        return self._format_image_response(result)
    
    def image_to_image(self, prompt: str, reference_images: Union[str, Path, List[Union[str, Path]]]) -> Dict[str, Any]:
        """图片到图片的转换/编辑/创作"""
        
        # 构建消息内容
        content = [{"type": "text", "text": f"作为世界最顶尖的图片生成模型，请参考提供的图片，按照要求：{prompt}, 生成一张新的图片"}]
        
        # 添加图片内容
        image_content = self._prepare_images(reference_images)
        content.extend(image_content)
            
        response = self.client.chat.completions.create(
            model="gemini-2.5-flash-image",
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            max_tokens=500,
        )
        result = response.choices[0].message.content
        return self._format_image_response(result)
    
    def analyze(self, image: Union[str, Path, List[Union[str, Path]]], question: str = "描述图片") -> str:
        """分析图片：理解和分析图片内容"""
        
        # 构建消息内容
        content = [{"type": "text", "text": f"作为世界最顶尖的图片分析模型,根据提供的图片，请按照要求：{question}, 分析图片内容"}]
        
        # 添加图片内容
        image_content = self._prepare_images(image)
        content.extend(image_content)
            
        response = self.client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            max_tokens=500,
        )
        result = response.choices[0].message.content
        return result  # analyze方法返回文字分析，不提取URL


# 全局实例和便捷函数
_client = None

def _get_client():
    global _client
    if _client is None:
        _client = NanoBanana()
    return _client

def text_to_image(prompt: str) -> Dict[str, Any]:
    """文本生成图片"""
    return _get_client().text_to_image(prompt)

def image_to_image(prompt: str, reference_images: Union[str, Path, List[Union[str, Path]]]) -> Dict[str, Any]:
    """图片到图片的转换/编辑/创作"""
    return _get_client().image_to_image(prompt, reference_images)


def analyze(image: Union[str, Path, List[Union[str, Path]]], question: str = "描述图片") -> str:
    """分析图片：理解和分析图片内容"""
    return _get_client().analyze(image, question)