"""Tests for the state management functionality."""

from unittest.mock import Mock

from ou_container_builder.state import State, merge_settings


def test_basic_merge() -> None:
    """Test that a basic merge works."""
    result = merge_settings({}, {"a": "value"})
    assert result["a"] == "value"


def test_basic_merge_with_existing_data() -> None:
    """Test that a basic merge works with existing data."""
    result = merge_settings({"b": "another value"}, {"a": "value"})
    assert result["a"] == "value"
    assert result["b"] == "another value"


def test_basic_merge_overwrite() -> None:
    """Test that a basic merge works with overwriting simple values."""
    result = merge_settings({"a": "old value"}, {"a": "new value"})
    assert result["a"] == "new value"


def test_merge_list() -> None:
    """Test that list items are merged together."""
    result = merge_settings({"a": ["one", "two"]}, {"a": ["three", "four"]})
    assert result["a"] == ["one", "two", "three", "four"]


def test_merge_nested() -> None:
    """Test that merging nested objects works."""
    result = merge_settings(
        {"a": {"a1": ["one", "two"], "a2": "old value", "a3": "keep this"}},
        {"a": {"a1": ["three", "four"], "a2": "new value"}, "b": {"b1": "something new"}},
    )
    assert result["a"]["a1"] == ["one", "two", "three", "four"]
    assert result["a"]["a2"] == "new value"
    assert result["a"]["a3"] == "keep this"
    assert result["b"]["b1"] == "something new"


def test_state_update() -> None:
    """Test that updating the state works."""
    state = State()
    state.update({"a": {"a1": ["one", "two"], "a2": "old value", "a3": "keep this"}})
    assert state["a"]["a1"] == ["one", "two"]
    assert state["a"]["a2"] == "old value"
    assert state["a"]["a3"] == "keep this"
    state.update({"a": {"a1": ["three", "four"], "a2": "new value"}, "b": {"b1": "something new"}})
    assert state["a"]["a1"] == ["one", "two", "three", "four"]
    assert state["a"]["a2"] == "new value"
    assert state["a"]["a3"] == "keep this"
    assert state["b"]["b1"] == "something new"


def test_state_basic_listener() -> None:
    """Test that a basic listener is called."""
    listener = Mock()
    state = State()
    state.add_listener("a", listener)
    state.update({"a": "new value"})
    assert listener.called


def test_multiple_listeners() -> None:
    """Test that multiple listeners are called."""
    listener1 = Mock()
    listener2 = Mock()
    state = State()
    state.add_listener("a", listener1)
    state.add_listener("a", listener2)
    state.update({"a": "new value"})
    assert listener1.called
    assert listener2.called


def test_state_length() -> None:
    """Test that the state reports the correct length."""
    state = State()
    assert len(state) == 0
    state.update({"a": "old value"})
    assert len(state) == 1
    state.update({"a": "new value"})
    assert len(state) == 1
    state.update({"b": "new value"})
    assert len(state) == 2


def test_state_iterate() -> None:
    """Test that iterating over the top-level state keys works."""
    state = State()
    for _ in state:
        raise AssertionError()
    state.update({"a": "value"})
    for value in state:
        assert value == "a"
