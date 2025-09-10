import logging

from . import cpr, crc, misc

# ADS-B Data Format (17)
FORMAT = 17

# Aircraft identification charset
AIC_CHARSET = "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_ !\"#$%&'()*+,-./0123456789:;<=>?"


def encode_altitude_mode_s(alt: float, surface: int) -> int:
    """
    Encode altitude for Mode-S.
    
    Args:
        alt: Altitude in feet
        surface: Surface flag (1 for surface, 0 for airborne)
    
    Returns:
        Encoded altitude value
    """
    mbit = 0
    qbit = 1
    encalt = int((int(alt) + 1000) / 25)
    
    if surface == 1:
        tmp1 = (encalt & 0xfe0) << 2
        tmp2 = (encalt & 0x010) << 1
    else:
        tmp1 = (encalt & 0xff8) << 1
        tmp2 = 0
    
    return (encalt & 0x0F) | tmp1 | tmp2 | (mbit << 6) | (qbit << 4)


def get_identification_message(icao: int, tc: int, ca: int, sign: str, cat: int) -> bytes:
    """
    Encode aircraft identification message.
    
    Args:
        icao: ICAO address
        tc: Type code
        ca: Capability
        sign: Aircraft identification (callsign, up to 8 characters)
        cat: Category
    
    Returns:
        Encoded message bytes
    """
    if len(sign) > 8:
        logging.error("Sign must be less than 8 chars")
        return b""
    
    # Pad sign to 8 characters
    if len(sign) < 8:
        sign += " " * (8 - len(sign))
    
    sign_encoded_array = bytearray()
    
    # Format + CA + ICAO
    sign_encoded_array.append((FORMAT << 3) | ca)
    sign_encoded_array.append((icao >> 16) & 0xff)
    sign_encoded_array.append((icao >> 8) & 0xff)
    sign_encoded_array.append(icao & 0xff)
    
    # TC + CAT
    sign_encoded_array.append((tc << 3) | cat)
    
    # SIGN
    symbols = []
    for i in range(8):
        char_position = AIC_CHARSET.find(sign[i])
        if char_position == -1:
            char_position = 32  # Default to space
        logging.info(f"Encoded char {ord(sign[i])} -> {char_position:02x}")
        symbols.append(char_position)
    
    sign_encoded_array.append((symbols[0] << 2) | (symbols[1] >> 4))
    sign_encoded_array.append(((symbols[1] & 0xf) << 4) | (symbols[2] >> 2))
    sign_encoded_array.append(((symbols[2] & 0x3) << 6) | symbols[3])
    sign_encoded_array.append((symbols[4] << 2) | (symbols[5] >> 4))
    sign_encoded_array.append(((symbols[5] & 0xf) << 4) | (symbols[6] >> 2))
    sign_encoded_array.append(((symbols[6] & 0x3) << 6) | symbols[7])
    
    # Convert to hex string for CRC calculation
    sign_string = sign_encoded_array.hex()
    logging.info(f"Sign frame without CRC [{sign_string}]")
    
    # Calculate CRC
    sign_crc = misc.binary_to_integer(crc.crc(sign_string + "000000", True))
    logging.info(f"Sign frame CRC [{sign_crc:06x}]")
    
    # Append CRC
    sign_encoded_array.append((sign_crc >> 16) & 0xff)
    sign_encoded_array.append((sign_crc >> 8) & 0xff)
    sign_encoded_array.append(sign_crc & 0xff)
    
    logging.info(f"Sign frame data [{sign_encoded_array.hex()}]")
    return bytes(sign_encoded_array)


def get_encoded_position(ca: int, icao: int, tc: int, ss: int, nicsb: int, 
                        alt: float, time: int, lat: float, lon: float, 
                        surface: int) -> tuple[bytes, bytes]:
    """
    Encode aircraft position with CPR.
    
    Args:
        ca: Capability
        icao: ICAO address
        tc: Type code
        ss: Surveillance status
        nicsb: Navigation integrity category subfield
        alt: Altitude in feet
        time: Time
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        surface: Surface flag (1 for surface, 0 for airborne)
    
    Returns:
        Tuple of (even_frame, odd_frame) bytes
    """
    # Altitude
    logging.info(f"Encode altitude [{alt}] with surface flag [{surface}]")
    enc_alt = encode_altitude_mode_s(alt, surface)
    logging.info(f"Encoded altitude [0x{enc_alt:04x}]")
    
    # Position - Even frame
    logging.info(f"Encode even frame with lat [{lat}] and lon [{lon}]")
    even_lat, even_lon = cpr.cpr_encode(lat, lon, 0, surface)
    logging.info(f"Encoded even frame lat [0x{even_lat:05x}] and lon [0x{even_lon:05x}]")
    
    # Position - Odd frame
    logging.info(f"Encode odd frame with lat [{lat}] and lon [{lon}]")
    odd_lat, odd_lon = cpr.cpr_encode(lat, lon, 1, surface)
    logging.info(f"Encoded odd frame lat [0x{odd_lat:05x}] and lon [0x{odd_lon:05x}]")
    
    # Encode even data
    ff = 0
    data_even_array = bytearray()
    
    # Format + CA + ICAO
    data_even_array.append((FORMAT << 3) | ca)
    data_even_array.append((icao >> 16) & 0xff)
    data_even_array.append((icao >> 8) & 0xff)
    data_even_array.append(icao & 0xff)
    
    # Lat + Lon + Alt (even)
    data_even_array.append((tc << 3) | (ss << 1) | nicsb)
    data_even_array.append((enc_alt >> 4) & 0xff)
    data_even_array.append(((enc_alt & 0xf) << 4) | (time << 3) | (ff << 2) | (even_lat >> 15))
    data_even_array.append((even_lat >> 7) & 0xff)
    data_even_array.append(((even_lat & 0x7f) << 1) | (even_lon >> 16))
    data_even_array.append((even_lon >> 8) & 0xff)
    data_even_array.append(even_lon & 0xff)
    
    # Calculate CRC for even frame
    data_even_string = data_even_array[:11].hex()
    logging.info(f"Even frame without CRC [{data_even_string}]")
    
    data_even_crc = misc.binary_to_integer(crc.crc(data_even_string + "000000", True))
    logging.info(f"Even data CRC [{data_even_crc:06x}]")
    
    # Append CRC to even frame
    data_even_array.append((data_even_crc >> 16) & 0xff)
    data_even_array.append((data_even_crc >> 8) & 0xff)
    data_even_array.append(data_even_crc & 0xff)
    logging.info(f"Even data [{data_even_array.hex()}]")
    
    # Encode odd data
    ff = 1
    data_odd_array = bytearray()
    
    # Format + CA + ICAO
    data_odd_array.append((FORMAT << 3) | ca)
    data_odd_array.append((icao >> 16) & 0xff)
    data_odd_array.append((icao >> 8) & 0xff)
    data_odd_array.append(icao & 0xff)
    
    # Lat + Lon + Alt (odd)
    data_odd_array.append((tc << 3) | (ss << 1) | nicsb)
    data_odd_array.append((enc_alt >> 4) & 0xff)
    data_odd_array.append(((enc_alt & 0xf) << 4) | (time << 3) | (ff << 2) | (odd_lat >> 15))
    data_odd_array.append((odd_lat >> 7) & 0xff)
    data_odd_array.append(((odd_lat & 0x7f) << 1) | (odd_lon >> 16))
    data_odd_array.append((odd_lon >> 8) & 0xff)
    data_odd_array.append(odd_lon & 0xff)
    
    # Calculate CRC for odd frame
    data_odd_string = data_odd_array[:11].hex()
    logging.info(f"Odd frame without CRC [{data_odd_string}]")
    
    data_odd_crc = misc.binary_to_integer(crc.crc(data_odd_string + "000000", True))
    logging.info(f"Odd data CRC [{data_odd_crc:06x}]")
    
    # Append CRC to odd frame
    data_odd_array.append((data_odd_crc >> 16) & 0xff)
    data_odd_array.append((data_odd_crc >> 8) & 0xff)
    data_odd_array.append(data_odd_crc & 0xff)
    logging.info(f"Odd data [{data_odd_array.hex()}]")
    
    return bytes(data_even_array), bytes(data_odd_array)