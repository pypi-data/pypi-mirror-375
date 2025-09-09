"""
nano-banana: A simple wrapper around OpenAI's Vision API

A lightweight Python package that provides easy access to OpenAI's Vision capabilities
with a fixed model configuration for consistent image analysis.
"""

from .vision import NanoBanana, text_to_image, image_to_image, analyze

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Expose main classes and functions
__all__ = [
    "NanoBanana",
    "text_to_image", 
    "image_to_image",
    "analyze"
]
