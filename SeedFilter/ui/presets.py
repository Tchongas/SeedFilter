"""Preset management: built-in Default plus user-saved presets."""
import json
import os
from copy import deepcopy

from .model import Filter
from .paths import DATA_DIR


PRESET_FILE = os.path.join(DATA_DIR, "presets.json")


def _default():
    """Return a fresh default filter."""
    return Filter()


BUILT_IN = {
    "Default": _default,
}


def _load_user_presets():
    """Load user presets from the JSON file."""
    if not os.path.exists(PRESET_FILE):
        return {}
    try:
        with open(PRESET_FILE, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}
    presets = {}
    for name, code in data.items():
        if isinstance(code, str):
            try:
                presets[name] = Filter.from_code(code)
            except Exception:
                continue
    return presets


def _save_user_presets(presets):
    """Write user presets to the JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PRESET_FILE, "w") as f:
        json.dump({name: f.to_code() for name, f in presets.items()}, f, indent=2)


def list_presets():
    """Return a list of all preset names, built-in first."""
    return list(BUILT_IN) + list(_load_user_presets())


def get_preset(name):
    """Return a deep copy of the requested preset filter."""
    if name in BUILT_IN:
        return deepcopy(BUILT_IN[name]())
    user = _load_user_presets()
    if name in user:
        return deepcopy(user[name])
    raise KeyError(f"Preset '{name}' not found")


def save_preset(name, filter_obj):
    """Save the current filter as a named user preset."""
    user = _load_user_presets()
    user[name] = deepcopy(filter_obj)
    _save_user_presets(user)


def delete_preset(name):
    """Delete a user preset. Built-in presets cannot be deleted."""
    if name in BUILT_IN:
        raise ValueError(f"Cannot delete built-in preset '{name}'")
    user = _load_user_presets()
    user.pop(name, None)
    _save_user_presets(user)


def import_preset(name, code):
    """Import a filter code string as a named user preset."""
    f = Filter.from_code(code)
    save_preset(name, f)
