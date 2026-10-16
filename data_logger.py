import csv
import os

def save_telemetry(data, filename="telemetry.csv"):
    # Check whether the CSV file already exists
    file_exists = os.path.exists(filename)

    # Check whether we need to write column headings
    needs_header = not file_exists or os.path.getsize(filename) == 0

    # Open the file in append mode so existing data is preserved
    with open(filename, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        # Write column names for a new or empty file
        if needs_header:
            writer.writeheader()
        # Save the new telemetry reading
        writer.writerow(data)
