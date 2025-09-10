"""
Hash utility functions for count-min sketch operations.

This module provides Python equivalents to the C++ HashUtil class,
maintaining the same input/output behavior and performance characteristics.
"""

import struct


class PyHashUtil:
    """
    Hash utility class providing byte hashing and hash combination functionality.

    This class provides static methods that mirror the C++ HashUtil implementation,
    ensuring consistent hash behavior across C++ and Python implementations.
    """

    # Prime factor constant matching C++ implementation
    PRIME_FACTOR: int = 10000019

    @staticmethod
    def hash_bytes(data: bytes | bytearray) -> int:
        """
        Hash a sequence of bytes using the same algorithm as C++ HashUtil::HashBytes.

        This implementation follows the algorithm from:
        https://github.com/greenplum-db/gpos/blob/b53c1acd6285de94044ff91fbee91589543feba1/libgpos/src/utils.cpp#L126

        Args:
            data: The bytes to hash

        Returns:
            The computed hash value as an integer
        """
        if not data:
            return 0

        # Convert to bytes if needed
        if isinstance(data, bytearray):
            data = bytes(data)

        length = len(data)
        hash_value = length

        for byte_val in data:
            # Convert to signed 8-bit integer (matching C++ static_cast<int8_t>)
            signed_byte = struct.unpack("b", bytes([byte_val]))[0]

            # Apply the same bit operations as C++: ((hash << 5) ^ (hash >> 27)) ^ byte
            hash_value = ((hash_value << 5) ^ (hash_value >> 27)) ^ signed_byte

            # Ensure we stay within 64-bit range (Python ints are arbitrary precision)
            hash_value &= 0xFFFFFFFFFFFFFFFF

        return hash_value

    @staticmethod
    def combine_hashes(left: int, right: int) -> int:
        """
        Combine two hash values using the same algorithm as C++ HashUtil::CombineHashes.

        This method creates a combined hash by treating the two input hashes as
        a sequence of bytes and hashing them together.

        Args:
            left: The first hash value
            right: The second hash value

        Returns:
            The combined hash value as an integer
        """
        # Pack both hashes as 8-byte little-endian values (matching C++ sizeof(hash_t) * 2)
        # Using 'Q' format for unsigned long long (8 bytes)
        packed_data = struct.pack("<QQ", left, right)

        # Hash the packed data
        return PyHashUtil.hash_bytes(packed_data)
