"""Tests de la jerarquía de excepciones."""
from __future__ import annotations
import pytest

from firesteeljm.exceptions import (
    FireSteelError,
    ConfigurationError,
    ConvergenceError,
    DependencyError,
)


def test_base_is_value_error():
    """FireSteelError debe heredar ValueError (backward compat)."""
    assert issubclass(FireSteelError, ValueError)


def test_subclasses_inherit_base():
    for cls in (ConfigurationError, ConvergenceError, DependencyError):
        assert issubclass(cls, FireSteelError)
        assert issubclass(cls, ValueError)


def test_raise_and_catch_as_value_error():
    with pytest.raises(ValueError):
        raise ConfigurationError("malo")


def test_raise_and_catch_as_base():
    with pytest.raises(FireSteelError):
        raise ConvergenceError("no converge")
