import time
import math

from packet_parser import parse_packet
from data_logger import save_telemetry


def generate_mock_packet(elapsed_time, packet_count):
    """Generate one simulated CanSat telemetry packet."""

    # Simulate a flight profile.
    if elapsed_time < 20:
        state = "ASCENT"
        altitude = 10 + 8 * elapsed_time

    elif elapsed_time < 30:
        state = "APOGEE"
        altitude = 170 + 2 * math.sin(elapsed_time)

    elif elapsed_time < 60:
        state = "DESCENT"
        altitude = max(0, 190 - 6 * (elapsed_time - 30))

    else:
        state = "LANDED"
        altitude = 0

    temperature = 24 + 0.03 * elapsed_time
    pressure = 1013.25 - altitude * 0.12
    battery_voltage = max(3.3, 4.2 - 0.002 * elapsed_time)

    # Simulated GPS coordinates near Huntsville.
    latitude = 34.7304 + 0.00001 * math.sin(elapsed_time / 5)
    longitude = -86.5861 + 0.00001 * math.cos(elapsed_time / 5)

    # Simulated acceleration values.
    accel_x = 0.2 * math.sin(elapsed_time)
    accel_y = 0.2 * math.cos(elapsed_time)
    accel_z = 9.81

    satellites = 8

    return (
        f"TEAM8,{elapsed_time:.1f},{packet_count},{state},"
        f"{altitude:.2f},{temperature:.2f},{pressure:.2f},"
        f"{battery_voltage:.2f},{latitude:.7f},{longitude:.7f},"
        f"{accel_x:.2f},{accel_y:.2f},{accel_z:.2f},{satellites}"
    )


def main():
    start_time = time.monotonic()
    packet_count = 0

    print("=== PICKLEBRICK GROUND STATION ===")
    print("SIMULATION MODE: These readings are fake.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            elapsed_time = time.monotonic() - start_time
            packet_count += 1

            packet = generate_mock_packet(
                elapsed_time,
                packet_count
            )

            try:
                data = parse_packet(packet)
                save_telemetry(data)

                print(
                    f"Packet {data['packet_count']:04d} | "
                    f"{data['state']:<7} | "
                    f"Altitude: {data['altitude']:7.2f} m | "
                    f"Temp: {data['temperature']:5.2f} C | "
                    f"Battery: {data['battery_voltage']:.2f} V"
                )

            except (ValueError, KeyError) as error:
                print(f"Telemetry error: {error}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nSimulation stopped.")


if __name__ == "__main__":
    main()