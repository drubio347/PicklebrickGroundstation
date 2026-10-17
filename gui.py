
import sys
import math

# pyqtgraph is required at runtime; the IDE may still flag it before the
# dependency is installed in the current environment.
import pyqtgraph as pg  # type: ignore[import-not-found]
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QGroupBox,
)


class GroundStation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Picklebrick Ground Station")
        self.resize(1400, 800)

        # Demo data only. No ESP32 is connected yet.
        self.show_all_data = False
        self.elapsed = 0
        self.times = []
        self.altitudes = []
        self.batteries = []
        self.temperatures = []
        self.velocities = []

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

        # Main window layout
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        # Header
        header = QHBoxLayout()

        title = QLabel("PICKLEBRICK | TEAM 8")
        title.setStyleSheet(
            "font-size: 25px; font-weight: bold; color: #426b31;"
        )

        self.demo_label = QLabel("SIMULATION MODE")
        self.demo_label.setStyleSheet(
            "background-color: #fff0c2; color: #805900;"
            "padding: 7px; font-weight: bold;"
        )

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.demo_label)
        main_layout.addLayout(header)

        # Three main columns
        columns = QHBoxLayout()
        columns.setSpacing(12)
        main_layout.addLayout(columns)

        left = QVBoxLayout()
        middle = QVBoxLayout()
        right = QVBoxLayout()

        columns.addLayout(left, 11)
        columns.addLayout(middle, 10)
        columns.addLayout(right, 10)

        # LEFT COLUMN: Flight status and telemetry
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

        telemetry_box = QGroupBox("Live Telemetry")
        telemetry_layout = QVBoxLayout(telemetry_box)

        self.altitude_label = QLabel("Altitude: -- m")
        self.temp_label = QLabel("Temperature: -- °C")
        self.battery_label = QLabel("Battery: -- V")
        self.panel_label = QLabel("Panel Voltage: -- mV")
        self.time_label = QLabel("Elapsed Time: 00:00")
        self.velocity_label = QLabel("Velocity: -- m/s")

        for label in [
            self.altitude_label,
            self.temp_label,
            self.battery_label,
            self.panel_label,
            self.time_label,
            self.velocity_label,
        ]:
            label.setStyleSheet("font-size: 15px; padding: 6px;")
            telemetry_layout.addWidget(label)

        left.addWidget(telemetry_box)

        controls_box = QGroupBox("Controls")
        controls_layout = QVBoxLayout(controls_box)

        solar_button = QPushButton("Deploy Solar Panels")
        cansat_button = QPushButton("Deploy CanSat")
        clear_button = QPushButton("Clear Graph Data")
        swap_graphs_button = QPushButton("Swap Graph Zoom")

        solar_button.clicked.connect(
            lambda: self.show_demo_notice("Solar deployment")
        )
        cansat_button.clicked.connect(
            lambda: self.show_demo_notice("CanSat deployment")
        )
        clear_button.clicked.connect(self.clear_data)
        swap_graphs_button.clicked.connect(self.swap_graphs)

        controls_layout.addWidget(solar_button)
        controls_layout.addWidget(cansat_button)
        controls_layout.addWidget(clear_button)
        controls_layout.addWidget(swap_graphs_button)
        

        left.addWidget(controls_box)
        left.addStretch()

        # MIDDLE COLUMN: Battery, altitude and velocity plots
        self.battery_plot = self.make_plot(
            "Battery Voltage", "Voltage (V)"
        )
        self.altitude_plot = self.make_plot(
            "Altitude Over Time", "Altitude (m)"
        )
        self.velocity_plot = self.make_plot(
            "Velocity Over Time", "Velocity (m/s)"
        )

        middle.addWidget(self.battery_plot["box"])
        middle.addWidget(self.altitude_plot["box"])
        middle.addWidget(self.velocity_plot["box"])

        # RIGHT COLUMN: Temperature and GPS placeholder
        self.temp_plot = self.make_plot(
            "Temperature Over Time", "Temperature (°C)"
        )
        right.addWidget(self.temp_plot["box"])

        gps_box = QGroupBox("GPS / Payload Location")
        gps_layout = QVBoxLayout(gps_box)

        self.gps_label = QLabel(
            "GPS map not connected\n\n"
            "Latitude: --\n"
            "Longitude: --\n\n"
            "Location display will be added when GPS data is available."
        )
        self.gps_label.setAlignment(
            self.gps_label.alignment()
        )
        self.gps_label.setWordWrap(True)
        self.gps_label.setMinimumHeight(180)

        gps_layout.addWidget(self.gps_label)
        right.addWidget(gps_box)

        # Bottom connection/status message
        self.statusBar().showMessage(
            "Simulation active | Waiting for real receiver integration"
        )

        # Update simulated measurements once per second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_demo_data)
        self.timer.start(1000)

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
            pen=pg.mkPen("#4778ff", width=2)
        )

        layout.addWidget(plot)

        return {
            "box": box,
            "plot": plot,
            "curve": curve,
        }

    def update_demo_data(self):
        """Generate test measurements for the GUI."""

        self.elapsed += 1
        t = self.elapsed

        # Simulated ascent followed by descent
        if t <= 25:
            altitude = 20.0 * t
        else:
            altitude = max(0.0, 500.0 - 18.0 * (t - 25))

        # These values are invented for testing the interface.
        battery = max(0.0, 4.1 - 0.001 * t)
        temperature = 23.4 + math.sin(t / 5) * 2
        panel_voltage = 500 + 50 * math.sin(t / 4)

        if t == 1:
            velocity = 0.0
        else:
            velocity = altitude - self.altitudes[-1]

        # Estimate the current flight phase
        if t < 3:
            state = "LAUNCH PAD"
        elif t <= 25:
            state = "ASCENT"
        elif t <= 28:
            state = "APOGEE"
        elif altitude > 0:
            state = "DESCENT"
        else:
            state = "LANDED"

        self.times.append(t)
        self.altitudes.append(altitude)
        self.batteries.append(battery)
        self.temperatures.append(temperature)
        self.velocities.append(velocity)

        # Preserve all readings; choose what to display.    
        if self.show_all_data:
            display_times = self.times
            display_altitudes = self.altitudes
            display_batteries = self.batteries
            display_temperatures = self.temperatures
            display_velocities = self.velocities
        else:
            display_times = self.times[-120:]
            display_altitudes = self.altitudes[-120:]
            display_batteries = self.batteries[-120:]
            display_temperatures = self.temperatures[-120:]
            display_velocities = self.velocities[-120:]

        # Update the telemetry labels
        self.state_label.setText(f"Flight State: {state}")
        self.altitude_label.setText(f"Altitude: {altitude:.1f} m")
        self.temp_label.setText(f"Temperature: {temperature:.1f} °C")
        self.battery_label.setText(f"Battery: {battery:.2f} V")
        self.panel_label.setText(
            f"Panel Voltage: {panel_voltage:.0f} mV"
        )
        self.time_label.setText(
            f"Elapsed Time: {t // 60:02d}:{t % 60:02d}"
        )
        self.velocity_label.setText(f"Velocity: {velocity:.1f} m/s")

        # Update the graphs
        self.battery_plot["curve"].setData(
            display_times, display_batteries
        )
        self.altitude_plot["curve"].setData(
            display_times, display_altitudes
        )
        self.velocity_plot["curve"].setData(
            display_times, display_velocities
        )
        self.temp_plot["curve"].setData(
            display_times, display_temperatures
        )

    def clear_data(self):
        """Clear stored graph readings."""

        self.elapsed = 0
        self.times.clear()
        self.altitudes.clear()
        self.batteries.clear()
        self.temperatures.clear()
        self.velocities.clear()

        for graph in [
            self.battery_plot,
            self.altitude_plot,
            self.velocity_plot,
            self.temp_plot,
        ]:
            graph["curve"].setData([], [])

        self.statusBar().showMessage(
            "Graph data cleared. Simulation will continue.",
            4000
        )

"""
    def swap_graphs(self):
        ""Changes zoom of graphs""
        timesClicked = 0
        Switch = 0
        if swap_graphs_button.clicked = True
            timesClicked += 1
            Switch = timesClicked%2
            if self.show_all_data ""Switch = 0"":
                display_times = self.times
                display_altitudes = self.altitudes
                display_batteries = self.batteries
                display_temperatures = self.temperatures
                display_velocities = self.velocities
            else:
                display_times = self.times[-120:]
                display_altitudes = self.altitudes[-120:]
                display_batteries = self.batteries[-120:]
                display_temperatures = self.temperatures[-120:]
                display_velocities = self.velocities[-120:]
            return  self.times, self.altitudes, self.batteries, self.temperatures, self.velocities
    
    )"""

    def swap_graphs(self):
        """Toggle between recent readings and all readings."""
        self.show_all_data = not self.show_all_data
    
        if self.show_all_data:
            mode = "All readings"
        else:
            mode = "Most recent 120 readings"
    
        self.statusBar().showMessage(
            f"Graph display: {mode}", 4000
        )
    
        # Refresh the graphs immediately.
        for graph, values in [
            (self.battery_plot, self.batteries),
            (self.altitude_plot, self.altitudes),
            (self.velocity_plot, self.velocities),
            (self.temp_plot, self.temperatures),
        ]:
            times = (
                self.times
                if self.show_all_data
                else self.times[-120:]
            )
            displayed_values = (
                values
                if self.show_all_data
                else values[-120:]
            )
            graph["curve"].setData(times, displayed_values)
        
        def show_demo_notice(self, command):
            """Prevent demo buttons from sending real commands."""
    
            self.statusBar().showMessage(
                f"{command}: DEMO ONLY. No hardware command sent.",
                5000
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GroundStation()
    window.show()
    sys.exit(app.exec())
