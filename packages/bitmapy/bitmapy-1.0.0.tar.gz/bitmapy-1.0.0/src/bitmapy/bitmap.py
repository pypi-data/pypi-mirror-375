"""Bitmap manipulation and operations."""

from enum import IntFlag
from typing import get_args


class Bitmap[T: IntFlag]:
    """Represents a bitmap value."""

    def __init__(self, value: int = 0) -> None:
        """
        Initialise the bitmap with an integer value.

        Keyword Arguments:
            value -- The initial value of the bitmap (default: {0}).
        """
        self.value = value

    @property
    def _enum_type(self) -> T:
        """Return the IntFlag type used for the bitmap."""
        orig_class = getattr(self, "__orig_class__", None)
        if orig_class is None:
            msg = "Generic type T must be specified."
            raise TypeError(msg)
        return get_args(orig_class)[0]

    def set(self, flag: T) -> None:
        """
        Set a specific bit in the bitmap.

        Arguments:
            flag -- The bit to set.
        """
        self.value |= flag

    def clear(self, flag: T) -> None:
        """
        Clear a specific bit in the bitmap.

        Arguments:
            flag -- The bit to clear.
        """
        self.value &= ~flag

    def toggle(self, flag: T) -> None:
        """
        Toggle a specific bit in the bitmap.

        Arguments:
            flag -- The bit to toggle.
        """
        self.value ^= flag

    def is_set(self, flag: T) -> bool:
        """
        Check if a specific bit is set in the bitmap.

        Arguments:
            flag -- The bit to check.

        Returns:
            True if the bit is set, False otherwise.
        """
        return (self.value & flag) == flag

    def reset(self) -> None:
        """Reset the bitmap value to zero."""
        self.value = 0

    @property
    def flags(self) -> list[str]:
        """Return a list of all set flags in the bitmap."""
        return [bit.name for bit in self._enum_type if bit.name and self.is_set(bit)]

    def __len__(self) -> int:
        """Return the number of flags in the bitmap."""
        return len(self._enum_type)

    def __str__(self) -> str:
        """Return the string representation of the bitmap value in binary format."""
        return f"0b{self.value:0{len(self)}b}"

    def __eq__(self, value: object) -> bool:
        """Check equality with another Bitmap or integer value."""
        if isinstance(value, Bitmap):
            return self.value == value.value
        if isinstance(value, int):
            return self.value == value
        return NotImplemented

    def __hash__(self) -> int:
        """
        Prevent hashing of Bitmap objects.

        Raises:
            TypeError: If an attempt is made to hash a Bitmap object.
        """
        msg = "Bitmap objects are mutable and cannot be hashed."
        raise TypeError(msg)
