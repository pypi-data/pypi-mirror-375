#!/usr/bin/env python3
"""Simple benchmark runner."""

import subprocess
import sys


def main():
    """Run benchmarks."""
    cmd = ["pytest", "test_benchmarks.py", "--benchmark-only", "--benchmark-sort=mean"]

    if len(sys.argv) > 1:
        if sys.argv[1] == "--json":
            cmd.extend(["--benchmark-json=results.json"])
        elif sys.argv[1] == "--help":
            print("Usage: python run.py [--json] [--help]")
            print("  --json    Save results to results.json")
            return

    subprocess.run(cmd)


if __name__ == "__main__":
    main()
