import math

def generate_mock_packet(elapsed_time, packet_count):
"""Generate a simulated 14-field CanSat telemetry packet."""

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

latitude = 34.7304 + 0.00001 * math.sin(elapsed_time / 5)
longitude = -86.5861 + 0.00001 * math.cos(elapsed_time / 5)

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