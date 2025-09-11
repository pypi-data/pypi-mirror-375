# -*- coding: utf-8 -*-
"""
"""

from mmh2 import MurmurHash2

from typing import Union


class MurmurHash2CurseForge(MurmurHash2):

    bytes_to_filter = {0x09, 0x0A, 0x0D, 0x20}

    @staticmethod
    def filter_bytes(
        data: bytes,
    ) -> bytes:
        """
        Filters unnecessary bytes from raw data.

        Args
            data: bytes.

        Returns
            bytes: filtered bytes.
        """
        data = bytearray(
                        b for b in data
                        if b not in MurmurHash2CurseForge.bytes_to_filter
                    )
        return bytes(data)

    @staticmethod
    def to_bytes(
        data: Union[str, bytes]
    ) -> bytes:
        """
        Converts strings to bytes or opens the file in binary mode.

        Args
            data: str, bytes; the data can be a string, a file path, or bytes.

        Returns
            bytes: bytes of content.
        """
        if isinstance(data, str):
            try:
                with open(data, "rb") as file:
                    data = file.read()
            except FileNotFoundError as e:
                data = data.encode("utf-8")
            except Exception as e:
                return b''

        return MurmurHash2CurseForge.filter_bytes(data=data)

    @staticmethod
    def hash32(
        data: Union[str, bytes],
        seed: int = 1,
    ) -> int:
        """
        Calculates the 32-bit murmurhash2 hash from the data.

        Args
            data: str, bytes; the data can be a string, a file path, or bytes.

        Returns
            int: 10-digit hash calculated from the data.
        """
        raw_data = MurmurHash2CurseForge.to_bytes(data=data)
        return MurmurHash2.hash32(
                                data=raw_data,
                                seed=seed,
                            )
