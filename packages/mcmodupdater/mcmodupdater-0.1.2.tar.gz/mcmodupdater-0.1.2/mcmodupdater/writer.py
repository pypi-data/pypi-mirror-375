# -*- coding: utf-8 -*-
"""
"""

from typing import Union


class Writer:

    def __init__(
        self,
        filename: str,
        mode: str = "wb",
    ) -> None:
        """
        """
        self.filename = filename
        self.mode = mode
        self.file = bytes()

    def open(self) -> None:
        """
        """
        self.file = open(self.filename, self.mode)

    def write(
        self,
        data: bytes
    ) -> None:
        """
        """
        self.file.write(data)

    def __enter__(self) -> None:
        """
        """
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        """
        self.file.close()
        self.filename = None
        self.file = None
