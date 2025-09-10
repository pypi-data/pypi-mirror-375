"""
Beast format message decoder.
"""

from typing import Optional, Iterator
from .types import BeastMessage, MessageType


class BeastDecoder:
    """Decoder for Beast binary format messages."""
    
    def __init__(self):
        """Initialize Beast decoder."""
        self.buffer = bytearray()
    
    def feed(self, data: bytes) -> Iterator[BeastMessage]:
        """
        Feed raw data to the decoder and yield complete messages.
        
        Args:
            data: Raw Beast format data
            
        Yields:
            Complete Beast messages
        """
        self.buffer.extend(data)
        
        while True:
            message = self._extract_message()
            if message is None:
                break
            yield message
    
    def _extract_message(self) -> Optional[BeastMessage]:
        """Extract a single message from the buffer."""
        if len(self.buffer) < 2:
            return None
        
        # Look for Beast message start
        escape_pos = self.buffer.find(0x1A)
        if escape_pos == -1:
            return None
        
        # Remove any data before the escape byte
        if escape_pos > 0:
            self.buffer = self.buffer[escape_pos:]
        
        if len(self.buffer) < 2:
            return None
        
        # Check message type
        if self.buffer[1] not in [MessageType.MODE_S_SHORT, MessageType.MODE_S_LONG]:
            # Invalid message type, skip this escape byte
            self.buffer = self.buffer[1:]
            return self._extract_message()
        
        msg_type = MessageType(self.buffer[1])
        
        # Calculate expected message length
        if msg_type == MessageType.MODE_S_SHORT:
            modes_len = 7
        else:  # MODE_S_LONG
            modes_len = 14
        
        # Minimum message length: escape(1) + type(1) + timestamp(6) + signal(1) + modes_message
        min_len = 1 + 1 + 6 + 1 + modes_len
        
        if len(self.buffer) < min_len:
            return None  # Not enough data yet
        
        # Extract message components
        try:
            # Handle escaped bytes while extracting
            extracted_data = bytearray()
            extracted_data.append(self.buffer[0])  # Escape byte
            extracted_data.append(self.buffer[1])  # Message type
            
            pos = 2
            data_bytes_needed = 6 + 1 + modes_len  # timestamp + signal + modes_message
            data_bytes_extracted = 0
            
            while data_bytes_extracted < data_bytes_needed and pos < len(self.buffer):
                byte_val = self.buffer[pos]
                extracted_data.append(byte_val)
                pos += 1
                data_bytes_extracted += 1
                
                # Handle escaped 0x1A bytes (but not the initial escape byte)
                if byte_val == 0x1A and pos < len(self.buffer) and self.buffer[pos] == 0x1A:
                    pos += 1  # Skip the second 0x1A
            
            if data_bytes_extracted < data_bytes_needed:
                return None  # Not enough data
            
            # Parse the extracted message
            timestamp = int.from_bytes(extracted_data[2:8], 'big')
            signal_level = extracted_data[8]
            modes_message = bytes(extracted_data[9:9 + modes_len])
            
            # Remove processed data from buffer
            self.buffer = self.buffer[pos:]
            
            return BeastMessage(
                raw_data=bytes(extracted_data),
                timestamp=timestamp,
                signal_level=signal_level,
                message_type=msg_type,
                modes_message=modes_message
            )
            
        except (IndexError, ValueError):
            # Malformed message, skip this escape byte
            self.buffer = self.buffer[1:]
            return self._extract_message()
    
    def clear_buffer(self):
        """Clear the internal buffer."""
        self.buffer.clear()


def decode_beast_message(data: bytes) -> Optional[BeastMessage]:
    """
    Convenience function to decode a single Beast message.
    
    Args:
        data: Raw Beast format message
        
    Returns:
        Decoded Beast message or None if invalid
    """
    decoder = BeastDecoder()
    messages = list(decoder.feed(data))
    return messages[0] if messages else None