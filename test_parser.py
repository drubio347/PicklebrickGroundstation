from packet_parser import parse_packet

mock_packet = (
    "TEAM8,12.5,15,ASCENT,150.2,23.4,"
    "1008.2,4.1,34.5000000,-86.6000000,"
    "3.2,0.4,9.7,8"
)

data = parse_packet(mock_packet)

print("=== PARSER TEST ===")
print(f"Team: {data['team_id']}")
print(f"Mission time: {data['mission_time']} s")
print(f"Flight state: {data['state']}")
print(f"Altitude: {data['altitude']} m")
print(f"Temperature: {data['temperature']} C")
print(f"Pressure: {data['pressure']} hPa")
print(f"Latitude: {data['latitude']}")
print(f"Longitude: {data['longitude']}")
print(f"Satellites: {data['satellites']}")
print("Parser test passed!")