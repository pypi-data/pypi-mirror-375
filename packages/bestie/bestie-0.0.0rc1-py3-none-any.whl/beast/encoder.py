"""
Beast format message encoder for Mode-S messages.
"""

import time
from typing import Optional
from .types import BeastMessage, MessageType


class BeastEncoder:
    """Encoder for Beast binary format messages."""
    
    def __init__(self):
        """Initialize Beast encoder."""
        pass
    
    def encode_message(self, modes_message: bytes, 
                      timestamp: Optional[int] = None,
                      signal_level: int = 0xFF) -> BeastMessage:
        """
        Encode a Mode-S message in Beast format.
        
        Args:
            modes_message: Raw Mode-S message (7 or 14 bytes)
            timestamp: Message timestamp in microseconds (None = current time)
            signal_level: Signal level (0-255, default 255)
        
        Returns:
            Complete Beast format message
        
        Raises:
            ValueError: If message length is invalid
        """
        if len(modes_message) == 7:
            msg_type = MessageType.MODE_S_SHORT
        elif len(modes_message) == 14:
            msg_type = MessageType.MODE_S_LONG
        else:
            raise ValueError(f"Invalid Mode-S message length: {len(modes_message)} (expected 7 or 14)")
        
        # Use current time if no timestamp provided
        if timestamp is None:
            timestamp = int(time.time() * 1_000_000) & 0xFFFFFFFFFFFF
        
        # Build Beast message
        beast_msg = bytearray()
        beast_msg.append(0x1A)  # Escape byte
        beast_msg.append(msg_type)  # Message type
        
        # Timestamp (6 bytes, big-endian)
        beast_msg.extend(timestamp.to_bytes(6, 'big'))
        
        # Signal level (1 byte)
        beast_msg.append(signal_level & 0xFF)
        
        # Mode-S message
        beast_msg.extend(modes_message)
        
        # Escape any 0x1A bytes in the data portion (after escape byte and type)
        escaped_msg = bytearray()
        escaped_msg.extend(beast_msg[:2])  # Keep escape and type as-is
        
        for byte_val in beast_msg[2:]:
            escaped_msg.append(byte_val)
            if byte_val == 0x1A:
                escaped_msg.append(0x1A)  # Double escape
        
        raw_data = bytes(escaped_msg)
        
        return BeastMessage(
            raw_data=raw_data,
            timestamp=timestamp,
            signal_level=signal_level,
            message_type=msg_type,
            modes_message=modes_message
        )
    
    def encode_multiple(self, messages: list[bytes], 
                       base_timestamp: Optional[int] = None,
                       interval_us: int = 500000,
                       signal_level: int = 0xFF) -> list[BeastMessage]:
        """
        Encode multiple Mode-S messages with sequential timestamps.
        
        Args:
            messages: List of Mode-S messages
            base_timestamp: Base timestamp in microseconds (None = current time)
            interval_us: Interval between messages in microseconds
            signal_level: Signal level for all messages
        
        Returns:
            List of Beast format messages
        """
        if base_timestamp is None:
            base_timestamp = int(time.time() * 1_000_000) & 0xFFFFFFFFFFFF
        
        beast_messages = []
        
        for i, msg in enumerate(messages):
            timestamp = (base_timestamp + (i * interval_us)) & 0xFFFFFFFFFFFF
            beast_msg = self.encode_message(msg, timestamp, signal_level)
            beast_messages.append(beast_msg)
        
        return beast_messages


def encode_beast_message(modes_message: bytes, 
                        timestamp: Optional[int] = None,
                        signal_level: int = 0xFF) -> bytes:
    """
    Convenience function to encode a single Mode-S message.
    
    Args:
        modes_message: Raw Mode-S message (7 or 14 bytes)
        timestamp: Message timestamp in microseconds (None = current time)
        signal_level: Signal level (0-255, default 255)
    
    Returns:
        Raw Beast format message bytes
    """
    encoder = BeastEncoder()
    beast_msg = encoder.encode_message(modes_message, timestamp, signal_level)
    return beast_msg.raw_data