"""Builder state handling."""

from collections.abc import Callable, Iterator, Mapping
from copy import deepcopy
from typing import Any


def merge_settings(base: dict, new: dict) -> dict:
    """Return a new dictionary created by merging the settings from ``new`` into ``base``.

    :param base: The base dictionary to merge into
    :type base: ``dict``
    :param new: The new dictionary to merge
    :type new: ``dict``
    :return: A new merged dictionary
    :rtype: ``dict``
    """
    result = {}
    for base_key, base_value in list(base.items()):
        if base_key not in new:
            result[base_key] = deepcopy(base_value)
        elif isinstance(base_value, list):
            result[base_key] = list(base_value + new[base_key])
        elif isinstance(base_value, dict):
            result[base_key] = merge_settings(base_value, new[base_key])
        else:
            result[base_key] = new[base_key]
    for new_key, new_value in list(new.items()):
        if new_key not in base:
            result[new_key] = deepcopy(new_value)
    return result


class State(Mapping):
    """The State represents the state of the builder and provides support for observing changes."""

    def __init__(self) -> None:
        """Initialise the State."""
        self._state = {}
        self._listeners: dict[str, Callable[[State, Any]]] = {}

    def update(self: "State", settings: dict) -> None:
        """Update the `State` with the given `settings`."""
        self._state = merge_settings(self._state, settings)
        self._notify(settings)

    def add_listener(self: "State", prefix: str, callback: Callable[["State", Any], None]):
        """Add a listener that is notified when the `State` changes at the location `prefix`."""
        if prefix in self._listeners:
            self._listeners[prefix].append(callback)
        else:
            self._listeners[prefix] = [callback]

    def _notify(self: "State", settings: dict) -> None:
        """Notify all listeners of a change."""

        def walk(current: dict, path: list[str] | None = None):
            """Walk the updated settings and send out notifications."""
            if path is None:
                path = []
            for key, value in current.items():
                prefix = ".".join([*path, key])
                if prefix in self._listeners:
                    for callback in self._listeners[prefix]:
                        callback(self)
                if isinstance(value, dict):
                    walk(value, [*path, key])

        walk(settings)

    def __getitem__(self: "State", key: str) -> Any:
        """Retrieve an item from the `State`."""
        return self._state[key]

    def __len__(self: "State") -> int:
        """Return the length of this `State`."""
        return len(self._state)

    def __iter__(self: "State") -> Iterator:
        """Iterate over the items of this `State`."""
        return self._state.__iter__()
