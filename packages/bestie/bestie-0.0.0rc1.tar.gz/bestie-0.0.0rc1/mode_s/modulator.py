from . import misc


def frame_1090es_ppm_modulate_cpr(adsb_even_frame: bytes, adsb_odd_frame: bytes) -> bytes:
    """
    Modulate CPR frames for 1090ES transmission.
    
    Args:
        adsb_even_frame: Even CPR frame bytes
        adsb_odd_frame: Odd CPR frame bytes
    
    Returns:
        Modulated frame data
    """
    ppm_array = bytearray()
    
    # Add preamble
    ppm_array.extend([0] * 48)
    ppm_array.extend([0xA1, 0x40])
    
    # Process even frame
    for byte_val in adsb_even_frame:
        word16 = misc.pack_bits(manchester_encode(~byte_val & 0xFF))
        ppm_array.extend(word16)
    
    # Add gap
    ppm_array.extend([0] * 100)
    ppm_array.extend([0xA1, 0x40])
    
    # Process odd frame
    for byte_val in adsb_odd_frame:
        word16 = misc.pack_bits(manchester_encode(~byte_val & 0xFF))
        ppm_array.extend(word16)
    
    # Add trailing zeros
    ppm_array.extend([0] * 48)
    
    return bytes(ppm_array)


def pulse_position_modulation(adsb_frame: bytes) -> bytes:
    """
    Apply pulse position modulation to ADS-B frame.
    
    Args:
        adsb_frame: ADS-B frame bytes
    
    Returns:
        Modulated frame data
    """
    ppm_array = bytearray()
    
    # Add preamble
    ppm_array.extend([0] * 48)
    ppm_array.extend([0xA1, 0x40])
    
    # Process frame
    for byte_val in adsb_frame:
        word16 = misc.pack_bits(manchester_encode(~byte_val & 0xFF))
        ppm_array.extend(word16)
    
    # Add trailing zeros
    ppm_array.extend([0] * 100)
    
    return bytes(ppm_array)


def manchester_encode(byte_val: int) -> list[int]:
    """
    Manchester encode a byte.
    
    Args:
        byte_val: Byte value to encode
    
    Returns:
        List of Manchester encoded bits
    """
    manchester_array = []
    
    for i in range(7, -1, -1):
        if misc.extract_bit(byte_val, i):
            manchester_array.extend([0, 1])
        else:
            manchester_array.extend([1, 0])
    
    return manchester_array


def generate_sdr_output(ppm_array: bytes) -> bytes:
    """
    Generate SDR output signal.
    
    Args:
        ppm_array: Pulse position modulated array
    
    Returns:
        I/Q sample data for SDR
    """
    ppm_bits = misc.unpack_bits(ppm_array)
    sdr_output = bytearray()
    
    for bit in ppm_bits:
        if bit == 1:
            i_val, q_val = 127, 127
        else:
            i_val, q_val = 0, 0
        sdr_output.extend([i_val, q_val])
    
    return bytes(sdr_output)