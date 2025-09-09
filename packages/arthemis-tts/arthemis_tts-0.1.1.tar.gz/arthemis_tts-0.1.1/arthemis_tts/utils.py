"""
Utility functions for Arthemis TTS
"""
import torch
from typing import Optional, Union
import os


def mask_from_sequence_lengths(
    sequence_lengths: torch.Tensor,
    max_length: int
) -> torch.BoolTensor:
    """
    Create boolean mask from sequence lengths
    
    Args:
        sequence_lengths: Tensor of sequence lengths
        max_length: Maximum sequence length
        
    Returns:
        torch.BoolTensor: Boolean mask where True indicates valid positions
        
    Example:
        If input is [2, 2, 3] with max_length=4, returns:
        [[True, True, False, False],
         [True, True, False, False], 
         [True, True, True, False]]
    """
    # (batch_size, max_length)
    ones = sequence_lengths.new_ones(sequence_lengths.size(0), max_length)
    range_tensor = ones.cumsum(dim=1)
    return sequence_lengths.unsqueeze(1) >= range_tensor


def get_device() -> str:
    """
    Get the best available device for computation
    
    Returns:
        str: Device name ("cuda", "mps", or "cpu")
    """
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


def load_model(model_path: Optional[str] = None) -> 'ArthemisTTS':
    """
    Load a pre-trained Arthemis TTS model
    
    Args:
        model_path: Path to model file. If None, uses default model.
        
    Returns:
        ArthemisTTS: Loaded model instance
    """
    from .tts import ArthemisTTS
    
    if model_path is None:
        # Try to find default model in package
        from .config import config
        model_path = config.default_model_path
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Default model not found at {model_path}. "
                "Please provide a valid model_path or download a pre-trained model."
            )
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    
    # Load model
    device = get_device()
    model = ArthemisTTS(device=device)
    
    # Load state dict
    state_dict = torch.load(model_path, map_location=device)
    
    # Handle different state dict formats
    if isinstance(state_dict, dict) and "model" in state_dict:
        model.load_state_dict(state_dict["model"])
    else:
        model.load_state_dict(state_dict)
    
    model.eval()
    return model


def text_to_speech(
    text: str,
    model_path: Optional[str] = None,
    output_path: Optional[str] = None,
    max_length: int = 800,
    gate_threshold: float = 0.5
) -> Union[torch.Tensor, None]:
    """
    Simple text-to-speech function
    
    Args:
        text: Input text to synthesize
        model_path: Path to model file (optional)
        output_path: Path to save audio file (optional)
        max_length: Maximum generation length
        gate_threshold: Stop token threshold
        
    Returns:
        torch.Tensor: Generated audio tensor, or None if saved to file
    """
    from .tts import ArthemisTTS
    from .text_processing import text_to_sequence
    from .audio_processing import inverse_mel_spec_to_wav, write_audio_to_file
    
    # Load model
    model = load_model(model_path)
    device = model.device if hasattr(model, 'device') else get_device()
    
    # Convert text to sequence
    text_seq = text_to_sequence(text).unsqueeze(0).to(device)
    
    # Generate mel spectrogram
    with torch.no_grad():
        mel_postnet, gate_outputs = model.inference(
            text_seq,
            max_length=max_length,
            stop_token_threshold=gate_threshold,
            with_tqdm=False
        )
    
    # Convert to audio
    audio = inverse_mel_spec_to_wav(mel_postnet.detach()[0].T)
    
    # Save to file if path provided
    if output_path:
        write_audio_to_file(audio, output_path)
        return None
    else:
        return audio


def download_pretrained_model(
    model_name: str = "default",
    cache_dir: Optional[str] = None
) -> str:
    """
    Download a pre-trained model (placeholder for future implementation)
    
    Args:
        model_name: Name of the model to download
        cache_dir: Directory to cache the model
        
    Returns:
        str: Path to downloaded model
    """
    # This is a placeholder for future implementation
    # In a real implementation, this would download from a model hub
    raise NotImplementedError(
        "Model downloading is not yet implemented. "
        "Please provide a local model file."
    ) 