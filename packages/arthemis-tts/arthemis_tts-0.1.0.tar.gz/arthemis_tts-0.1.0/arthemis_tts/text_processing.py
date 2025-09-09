"""
Text processing utilities for Arthemis TTS
"""
import torch
from typing import Union, List
from .config import config


def create_symbol_to_id_mapping():
    """Create symbol to ID mapping from config symbols"""
    return {s: i for i, s in enumerate(config.symbols)}


# Global symbol mapping
SYMBOL_TO_ID = create_symbol_to_id_mapping()


def text_to_sequence(text: str) -> torch.IntTensor:
    """
    Convert text string to sequence of token IDs
    
    Args:
        text: Input text string
        
    Returns:
        torch.IntTensor: Sequence of token IDs
    """
    text = text.lower()
    seq = []
    
    for char in text:
        token_id = SYMBOL_TO_ID.get(char, None)
        if token_id is not None:
            seq.append(token_id)
    
    # Add end-of-sequence token
    seq.append(SYMBOL_TO_ID["EOS"])
    
    return torch.IntTensor(seq)


def sequence_to_text(sequence: Union[torch.Tensor, List[int]]) -> str:
    """
    Convert sequence of token IDs back to text
    
    Args:
        sequence: Sequence of token IDs
        
    Returns:
        str: Decoded text string
    """
    if isinstance(sequence, torch.Tensor):
        sequence = sequence.tolist()
    
    # Create reverse mapping
    id_to_symbol = {i: s for s, i in SYMBOL_TO_ID.items()}
    
    text = ""
    for token_id in sequence:
        if token_id in id_to_symbol:
            symbol = id_to_symbol[token_id]
            if symbol == "EOS":
                break
            text += symbol
    
    return text


def batch_text_to_sequences(texts: List[str]) -> torch.Tensor:
    """
    Convert batch of texts to padded sequences
    
    Args:
        texts: List of input text strings
        
    Returns:
        torch.Tensor: Padded batch of sequences
    """
    sequences = [text_to_sequence(text) for text in texts]
    
    # Pad sequences to same length
    max_len = max(len(seq) for seq in sequences)
    padded_sequences = []
    
    for seq in sequences:
        padded = torch.zeros(max_len, dtype=torch.int)
        padded[:len(seq)] = seq
        padded_sequences.append(padded)
    
    return torch.stack(padded_sequences) 