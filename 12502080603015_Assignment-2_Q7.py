import json
import math

def read_records(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            yield line

def parse_records(lines):
    for line in lines:
        try:
            record = json.loads(line)

            device = record.get("device_id")
            temperature = float(record.get("temperature_c"))
            humidity = float(record.get("humidity"))

            if (
                not isinstance(device, str)
                or not device.strip()
                or not math.isfinite(temperature)
                or not math.isfinite(humidity)
                or not 0 <= humidity <= 100
            ):
                yield None
                continue

            yield {
                "device_id": device,
                "temperature_c": temperature,
                "humidity": humidity
            }

        except (json.JSONDecodeError, TypeError, ValueError):
            yield None

def transform_records(records):
    for record in records:
        if record is not None:
            record["temperature_f"] = (
                record["temperature_c"] * 9 / 5 + 32
            )
            yield record

def aggregate_records(records):
    statistics = {}
    corrupted = 0

    for record in records:
        if record is None:
            corrupted += 1
            continue

        device = record["device_id"]
        temperature = record["temperature_c"]

        if device not in statistics:
            statistics[device] = {
                "count": 0,
                "min": temperature,
                "max": temperature,
                "total": 0.0,
                "corrupted": 0
            }

        stats = statistics[device]
        stats["count"] += 1
        stats["min"] = min(stats["min"], temperature)
        stats["max"] = max(stats["max"], temperature)
        stats["total"] += temperature

    return statistics, corrupted

print("=== Generator-Based JSON ETL Pipeline ===")

file_path = input("Enter JSONL file path: ").strip()

try:
    lines = read_records(file_path)
    parsed_records = parse_records(lines)
    transformed_records = transform_records(parsed_records)
    statistics, corrupted = aggregate_records(transformed_records)

    print("\nDevice Summary:")

    for device in sorted(statistics):
        stats = statistics[device]
        average = stats["total"] / stats["count"]

        print(
            f"{device} count={stats['count']} "
            f"min={stats['min']:g} "
            f"max={stats['max']:g} "
            f"avg={average:.2f} "
            f"corrupted={corrupted}"
        )

    if not statistics:
        print("No valid records found.")

except OSError as e:
    print("ERROR:", e)