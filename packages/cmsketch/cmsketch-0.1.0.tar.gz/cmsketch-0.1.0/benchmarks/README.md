# Simple Count-Min Sketch Benchmarks

Benchmarks using realistic IP data: 10 unique IPs with 100k weighted samples.

## Setup

First generate the test data:
```bash
cd benchmarks
python generate_data.py
```

## Usage

```bash
pytest test_benchmarks.py --benchmark-only
```

## What it tests

- **Insert**: Stream all 100k IP samples
- **Count**: Query counts for the 10 unique IPs  
- **Top-K**: Find top 3 IPs from the 10 unique ones
- **Streaming**: Complete workflow (insert + top-k)

Results show C++ vs Python performance with realistic data distribution.
