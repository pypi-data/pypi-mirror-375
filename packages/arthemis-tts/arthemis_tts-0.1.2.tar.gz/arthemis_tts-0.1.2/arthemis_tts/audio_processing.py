"""
Audio processing utilities for Arthemis TTS
"""
import torch
import torchaudio
import numpy as np
import io
from typing import Union, Optional
from .config import config

# Lazy initialization of transforms to avoid CUDA errors during import
_spec_transform = None
_mel_scale_transform = None
_mel_inverse_transform = None
_griffnlim_transform = None


def get_spec_transform():
    """Lazy initialization of spectrogram transform"""
    global _spec_transform
    if _spec_transform is None:
        _spec_transform = torchaudio.transforms.Spectrogram(
            n_fft=config.n_fft,
            win_length=config.win_length,
            hop_length=config.hop_length,
            power=config.power
        )
    return _spec_transform


def get_mel_scale_transform():
    """Lazy initialization of mel scale transform"""
    global _mel_scale_transform
    if _mel_scale_transform is None:
        _mel_scale_transform = torchaudio.transforms.MelScale(
            n_mels=config.mel_freq,
            sample_rate=config.sr,
            n_stft=config.n_stft
        )
    return _mel_scale_transform


def get_mel_inverse_transform(device: str = "cpu"):
    """Lazy initialization of inverse mel transform"""
    global _mel_inverse_transform
    if _mel_inverse_transform is None:
        _mel_inverse_transform = torchaudio.transforms.InverseMelScale(
            n_mels=config.mel_freq,
            sample_rate=config.sr,
            n_stft=config.n_stft
        ).to(device)
    return _mel_inverse_transform


def get_griffnlim_transform(device: str = "cpu"):
    """Lazy initialization of Griffin-Lim transform"""
    global _griffnlim_transform
    if _griffnlim_transform is None:
        _griffnlim_transform = torchaudio.transforms.GriffinLim(
            n_fft=config.n_fft,
            win_length=config.win_length,
            hop_length=config.hop_length
        ).to(device)
    return _griffnlim_transform


def pow_to_db_mel_spec(mel_spec: torch.Tensor) -> torch.Tensor:
    """Convert power mel spectrogram to decibel scale"""
    mel_spec = torchaudio.functional.amplitude_to_DB(
        mel_spec,
        multiplier=config.ampl_multiplier,
        amin=config.ampl_amin,
        db_multiplier=config.db_multiplier,
        top_db=config.max_db
    )
    mel_spec = mel_spec / config.scale_db
    return mel_spec


def db_to_power_mel_spec(mel_spec: torch.Tensor) -> torch.Tensor:
    """Convert decibel mel spectrogram to power scale"""
    mel_spec = mel_spec * config.scale_db
    mel_spec = torchaudio.functional.DB_to_amplitude(
        mel_spec,
        ref=config.ampl_ref,
        power=config.ampl_power
    )
    return mel_spec


def convert_to_mel_spec(wav: torch.Tensor) -> torch.Tensor:
    """
    Convert waveform to mel spectrogram
    
    Args:
        wav: Input waveform tensor
        
    Returns:
        torch.Tensor: Mel spectrogram in dB scale
    """
    spec = get_spec_transform()(wav)
    mel_spec = get_mel_scale_transform()(spec)
    db_mel_spec = pow_to_db_mel_spec(mel_spec)
    db_mel_spec = db_mel_spec.squeeze(0)
    return db_mel_spec


def inverse_mel_spec_to_wav(mel_spec: torch.Tensor) -> torch.Tensor:
    """
    Convert mel spectrogram back to waveform using Griffin-Lim
    
    Args:
        mel_spec: Input mel spectrogram
        
    Returns:
        torch.Tensor: Reconstructed waveform
    """
    device = mel_spec.device
    power_mel_spec = db_to_power_mel_spec(mel_spec)
    spectrogram = get_mel_inverse_transform(device)(power_mel_spec)
    pseudo_wav = get_griffnlim_transform(device)(spectrogram)
    return pseudo_wav


def write_audio_to_file(
    audio: Union[torch.Tensor, np.ndarray],
    filename: str,
    sample_rate: int = None,
    normalized: bool = True
) -> None:
    """
    Write audio array to file (supports wav, mp3, etc.)
    
    Args:
        audio: Audio data as tensor or numpy array
        filename: Output filename
        sample_rate: Sample rate (defaults to config.sr)
        normalized: Whether audio is normalized to [-1, 1]
    """
    if sample_rate is None:
        sample_rate = config.sr
    
    # Convert to numpy if tensor
    if isinstance(audio, torch.Tensor):
        audio = audio.detach().cpu().numpy()
    
    # Ensure audio is 1D
    if audio.ndim > 1:
        audio = audio.squeeze()
    
    # Normalize if needed
    if not normalized:
        # Assume audio is in range that needs normalization
        audio = audio / np.max(np.abs(audio))
    
    try:
        # Convert to tensor for torchaudio
        audio_tensor = torch.from_numpy(audio).unsqueeze(0)  # Add channel dimension
        
        # Save using torchaudio (supports many formats)
        torchaudio.save(filename, audio_tensor, sample_rate)
    except RuntimeError as e:
        # Fallback to scipy if torchaudio backend fails
        print(f"Warning: torchaudio save failed ({e}), using scipy fallback...")
        try:
            from scipy.io import wavfile
            # Convert to int16 for wav format
            audio_int16 = (audio * 32767).astype(np.int16)
            wavfile.write(filename, sample_rate, audio_int16)
        except ImportError:
            # Final fallback - save as numpy array
            print("Warning: scipy not available, saving as .npy file...")
            np.save(filename.replace('.wav', '.npy'), audio)


def audio_to_bytes(
    audio: Union[torch.Tensor, np.ndarray],
    sample_rate: int = None,
    format: str = "wav"
) -> bytes:
    """
    Convert audio to bytes for streaming or API responses
    
    Args:
        audio: Audio data
        sample_rate: Sample rate
        format: Audio format ("wav", "mp3", etc.)
        
    Returns:
        bytes: Audio data as bytes
    """
    if sample_rate is None:
        sample_rate = config.sr
    
    # Convert to numpy if tensor
    if isinstance(audio, torch.Tensor):
        audio = audio.detach().cpu().numpy()
    
    # Ensure audio is 1D and float32
    if audio.ndim > 1:
        audio = audio.squeeze()
    
    # Convert to tensor for torchaudio
    audio_tensor = torch.from_numpy(audio.astype(np.float32)).unsqueeze(0)
    
    # Save to bytes buffer
    buffer = io.BytesIO()
    torchaudio.save(buffer, audio_tensor, sample_rate, format=format)
    buffer.seek(0)
    return buffer.read() 