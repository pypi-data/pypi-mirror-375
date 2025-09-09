"""
Arthemis TTS - A simple transformer-based text-to-speech library

This library provides a simple interface for text-to-speech synthesis using
a transformer-based architecture.
"""

__version__ = "0.1.0"
__author__ = "Arthemis TTS Team"
__email__ = "arthemis@example.com"

from .tts import ArthemisTTS
from .utils import text_to_speech, load_model

__all__ = ["ArthemisTTS", "text_to_speech", "load_model"] 