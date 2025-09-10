from . import misc

# For all Mode-S messages
GENERATOR = "1111111111111010000001001"


def crc(message: str, encode: bool = True) -> str:
    """
    Calculate CRC for Mode-S message.
    
    Args:
        message: Hexadecimal message string
        encode: Whether to encode (set last 24 bits to 0) or verify
    
    Returns:
        24-bit CRC remainder as binary string
    """
    binary_message = list(misc.hexadecimal_to_binary(message))
    generator = [int(c) for c in GENERATOR]
    
    if encode:
        # Set last 24 bits to 0 for encoding
        for i in range(len(binary_message) - 24, len(binary_message)):
            binary_message[i] = '0'
    
    # Perform polynomial division
    for i in range(len(binary_message) - 24):
        if binary_message[i] == '1':
            for j in range(len(generator)):
                binary_message[i + j] = str(int(binary_message[i + j]) ^ generator[j])
    
    # Return the remainder (last 24 bits)
    remainder = ''.join(binary_message[-24:])
    return remainder