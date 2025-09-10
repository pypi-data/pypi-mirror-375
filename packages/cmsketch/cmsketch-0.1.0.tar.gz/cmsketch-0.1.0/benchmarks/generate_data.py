#!/usr/bin/env python3
"""Generate benchmark data using the exact approach from your snippet."""

import random
from faker import Faker
from pathlib import Path


def generate_benchmark_data():
    """Generate IP data exactly like your snippet."""
    fake = Faker()

    # Infer data directory path (relative to project root)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / "data"

    # Create data directory
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"Using data directory: {data_dir}")

    # Generate 10 unique IPs
    num_unique_ips = 10
    unique_ips = [fake.ipv4() for _ in range(num_unique_ips)]

    print(f"Generated {len(unique_ips)} unique IPs:")
    for i, ip in enumerate(unique_ips):
        print(f"  {i+1}: {ip}")

    # Save unique IPs
    with open(data_dir / "unique-ips.txt", "w") as f:
        for ip in unique_ips:
            f.write(ip + "\n")

    # Generate 100k samples with weighted distribution
    num_samples = 100_000

    ips = random.choices(
        unique_ips,
        weights=[
            10,  # Most frequent
            8,
            6,
            4,
            2,
            *[1] * 5,  # Least frequent (5 IPs with weight 1 each)
        ],
        k=num_samples,
    )

    # Save all IP samples
    with open(data_dir / "ips.txt", "w") as f:
        for ip in ips:
            f.write(ip + "\n")

    print(f"\nGenerated {len(ips)} IP samples with weighted distribution")

    # Show distribution
    print("\nDistribution of generated IPs:")
    for ip in unique_ips:
        count = ips.count(ip)
        percentage = (count / len(ips)) * 100
        print(f"  {ip}: {count:,} times ({percentage:.1f}%)")

    print("\nData saved to:")
    print(f"  - {data_dir / 'unique-ips.txt'} ({len(unique_ips)} unique IPs)")
    print(f"  - {data_dir / 'ips.txt'} ({len(ips):,} samples)")


if __name__ == "__main__":
    generate_benchmark_data()
