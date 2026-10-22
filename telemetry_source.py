import math


def generate_mock_packet(mission_time, packet_count):
    """Generate one simulated telemetry packet."""

    if mission_time < 30:
        altitude = 10 + mission_time * 8
        state = "ASCENT"

    elif mission_time < 40:
        altitude = 250 + (mission_time - 30) * 2
        state = "APOGEE"

    elif mission_time < 80:
        altitude = 270 - (mission_time - 40) * 5
        state = "DESCENT"

    else:
        altitude = max(
            0,
            70 - (mission_time - 80) * 3,
        )

        state = "LANDED" if altitude == 0 else "DESCENT"

    temperature = 23 + 2 * math.sin(mission_time / 10)

    battery_voltage = max(
        3.0,
        4.2 - mission_time * 0.001,
    )

    return (
        f"TEAM8,{mission_time:.2f},{packet_count},"
        f"{state},{altitude:.2f},{temperature:.2f},"
        f"{battery_voltage:.2f}"
    )