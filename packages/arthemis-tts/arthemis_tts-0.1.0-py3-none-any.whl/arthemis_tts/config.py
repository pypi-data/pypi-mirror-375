"""
Configuration settings for Arthemis TTS
"""
import os
from typing import List


class TTSConfig:
    """Configuration class for TTS model and audio processing"""
    
    # Model architecture parameters
    embedding_size: int = 256
    encoder_embedding_size: int = 512
    dim_feedforward: int = 1024
    postnet_embedding_size: int = 1024
    encoder_kernel_size: int = 3
    postnet_kernel_size: int = 5
    max_mel_time: int = 1024
    
    # Text processing parameters
    symbols: List[str] = [
        'EOS', ' ', '!', ',', '-', '.', 
        ';', '?', 'a', 'b', 'c', 'd', 'e', 'f',
        'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
        'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'à',
        'â', 'è', 'é', 'ê', 'ü', "'", '"', '"'
    ]
    
    # Audio processing parameters
    sr: int = 22050  # Sample rate
    n_fft: int = 2048
    n_stft: int = int((n_fft // 2) + 1)
    frame_shift: float = 0.0125  # seconds
    hop_length: int = int(n_fft / 8.0)
    frame_length: float = 0.05  # seconds
    win_length: int = int(n_fft / 2.0)
    mel_freq: int = 128
    
    # Audio normalization parameters
    max_db: float = 100
    scale_db: float = 10
    ref: float = 4.0
    power: float = 2.0
    norm_db: float = 10
    ampl_multiplier: float = 10.0
    ampl_amin: float = 1e-10
    db_multiplier: float = 1.0
    ampl_ref: float = 1.0
    ampl_power: float = 1.0
    
    # Computed parameters
    @property
    def text_num_embeddings(self) -> int:
        return 2 * len(self.symbols)
    
    @property
    def min_level_db(self) -> float:
        return -self.max_db
    
    # Default model path
    @property
    def default_model_path(self) -> str:
        return os.path.join(os.path.dirname(__file__), "models", "arthemis_tts.pt")


# Global config instance
config = TTSConfig() 