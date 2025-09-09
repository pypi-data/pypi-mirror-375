"""
Main TTS model implementation for Arthemis TTS
"""
import math
import torch
import torch.nn.functional as F
import torch.nn as nn
from tqdm import tqdm
from typing import Tuple, Optional

from .config import config
from .utils import mask_from_sequence_lengths
from .text_processing import text_to_sequence


class EncoderBlock(nn.Module):
    """Transformer encoder block"""
    
    def __init__(self):
        super(EncoderBlock, self).__init__()
        self.norm_1 = nn.LayerNorm(normalized_shape=config.embedding_size)
        self.attn = torch.nn.MultiheadAttention(
            embed_dim=config.embedding_size,
            num_heads=4,
            dropout=0.1,
            batch_first=True
        )
        self.dropout_1 = torch.nn.Dropout(0.1)

        self.norm_2 = nn.LayerNorm(normalized_shape=config.embedding_size)

        self.linear_1 = nn.Linear(config.embedding_size, config.dim_feedforward)
        self.dropout_2 = torch.nn.Dropout(0.1)
        self.linear_2 = nn.Linear(config.dim_feedforward, config.embedding_size)
        self.dropout_3 = torch.nn.Dropout(0.1)

    def forward(self, x, attn_mask=None, key_padding_mask=None):
        x_out = self.norm_1(x)
        x_out, _ = self.attn(
            query=x_out,
            key=x_out,
            value=x_out,
            attn_mask=attn_mask,
            key_padding_mask=key_padding_mask
        )
        x_out = self.dropout_1(x_out)
        x = x + x_out

        x_out = self.norm_2(x)
        x_out = self.linear_1(x_out)
        x_out = F.relu(x_out)
        x_out = self.dropout_2(x_out)
        x_out = self.linear_2(x_out)
        x_out = self.dropout_3(x_out)

        x = x + x_out
        return x


class DecoderBlock(nn.Module):
    """Transformer decoder block"""
    
    def __init__(self):
        super(DecoderBlock, self).__init__()
        self.norm_1 = nn.LayerNorm(normalized_shape=config.embedding_size)
        self.self_attn = torch.nn.MultiheadAttention(
            embed_dim=config.embedding_size,
            num_heads=4,
            dropout=0.1,
            batch_first=True
        )
        self.dropout_1 = torch.nn.Dropout(0.1)

        self.norm_2 = nn.LayerNorm(normalized_shape=config.embedding_size)
        self.attn = torch.nn.MultiheadAttention(
            embed_dim=config.embedding_size,
            num_heads=4,
            dropout=0.1,
            batch_first=True
        )
        self.dropout_2 = torch.nn.Dropout(0.1)

        self.norm_3 = nn.LayerNorm(normalized_shape=config.embedding_size)
        self.linear_1 = nn.Linear(config.embedding_size, config.dim_feedforward)
        self.dropout_3 = torch.nn.Dropout(0.1)
        self.linear_2 = nn.Linear(config.dim_feedforward, config.embedding_size)
        self.dropout_4 = torch.nn.Dropout(0.1)

    def forward(self, x, memory, x_attn_mask=None, x_key_padding_mask=None,
                memory_attn_mask=None, memory_key_padding_mask=None):
        x_out, _ = self.self_attn(
            query=x,
            key=x,
            value=x,
            attn_mask=x_attn_mask,
            key_padding_mask=x_key_padding_mask
        )
        x_out = self.dropout_1(x_out)
        x = self.norm_1(x + x_out)

        x_out, _ = self.attn(
            query=x,
            key=memory,
            value=memory,
            attn_mask=memory_attn_mask,
            key_padding_mask=memory_key_padding_mask
        )
        x_out = self.dropout_2(x_out)
        x = self.norm_2(x + x_out)

        x_out = self.linear_1(x)
        x_out = F.relu(x_out)
        x_out = self.dropout_3(x_out)
        x_out = self.linear_2(x_out)
        x_out = self.dropout_4(x_out)
        x = self.norm_3(x + x_out)

        return x


class EncoderPreNet(nn.Module):
    """Text encoder pre-net"""
    
    def __init__(self):
        super(EncoderPreNet, self).__init__()
        
        self.embedding = nn.Embedding(
            num_embeddings=config.text_num_embeddings,
            embedding_dim=config.encoder_embedding_size
        )

        self.linear_1 = nn.Linear(
            config.encoder_embedding_size,
            config.encoder_embedding_size
        )
        self.linear_2 = nn.Linear(
            config.encoder_embedding_size,
            config.embedding_size
        )

        # Convolutional layers
        self.conv_1 = nn.Conv1d(
            config.encoder_embedding_size,
            config.encoder_embedding_size,
            kernel_size=config.encoder_kernel_size,
            stride=1,
            padding=int((config.encoder_kernel_size - 1) / 2),
            dilation=1
        )
        self.bn_1 = nn.BatchNorm1d(config.encoder_embedding_size)
        self.dropout_1 = torch.nn.Dropout(0.5)

        self.conv_2 = nn.Conv1d(
            config.encoder_embedding_size,
            config.encoder_embedding_size,
            kernel_size=config.encoder_kernel_size,
            stride=1,
            padding=int((config.encoder_kernel_size - 1) / 2),
            dilation=1
        )
        self.bn_2 = nn.BatchNorm1d(config.encoder_embedding_size)
        self.dropout_2 = torch.nn.Dropout(0.5)

        self.conv_3 = nn.Conv1d(
            config.encoder_embedding_size,
            config.encoder_embedding_size,
            kernel_size=config.encoder_kernel_size,
            stride=1,
            padding=int((config.encoder_kernel_size - 1) / 2),
            dilation=1
        )
        self.bn_3 = nn.BatchNorm1d(config.encoder_embedding_size)
        self.dropout_3 = torch.nn.Dropout(0.5)

    def forward(self, text):
        x = self.embedding(text)  # (N, S, E)
        x = self.linear_1(x)

        x = x.transpose(2, 1)  # (N, E, S)

        x = self.conv_1(x)
        x = self.bn_1(x)
        x = F.relu(x)
        x = self.dropout_1(x)

        x = self.conv_2(x)
        x = self.bn_2(x)
        x = F.relu(x)
        x = self.dropout_2(x)

        x = self.conv_3(x)
        x = self.bn_3(x)
        x = F.relu(x)
        x = self.dropout_3(x)

        x = x.transpose(1, 2)  # (N, S, E)
        x = self.linear_2(x)

        return x


class PostNet(nn.Module):
    """Mel spectrogram post-processing network"""
    
    def __init__(self):
        super(PostNet, self).__init__()
        
        # 5 convolutional layers
        self.conv_1 = nn.Conv1d(
            config.mel_freq,
            config.postnet_embedding_size,
            kernel_size=config.postnet_kernel_size,
            stride=1,
            padding=int((config.postnet_kernel_size - 1) / 2),
            dilation=1
        )
        self.bn_1 = nn.BatchNorm1d(config.postnet_embedding_size)
        self.dropout_1 = torch.nn.Dropout(0.5)

        self.conv_2 = nn.Conv1d(
            config.postnet_embedding_size,
            config.postnet_embedding_size,
            kernel_size=config.postnet_kernel_size,
            stride=1,
            padding=int((config.postnet_kernel_size - 1) / 2),
            dilation=1
        )
        self.bn_2 = nn.BatchNorm1d(config.postnet_embedding_size)
        self.dropout_2 = torch.nn.Dropout(0.5)

        self.conv_3 = nn.Conv1d(
            config.postnet_embedding_size,
            config.postnet_embedding_size,
            kernel_size=config.postnet_kernel_size,
            stride=1,
            padding=int((config.postnet_kernel_size - 1) / 2),
            dilation=1
        )
        self.bn_3 = nn.BatchNorm1d(config.postnet_embedding_size)
        self.dropout_3 = torch.nn.Dropout(0.5)

        self.conv_4 = nn.Conv1d(
            config.postnet_embedding_size,
            config.postnet_embedding_size,
            kernel_size=config.postnet_kernel_size,
            stride=1,
            padding=int((config.postnet_kernel_size - 1) / 2),
            dilation=1
        )
        self.bn_4 = nn.BatchNorm1d(config.postnet_embedding_size)
        self.dropout_4 = torch.nn.Dropout(0.5)

        self.conv_5 = nn.Conv1d(
            config.postnet_embedding_size,
            config.postnet_embedding_size,
            kernel_size=config.postnet_kernel_size,
            stride=1,
            padding=int((config.postnet_kernel_size - 1) / 2),
            dilation=1
        )
        self.bn_5 = nn.BatchNorm1d(config.postnet_embedding_size)
        self.dropout_5 = torch.nn.Dropout(0.5)

        self.conv_6 = nn.Conv1d(
            config.postnet_embedding_size,
            config.mel_freq,
            kernel_size=config.postnet_kernel_size,
            stride=1,
            padding=int((config.postnet_kernel_size - 1) / 2),
            dilation=1
        )
        self.bn_6 = nn.BatchNorm1d(config.mel_freq)
        self.dropout_6 = torch.nn.Dropout(0.5)

    def forward(self, x):
        # x - (N, TIME, FREQ)
        x = x.transpose(2, 1)  # (N, FREQ, TIME)

        x = self.conv_1(x)
        x = self.bn_1(x)
        x = torch.tanh(x)
        x = self.dropout_1(x)

        x = self.conv_2(x)
        x = self.bn_2(x)
        x = torch.tanh(x)
        x = self.dropout_2(x)

        x = self.conv_3(x)
        x = self.bn_3(x)
        x = torch.tanh(x)
        x = self.dropout_3(x)

        x = self.conv_4(x)
        x = self.bn_4(x)
        x = torch.tanh(x)
        x = self.dropout_4(x)

        x = self.conv_5(x)
        x = self.bn_5(x)
        x = torch.tanh(x)
        x = self.dropout_5(x)

        x = self.conv_6(x)
        x = self.bn_6(x)
        x = self.dropout_6(x)

        x = x.transpose(1, 2)  # (N, TIME, FREQ)
        return x


class DecoderPreNet(nn.Module):
    """Mel spectrogram decoder pre-net"""
    
    def __init__(self):
        super(DecoderPreNet, self).__init__()
        self.linear_1 = nn.Linear(config.mel_freq, config.embedding_size)
        self.linear_2 = nn.Linear(config.embedding_size, config.embedding_size)

    def forward(self, x):
        x = self.linear_1(x)
        x = F.relu(x)
        x = F.dropout(x, p=0.5, training=True)

        x = self.linear_2(x)
        x = F.relu(x)
        x = F.dropout(x, p=0.5, training=True)

        return x


class ArthemisTTS(nn.Module):
    """
    Main Arthemis TTS model
    
    A transformer-based text-to-speech model that converts text sequences
    to mel spectrograms, which can then be converted to audio.
    """
    
    def __init__(self, device: str = "cpu"):
        super(ArthemisTTS, self).__init__()
        self.device = device

        # Sub-networks
        self.encoder_prenet = EncoderPreNet()
        self.decoder_prenet = DecoderPreNet()
        self.postnet = PostNet()

        # Positional encoding
        self.pos_encoding = nn.Embedding(
            num_embeddings=config.max_mel_time,
            embedding_dim=config.embedding_size
        )

        # Transformer blocks
        self.encoder_block_1 = EncoderBlock()
        self.encoder_block_2 = EncoderBlock()
        self.encoder_block_3 = EncoderBlock()

        self.decoder_block_1 = DecoderBlock()
        self.decoder_block_2 = DecoderBlock()
        self.decoder_block_3 = DecoderBlock()

        # Output layers
        self.linear_1 = nn.Linear(config.embedding_size, config.mel_freq)
        self.linear_2 = nn.Linear(config.embedding_size, 1)

        # Memory normalization
        self.norm_memory = nn.LayerNorm(normalized_shape=config.embedding_size)

        # Move to device
        self.to(device)

    def forward(self, text, text_len, mel, mel_len):
        """Forward pass for training"""
        N = text.shape[0]
        S = text.shape[1]
        TIME = mel.shape[1]

        # Create masks
        self.src_key_padding_mask = torch.zeros(
            (N, S), device=text.device
        ).masked_fill(
            ~mask_from_sequence_lengths(text_len, max_length=S),
            float("-inf")
        )

        self.src_mask = torch.zeros(
            (S, S), device=text.device
        ).masked_fill(
            torch.triu(
                torch.full((S, S), True, dtype=torch.bool), diagonal=1
            ).to(text.device),
            float("-inf")
        )

        self.tgt_key_padding_mask = torch.zeros(
            (N, TIME), device=mel.device
        ).masked_fill(
            ~mask_from_sequence_lengths(mel_len, max_length=TIME),
            float("-inf")
        )

        self.tgt_mask = torch.zeros(
            (TIME, TIME), device=mel.device
        ).masked_fill(
            torch.triu(
                torch.full(
                    (TIME, TIME), True, device=mel.device, dtype=torch.bool
                ), diagonal=1
            ),
            float("-inf")
        )

        self.memory_mask = torch.zeros(
            (TIME, S), device=mel.device
        ).masked_fill(
            torch.triu(
                torch.full(
                    (TIME, S), True, device=mel.device, dtype=torch.bool
                ), diagonal=1
            ),
            float("-inf")
        )

        # Encoder
        text_x = self.encoder_prenet(text)  # (N, S, E)

        pos_codes = self.pos_encoding(
            torch.arange(config.max_mel_time).to(mel.device)
        )  # (MAX_S_TIME, E)

        S = text_x.shape[1]
        text_x = text_x + pos_codes[:S]

        text_x = self.encoder_block_1(
            text_x,
            attn_mask=self.src_mask,
            key_padding_mask=self.src_key_padding_mask
        )
        text_x = self.encoder_block_2(
            text_x,
            attn_mask=self.src_mask,
            key_padding_mask=self.src_key_padding_mask
        )
        text_x = self.encoder_block_3(
            text_x,
            attn_mask=self.src_mask,
            key_padding_mask=self.src_key_padding_mask
        )  # (N, S, E)

        text_x = self.norm_memory(text_x)

        # Decoder
        mel_x = self.decoder_prenet(mel)  # (N, TIME, E)
        mel_x = mel_x + pos_codes[:TIME]

        mel_x = self.decoder_block_1(
            x=mel_x,
            memory=text_x,
            x_attn_mask=self.tgt_mask,
            x_key_padding_mask=self.tgt_key_padding_mask,
            memory_attn_mask=self.memory_mask,
            memory_key_padding_mask=self.src_key_padding_mask
        )

        mel_x = self.decoder_block_2(
            x=mel_x,
            memory=text_x,
            x_attn_mask=self.tgt_mask,
            x_key_padding_mask=self.tgt_key_padding_mask,
            memory_attn_mask=self.memory_mask,
            memory_key_padding_mask=self.src_key_padding_mask
        )

        mel_x = self.decoder_block_3(
            x=mel_x,
            memory=text_x,
            x_attn_mask=self.tgt_mask,
            x_key_padding_mask=self.tgt_key_padding_mask,
            memory_attn_mask=self.memory_mask,
            memory_key_padding_mask=self.src_key_padding_mask
        )  # (N, TIME, E)

        # Output
        mel_linear = self.linear_1(mel_x)  # (N, TIME, FREQ)
        mel_postnet = self.postnet(mel_linear)  # (N, TIME, FREQ)
        mel_postnet = mel_linear + mel_postnet  # (N, TIME, FREQ)
        stop_token = self.linear_2(mel_x)  # (N, TIME, 1)

        # Apply masking
        bool_mel_mask = self.tgt_key_padding_mask.ne(0).unsqueeze(-1).repeat(
            1, 1, config.mel_freq
        )

        mel_linear = mel_linear.masked_fill(bool_mel_mask, 0)
        mel_postnet = mel_postnet.masked_fill(bool_mel_mask, 0)
        stop_token = stop_token.masked_fill(
            bool_mel_mask[:, :, 0].unsqueeze(-1), 1e3
        ).squeeze(2)

        return mel_postnet, mel_linear, stop_token

    @torch.no_grad()
    def inference(
        self,
        text: torch.Tensor,
        max_length: int = 800,
        stop_token_threshold: float = 0.5,
        with_tqdm: bool = True
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Generate mel spectrogram from text
        
        Args:
            text: Input text tensor of shape (1, seq_len)
            max_length: Maximum generation length
            stop_token_threshold: Threshold for stop token
            with_tqdm: Whether to show progress bar
            
        Returns:
            Tuple of (mel_spectrogram, stop_tokens)
        """
        self.eval()
        text_lengths = torch.tensor(text.shape[1]).unsqueeze(0).to(self.device)
        N = 1
        SOS = torch.zeros((N, 1, config.mel_freq), device=self.device)

        mel_padded = SOS
        mel_lengths = torch.tensor(1).unsqueeze(0).to(self.device)
        stop_token_outputs = torch.FloatTensor([]).to(text.device)

        iters = tqdm(range(max_length)) if with_tqdm else range(max_length)

        for _ in iters:
            mel_postnet, mel_linear, stop_token = self(
                text, text_lengths, mel_padded, mel_lengths
            )

            mel_padded = torch.cat(
                [mel_padded, mel_postnet[:, -1:, :]], dim=1
            )
            
            if torch.sigmoid(stop_token[:, -1]) > stop_token_threshold:
                break
            else:
                stop_token_outputs = torch.cat(
                    [stop_token_outputs, stop_token[:, -1:]], dim=1
                )
                mel_lengths = torch.tensor(mel_padded.shape[1]).unsqueeze(0).to(self.device)

        return mel_postnet, stop_token_outputs

    def synthesize(
        self,
        text: str,
        max_length: int = 800,
        stop_token_threshold: float = 0.5
    ) -> torch.Tensor:
        """
        High-level synthesis function
        
        Args:
            text: Input text string
            max_length: Maximum generation length
            stop_token_threshold: Stop token threshold
            
        Returns:
            torch.Tensor: Generated audio waveform
        """
        from .audio_processing import inverse_mel_spec_to_wav
        
        # Convert text to sequence
        text_seq = text_to_sequence(text).unsqueeze(0).to(self.device)
        
        # Generate mel spectrogram
        mel_postnet, _ = self.inference(
            text_seq,
            max_length=max_length,
            stop_token_threshold=stop_token_threshold,
            with_tqdm=False
        )
        
        # Convert to audio
        audio = inverse_mel_spec_to_wav(mel_postnet.detach()[0].T)
        return audio 