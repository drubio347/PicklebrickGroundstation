import sys
import time
import math
import random

import pyqtgraph as pg

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QPushButton,
)


class GroundStation(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Picklebrick Ground Station")
        self.resize(1400, 800)

        # ==========================================
        # SIMULATION DATA
        # ==========================================

        self.start_time = time.monotonic()
        self.packet_count = 0
        self.previous_altitude = None
        self.previous_mission_time = 0.0

        self.times = []
        self.altitudes = []
        self.batteries = []
        self.temperatures = []
        self.velocities = []

        self.show_all_data = False

        # ==========================================
        # APPLICATION STYLE
        # ==========================================

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #edf2e8;
                color: #202820;
                font-family: Arial;
                font-size: 13px;
            }

            QGroupBox {
                background-color: white;
                border: 1px solid #a4b39a;
                border-radius: 5px;
                margin-top: 12px;
                padding: 10px;
                font-weight: bold;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }

            QPushButton {
                background-color: #78956a;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #5f7e52;
            }
        """)

        # ==========================================
        # MAIN WINDOW LAYOUT
        # ==========================================

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        # ==========================================
        # HEADER
        # ==========================================

        header = QHBoxLayout()

        title = QLabel("PICKLEBRICK | TEAM 8")
        title.setStyleSheet(
            "font-size: 25px; font-weight: bold; color: #426b31;"
        )

        self.demo_label = QLabel("SIMULATION MODE")
        self.demo_label.setStyleSheet(
            "background-color: #fff0c2; "
            "color: #805900; "
            "padding: 7px; "
            "font-weight: bold;"
        )

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.demo_label)

        main_layout.addLayout(header)

        # ==========================================
        # THREE MAIN COLUMNS
        # ==========================================

        columns = QHBoxLayout()
        columns.setSpacing(12)

        main_layout.addLayout(columns)

        left = QVBoxLayout()
        middle = QVBoxLayout()
        right = QVBoxLayout()

        columns.addLayout(left, 11)
        columns.addLayout(middle, 10)
        columns.addLayout(right, 10)

        # ==========================================
        # LEFT COLUMN: FLIGHT STATUS
        # ==========================================

        flight_box = QGroupBox("Flight Status")
        flight_layout = QVBoxLayout(flight_box)

        self.state_label = QLabel("Flight State: LAUNCH PAD")
        self.state_label.setStyleSheet(
            "font-size: 17px; font-weight: bold; color: #426b31;"
        )

        flight_layout.addWidget(self.state_label)

        self.phase_label = QLabel(
            "Launch Pad  →  Ascent  →  Apogee  →  Descent  →  Landed"
        )
        self.phase_label.setWordWrap(True)

        flight_layout.addWidget(self.phase_label)

        left.addWidget(flight_box)

        # ==========================================
        # LIVE TELEMETRY
        # ==========================================

        telemetry_box = QGroupBox("Live Telemetry")
        telemetry_layout = QVBoxLayout(telemetry_box)

        self.altitude_label = QLabel("Altitude: -- m")
        self.temp_label = QLabel("Temperature: -- °C")
        self.battery_label = QLabel("Battery: -- V")
        self.panel_label = QLabel("Panel Voltage: Not instrumented")
        self.time_label = QLabel("Elapsed Time: 00:00")
        self.velocity_label = QLabel("Vertical Velocity: -- m/s")

        for label in (
            self.altitude_label,
            self.temp_label,
            self.battery_label,
            self.panel_label,
            self.time_label,
            self.velocity_label,
        ):
            label.setStyleSheet("font-size: 15px; padding: 6px;")
            telemetry_layout.addWidget(label)

        left.addWidget(telemetry_box)

        # ==========================================
        # CONTROLS
        # ==========================================

        controls_box = QGroupBox("Controls")
        controls_layout = QVBoxLayout(controls_box)

        solar_button = QPushButton("Deploy Solar Panels")
        cansat_button = QPushButton("Deploy CanSat")
        clear_button = QPushButton("Clear Graph Data")

        self.swap_graphs_button = QPushButton("Show All Graph Data")

        solar_button.clicked.connect(
            lambda: self.show_demo_notice("Solar deployment")
        )

        cansat_button.clicked.connect(
            lambda: self.show_demo_notice("CanSat deployment")
        )

        clear_button.clicked.connect(self.clear_data)

        self.swap_graphs_button.clicked.connect(self.swap_graphs)

        for button in (
            solar_button,
            cansat_button,
            clear_button,
            self.swap_graphs_button,
        ):
            controls_layout.addWidget(button)

        left.addWidget(controls_box)
        left.addStretch()

        # ==========================================
        # MIDDLE COLUMN: GRAPHS
        # ==========================================

        self.battery_plot = self.make_plot(
            "Battery Voltage",
            "Voltage (V)",
        )

        self.altitude_plot = self.make_plot(
            "Altitude Over Time",
            "Altitude (m)",
        )

        self.velocity_plot = self.make_plot(
            "Velocity Over Time",
            "Velocity (m/s)",
        )

        middle.addWidget(self.battery_plot["box"])
        middle.addWidget(self.altitude_plot["box"])
        middle.addWidget(self.velocity_plot["box"])

        # ==========================================
        # RIGHT COLUMN: TEMPERATURE AND GPS
        # ==========================================

        self.temp_plot = self.make_plot(
            "Temperature Over Time",
            "Temperature (°C)",
        )

        right.addWidget(self.temp_plot["box"])

        gps_box = QGroupBox("GPS / Payload Location")
        gps_layout = QVBoxLayout(gps_box)

        self.gps_label = QLabel(
            "SIMULATED GPS DATA\n\n"
            "Latitude: --\n"
            "Longitude: --\n"
            "Satellites: --"
        )

        self.gps_label.setWordWrap(True)
        self.gps_label.setMinimumHeight(180)

        gps_layout.addWidget(self.gps_label)
        right.addWidget(gps_box)

        # ==========================================
        # STATUS BAR
        # ==========================================

        self.statusBar().showMessage(
            "Simulation active | Waiting for receiver integration"
        )

        # ==========================================
        # SIMULATION TIMER
        # ==========================================

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_telemetry)
        self.timer.start(1000)

    # ==============================================
    # CREATE A GRAPH
    # ==============================================

    def make_plot(self, title, y_label):
        """Create a graph panel."""

        box = QGroupBox(title)
        layout = QVBoxLayout(box)

        plot = pg.PlotWidget()
        plot.setBackground("w")

        plot.showGrid(x=True, y=True, alpha=0.25)

        plot.setLabel("bottom", "Time", units="s")
        plot.setLabel("left", y_label)

        plot.setMinimumHeight(160)

        curve = plot.plot(
            [],
            [],
            pen=pg.mkPen("#4778ff", width=2),
        )

        layout.addWidget(plot)

        return {
            "box": box,
            "plot": plot,
            "curve": curve,
        }

    # ==============================================
    # GENERATE SIMULATED TELEMETRY
    # ==============================================

    def generate_mock_data(self, mission_time):
        """Generate example telemetry for GUI testing."""

        # Simulate ascent followed by descent.
        if mission_time < 30:
            altitude = 10 + (mission_time * 8)
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

        # Example values only, not actual hardware measurements.
        temperature = 23 + 2 * math.sin(mission_time / 10)

        battery = max(
            3.0,
            4.2 - mission_time * 0.001,
        )

        latitude = 34.7254
        longitude = -86.6473
        satellites = 8

        return {
            "state": state,
            "altitude": altitude,
            "temperature": temperature,
            "battery_voltage": battery,
            "latitude": latitude,
            "longitude": longitude,
            "satellites": satellites,
        }

    # ==============================================
    # UPDATE TELEMETRY
    # ==============================================

    def update_telemetry(self):
        """Generate and display one simulated telemetry reading."""

        mission_time = time.monotonic() - self.start_time
        self.packet_count += 1

        data = self.generate_mock_data(mission_time)

        altitude = data["altitude"]
        temperature = data["temperature"]
        battery = data["battery_voltage"]
        state = data["state"]

        # Estimate vertical velocity from altitude changes.
        if self.previous_altitude is None:
            velocity = 0.0

        else:
            interval = max(
                0.001,
                mission_time - self.previous_mission_time,
            )

            velocity = (
                altitude - self.previous_altitude
            ) / interval

        self.previous_altitude = altitude
        self.previous_mission_time = mission_time

        # Save readings in memory for the graphs.
        self.times.append(mission_time)
        self.altitudes.append(altitude)
        self.batteries.append(battery)
        self.temperatures.append(temperature)
        self.velocities.append(velocity)

        # Update flight status.
        self.state_label.setText(
            f"Flight State: {state}"
        )

        # Update telemetry labels.
        self.altitude_label.setText(
            f"Altitude: {altitude:.1f} m"
        )

        self.temp_label.setText(
            f"Temperature: {temperature:.1f} °C"
        )

        self.battery_label.setText(
            f"Battery: {battery:.2f} V"
        )

        self.panel_label.setText(
            "Panel Voltage: Not instrumented"
        )

        minutes = int(mission_time // 60)
        seconds = int(mission_time % 60)

        self.time_label.setText(
            f"Elapsed Time: {minutes:02d}:{seconds:02d}"
        )

        self.velocity_label.setText(
            f"Vertical Velocity: {velocity:.1f} m/s"
        )

        # Update GPS display.
        self.gps_label.setText(
            "SIMULATED GPS DATA\n\n"
            f"Latitude: {data['latitude']:.7f}\n"
            f"Longitude: {data['longitude']:.7f}\n"
            f"Satellites: {data['satellites']}"
        )

        # Refresh all graphs.
        self.refresh_graphs()

    # ==============================================
    # REFRESH GRAPHS
    # ==============================================

    def refresh_graphs(self):
        """Refresh graphs using recent or all readings."""

        if self.show_all_data:
            display_times = self.times
            start_index = 0

        else:
            display_times = self.times[-60:]
            start_index = len(self.times) - len(display_times)

        datasets = (
            (self.battery_plot, self.batteries),
            (self.altitude_plot, self.altitudes),
            (self.velocity_plot, self.velocities),
            (self.temp_plot, self.temperatures),
        )

        for graph, values in datasets:
            graph["curve"].setData(
                display_times,
                values[start_index:],
            )

        self.swap_graphs_button.setText(
            "Show Recent 60 Readings"
            if self.show_all_data
            else "Show All Graph Data"
        )

    # ==============================================
    # CLEAR GRAPH DATA
    # ==============================================

    def clear_data(self):
        """Clear graph history and restart the simulation clock."""

        self.start_time = time.monotonic()
        self.packet_count = 0
        self.previous_altitude = None
        self.previous_mission_time = 0.0

        self.times.clear()
        self.altitudes.clear()
        self.batteries.clear()
        self.temperatures.clear()
        self.velocities.clear()

        self.show_all_data = False

        self.state_label.setText(
            "Flight State: LAUNCH PAD"
        )

        self.altitude_label.setText("Altitude: -- m")
        self.temp_label.setText("Temperature: -- °C")
        self.battery_label.setText("Battery: -- V")

        self.panel_label.setText(
            "Panel Voltage: Not instrumented"
        )

        self.time_label.setText("Elapsed Time: 00:00")

        self.velocity_label.setText(
            "Vertical Velocity: -- m/s"
        )

        self.gps_label.setText(
            "SIMULATED GPS DATA\n\n"
            "Latitude: --\n"
            "Longitude: --\n"
            "Satellites: --"
        )

        self.refresh_graphs()

        self.statusBar().showMessage(
            "Graph data cleared. Simulation will continue.",
            4000,
        )

    # ==============================================
    # TOGGLE GRAPH HISTORY
    # ==============================================

    def swap_graphs(self):
        """Toggle between recent and all recorded readings."""

        self.show_all_data = not self.show_all_data

        self.refresh_graphs()

        mode = (
            "all recorded readings"
            if self.show_all_data
            else "the most recent 60 readings"
        )

        self.statusBar().showMessage(
            f"Displaying {mode}.",
            4000,
        )

    # ==============================================
    # DEMO BUTTON MESSAGES
    # ==============================================

    def show_demo_notice(self, command):
        """Prevent demo buttons from sending hardware commands."""

        self.statusBar().showMessage(
            f"{command}: DEMO ONLY. No hardware command sent.",
            5000,
        )


# ==============================================
# START APPLICATION
# ==============================================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = GroundStation()
    window.show()

    sys.exit(app.exec())