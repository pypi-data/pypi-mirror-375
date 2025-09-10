import math

LATZ = 15


def nz(ctype: int) -> int:
    """Calculate NZ parameter."""
    return 4 * LATZ - ctype


def encode_latitude(ctype: int, surface: int) -> float:
    """Encode latitude zones."""
    tmp = 90.0 if surface == 1 else 360.0
    
    nz_calc = nz(ctype)
    if nz_calc == 0:
        return tmp
    else:
        return tmp / nz_calc


def nl(declat_in: float) -> float:
    """Calculate NL parameter."""
    if abs(declat_in) >= 87.0:
        return 1.0
    
    return math.floor(
        (2.0 * math.pi) * (
            math.acos(
                1.0 - (1.0 - math.cos(math.pi / (2.0 * LATZ))) / 
                (math.cos((math.pi / 180.0) * abs(declat_in)) ** 2)
            ) ** -1
        )
    )


def encode_longitude(latitude: float, ctype: int, surface: int) -> float:
    """Encode longitude zones."""
    tmp = 90.0 if surface == 1 else 360.0
    nl_calc = max(nl(latitude) - ctype, 1)
    return tmp / nl_calc


def cpr_encode(lat: float, lon: float, ctype: int, surface: int) -> tuple[int, int]:
    """
    Encode CPR coordinates.
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        ctype: CPR type (0 for even, 1 for odd)
        surface: Surface flag (1 for surface, 0 for airborne)
    
    Returns:
        Tuple of (encoded_lat, encoded_lon)
    """
    scalar = 2 ** 19 if surface == 1 else 2 ** 17
    
    latitude_zone = encode_latitude(ctype, surface)
    latitude_zones_count = math.floor(
        scalar * ((lat % latitude_zone) / latitude_zone) + 0.5
    )
    
    longitude_zone = encode_longitude(lat, ctype, surface)
    longitude_zones_count = math.floor(
        scalar * ((lon % longitude_zone) / longitude_zone) + 0.5
    )
    
    # Apply 17-bit mask
    encoded_lat = int(latitude_zones_count) & ((1 << 17) - 1)
    encoded_lon = int(longitude_zones_count) & ((1 << 17) - 1)
    
    return encoded_lat, encoded_lon