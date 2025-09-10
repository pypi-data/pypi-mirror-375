"""Simple benchmarks for Count-Min Sketch implementations using real IP data."""

import pytest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, wait
from cmsketch import CountMinSketchStr, PyCountMinSketchStr


# Infer data directory path (relative to project root)
benchmark_dir = Path(__file__).parent
project_root = benchmark_dir.parent
data_dir = project_root / "data"

ips_file_path = data_dir / "ips.txt"
unique_ips_file_path = data_dir / "unique-ips.txt"


# Check if data exists, create if not
def ensure_data_exists():
    """Ensure benchmark data exists, generate if missing."""
    if not data_dir.exists():
        print(f"Creating data directory: {data_dir}")
        data_dir.mkdir(parents=True, exist_ok=True)

    if not ips_file_path.exists() or not unique_ips_file_path.exists():
        print("Benchmark data not found. Generating...")
        print(f"Data will be saved to: {data_dir}")

        # Generate data using the same approach as your snippet
        import random
        from faker import Faker

        fake = Faker()

        # Generate 10 unique IPs
        num_unique_ips = 10
        unique_ips_generated = [fake.ipv4() for _ in range(num_unique_ips)]

        # Save unique IPs
        with open(unique_ips_file_path, "w") as f:
            for ip in unique_ips_generated:
                f.write(ip + "\n")

        # Generate 100k samples with weighted distribution
        num_samples = 100_000
        ips_generated = random.choices(
            unique_ips_generated,
            weights=[10, 8, 6, 4, 2, *[1] * 5],
            k=num_samples,
        )

        # Save all IP samples
        with open(ips_file_path, "w") as f:
            for ip in ips_generated:
                f.write(ip + "\n")

        print(
            f"Generated {len(unique_ips_generated)} unique IPs and {len(ips_generated):,} samples"
        )


# Ensure data exists before loading
ensure_data_exists()

# Get the 10 unique IPs
unique_ips = []
if unique_ips_file_path.exists():
    with open(unique_ips_file_path, "r") as f:
        for line in f:
            ip = line.strip()
            if ip:
                unique_ips.append(ip)

# Get all 100k IP samples (from the 10 unique IPs)
all_ips = []
if ips_file_path.exists():
    with open(ips_file_path, "r") as f:
        for line in f:
            ip = line.strip()
            if ip:
                all_ips.append(ip)

# Sketch config from your snippet
width = 1_000
depth = 10
batch_size = 1_000

print(f"Loaded {len(unique_ips)} unique IPs and {len(all_ips)} total IP samples")


# Helper functions from your snippet
def insert_ips(ips, count_min_sketch):
    """Insert IPs into sketch (for threading)."""
    for ip in ips:
        count_min_sketch.insert(ip)


def ip_batch_generator(batch_size):
    """Generate IP batches from the loaded data."""
    for i in range(0, len(all_ips), batch_size):
        yield all_ips[i : i + batch_size]


def process_with_threading(count_min_sketch):
    """Process IPs with threading (exactly like your snippet)."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []

        for ip_batch in ip_batch_generator(batch_size):
            future = executor.submit(insert_ips, ip_batch, count_min_sketch)
            futures.append(future)

        wait(futures)


class TestInsertBenchmarks:
    """Benchmark insert operations."""

    @pytest.mark.benchmark(group="insert")
    def test_cpp_insert_100k_ips_threaded(self, benchmark):
        """Benchmark C++ insert with 100k IP samples using threading (like your snippet)."""
        if not all_ips:
            pytest.skip("No IP data available")

        def insert_all_ips_threaded():
            count_min_sketch = CountMinSketchStr(width=width, depth=depth)
            process_with_threading(count_min_sketch)
            return count_min_sketch

        result = benchmark(insert_all_ips_threaded)
        assert result.get_width() == width

    @pytest.mark.benchmark(group="insert")
    def test_py_insert_100k_ips_threaded(self, benchmark):
        """Benchmark Python insert with 100k IP samples using threading (like your snippet)."""
        if not all_ips:
            pytest.skip("No IP data available")

        def insert_all_ips_threaded():
            py_count_min_sketch = PyCountMinSketchStr(width=width, depth=depth)
            process_with_threading(py_count_min_sketch)
            return py_count_min_sketch

        result = benchmark(insert_all_ips_threaded)
        assert result.get_width() == width


class TestCountBenchmarks:
    """Benchmark count operations."""

    @pytest.mark.benchmark(group="count")
    def test_cpp_count_unique_ips(self, benchmark):
        """Benchmark C++ count for the 10 unique IPs."""
        if not all_ips or not unique_ips:
            pytest.skip("No IP data available")

        # Pre-populate with all 100k samples
        count_min_sketch = CountMinSketchStr(width=width, depth=depth)
        for ip in all_ips:
            count_min_sketch.insert(ip)

        def count_all_unique():
            total = 0
            for ip in unique_ips:  # Count all 10 unique IPs
                total += count_min_sketch.count(ip)
            return total

        result = benchmark(count_all_unique)
        assert result > 0  # Should have counts for all unique IPs

    @pytest.mark.benchmark(group="count")
    def test_py_count_unique_ips(self, benchmark):
        """Benchmark Python count for the 10 unique IPs."""
        if not all_ips or not unique_ips:
            pytest.skip("No IP data available")

        # Pre-populate with all 100k samples
        py_count_min_sketch = PyCountMinSketchStr(width=width, depth=depth)
        for ip in all_ips:
            py_count_min_sketch.insert(ip)

        def count_all_unique():
            total = 0
            for ip in unique_ips:  # Count all 10 unique IPs
                total += py_count_min_sketch.count(ip)
            return total

        result = benchmark(count_all_unique)
        assert result > 0  # Should have counts for all unique IPs


class TestTopKBenchmarks:
    """Benchmark top-k operations."""

    @pytest.mark.benchmark(group="topk")
    def test_cpp_topk_from_unique_ips(self, benchmark):
        """Benchmark C++ top-k with the 10 unique IPs as candidates."""
        if not all_ips or not unique_ips:
            pytest.skip("No IP data available")

        # Pre-populate with all 100k samples
        count_min_sketch = CountMinSketchStr(width=width, depth=depth)
        for ip in all_ips:
            count_min_sketch.insert(ip)

        def topk_query():
            # Get top 3 IPs from the 10 unique IPs (exactly like your snippet)
            return count_min_sketch.top_k(3, unique_ips)

        result = benchmark(topk_query)
        assert len(result) <= 3
        assert len(result) > 0  # Should find some top IPs

    @pytest.mark.benchmark(group="topk")
    def test_py_topk_from_unique_ips(self, benchmark):
        """Benchmark Python top-k with the 10 unique IPs as candidates."""
        if not all_ips or not unique_ips:
            pytest.skip("No IP data available")

        # Pre-populate with all 100k samples
        py_count_min_sketch = PyCountMinSketchStr(width=width, depth=depth)
        for ip in all_ips:
            py_count_min_sketch.insert(ip)

        def topk_query():
            # Get top 3 IPs from the 10 unique IPs (exactly like your snippet)
            return py_count_min_sketch.top_k(3, unique_ips)

        result = benchmark(topk_query)
        assert len(result) <= 3
        assert len(result) > 0  # Should find some top IPs


class TestStreamingBenchmarks:
    """Benchmark streaming scenarios like your snippet."""

    @pytest.mark.benchmark(group="streaming")
    def test_cpp_streaming_insert_and_topk(self, benchmark):
        """Benchmark C++ streaming: insert all 100k IPs then get top-3."""
        if not all_ips or not unique_ips:
            pytest.skip("No IP data available")

        def streaming_workflow():
            count_min_sketch = CountMinSketchStr(width=width, depth=depth)

            # Stream all IPs with threading (like your snippet)
            process_with_threading(count_min_sketch)

            # Get top 3 IPs (like your snippet)
            top_ips = count_min_sketch.top_k(3, unique_ips)

            return count_min_sketch, top_ips

        result = benchmark(streaming_workflow)
        assert result[0].get_width() == width
        assert len(result[1]) <= 3

    @pytest.mark.benchmark(group="streaming")
    def test_py_streaming_insert_and_topk(self, benchmark):
        """Benchmark Python streaming: insert all 100k IPs then get top-3."""
        if not all_ips or not unique_ips:
            pytest.skip("No IP data available")

        def streaming_workflow():
            py_count_min_sketch = PyCountMinSketchStr(width=width, depth=depth)

            # Stream all IPs with threading (like your snippet)
            process_with_threading(py_count_min_sketch)

            # Get top 3 IPs (like your snippet)
            top_ips = py_count_min_sketch.top_k(3, unique_ips)

            return py_count_min_sketch, top_ips

        result = benchmark(streaming_workflow)
        assert result[0].get_width() == width
        assert len(result[1]) <= 3
