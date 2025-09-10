"""
Data types for Beast format encoding.
"""

from dataclasses import dataclass
from typing import Optional
from enum import IntEnum


class MessageType(IntEnum):
    """Beast message types."""
    MODE_S_SHORT = 0x32  # 7-byte Mode-S message
    MODE_S_LONG = 0x33   # 14-byte Mode-S message


@dataclass
class BeastMessage:
    """Represents a complete Beast format message."""
    raw_data: bytes
    timestamp: int
    signal_level: int
    message_type: MessageType
    modes_message: bytes
    
    def __len__(self) -> int:
        """Return total message length."""
        return len(self.raw_data)
    
    def hex(self) -> str:
        """Return message as hex string."""
        return self.raw_data.hex().upper()