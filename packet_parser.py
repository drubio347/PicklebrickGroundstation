def parse_packet(packet):
    """Convert a telemetry string into structured Python data."""

    # Remove whitespace and split the packet at each comma
    fields = packet.strip().split(",")

    # Make sure the packet contains all 7 expected fields
    if len(fields) != 7:
        raise ValueError(
            f"Expected 7 fields, received {len(fields)}"
        )

    # Convert the text into useful values
    data = {
        "team_id": fields[0],
        "mission_time": float(fields[1]),
        "packet_count": int(fields[2]),
        "state": fields[3],
        "altitude": float(fields[4]),
        "temperature": float(fields[5]),
        "battery_voltage": float(fields[6]),
    }

    return data