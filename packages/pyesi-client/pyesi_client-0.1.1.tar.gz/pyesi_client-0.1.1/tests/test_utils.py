"""Test utilities and helper functions."""

import pytest


def is_odd(number: int) -> bool:
    """
    Check if a number is odd.

    Args:
        number: The integer to check

    Returns:
        True if the number is odd, False otherwise

    Raises:
        TypeError: If number is not an integer
    """
    if not isinstance(number, int):
        raise TypeError(f"Expected int, got {type(number).__name__}")
    return number % 2 == 1


class TestIsOdd:
    """Tests for the is_odd utility function."""

    def test_is_odd_with_odd_numbers(self):
        """Test that odd numbers return True."""
        assert is_odd(1) is True
        assert is_odd(3) is True
        assert is_odd(5) is True
        assert is_odd(999) is True
        assert is_odd(-1) is True
        assert is_odd(-3) is True

    def test_is_odd_with_even_numbers(self):
        """Test that even numbers return False."""
        assert is_odd(0) is False
        assert is_odd(2) is False
        assert is_odd(4) is False
        assert is_odd(1000) is False
        assert is_odd(-2) is False
        assert is_odd(-4) is False

    def test_is_odd_type_error(self):
        """Test that non-integers raise TypeError."""
        with pytest.raises(TypeError):
            is_odd("5")  # type: ignore

        with pytest.raises(TypeError):
            is_odd(5.5)  # type: ignore

        with pytest.raises(TypeError):
            is_odd(None)  # type: ignore
