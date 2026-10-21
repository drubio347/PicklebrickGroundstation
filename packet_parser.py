def parse_packet(packet):
    """Parse a comma-separated CanSat telemetry packet."""

    fields = packet.strip().split(",")

    if len(fields) != 14:
        raise ValueError(
            f"Expected 14 fields, received {len(fields)}"
        )

    data = {
        "team_id": fields[0],
        "mission_time": float(fields[1]),
        "packet_count": int(fields[2]),
        "state": fields[3],
        "altitude": float(fields[4]),
        "temperature": float(fields[5]),
        "pressure": float(fields[6]),
        "battery_voltage": float(fields[7]),
        "latitude": float(fields[8]),
        "longitude": float(fields[9]),
        "accel_x": float(fields[10]),
        "accel_y": float(fields[11]),
        "accel_z": float(fields[12]),
        "satellites": int(fields[13]),
    }

    return data