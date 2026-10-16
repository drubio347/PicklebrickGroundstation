from packet_parser import parse_packet
from data_logger import save_telemetry

def main():
    # Simulate a packet from the CanSat
    fake_packet = "Pickle Brick,12.5,1,DESCENT,150.2,23.4,4.1"

    # Convert the packet into structured data
    data = parse_packet(fake_packet)
    save_telemetry(data)
    print("Telemetry saved to CSV!")

    # Display the parsed information
    print("=== PICKLEBRICK GROUND STATION ===")
    print(f"Team: {data['team_id']}")
    print(f"Mission time: {data['mission_time']} seconds")
    print(f"Packet count: {data['packet_count']}")
    print(f"Flight state: {data['state']}")
    print(f"Altitude: {data['altitude']} m")
    print(f"Temperature: {data['temperature']} °C")
    print(f"Battery: {data['battery_voltage']} V")


if __name__ == "__main__":
    main()