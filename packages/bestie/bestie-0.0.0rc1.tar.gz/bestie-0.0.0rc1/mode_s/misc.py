import math


def binary_to_integer(binary_str: str) -> int:
    """Convert binary string to integer."""
    return int(binary_str, 2)


def extract_bit(byte_val: int, bit_position: int) -> bool:
    """Extract a specific bit from a byte."""
    return (byte_val >> bit_position) & 1 == 1


def pack_bits(bits: list[int]) -> bytes:
    """Pack bits into bytes (equivalent to numpy.packbits)."""
    bytes_count = math.ceil(len(bits) / 8.0)
    packed_bytes = bytearray(bytes_count)
    
    for position, bit in enumerate(bits):
        if bit != 0:
            byte_index = position // 8
            bit_position = 7 - (position % 8)
            packed_bytes[byte_index] |= 1 << bit_position
    
    return bytes(packed_bytes)


def save_to_file(filename: str, data: bytes) -> None:
    """Save data to file."""
    with open(filename, 'wb') as f:
        f.write(data)


def unpack_bits(data: bytes) -> list[int]:
    """Unpack bytes to bits (equivalent to numpy.unpackbits)."""
    bits_array = []
    for byte_val in data:
        for i in range(7, -1, -1):
            bits_array.append((byte_val >> i) & 1)
    return bits_array


def hexadecimal_to_binary(hex_str: str) -> str:
    """Convert hexadecimal string to binary string."""
    binary_int = int(hex_str, 16)
    binary_str = bin(binary_int)[2:]  # Remove '0b' prefix
    
    # Pad with zeros to match expected bit count
    bits_count = len(hex_str) * 4
    if len(binary_str) < bits_count:
        binary_str = '0' * (bits_count - len(binary_str)) + binary_str
    
    return binary_str