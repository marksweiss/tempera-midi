"""Canvas file management for saving/loading complete Tempera state."""

import json
import os
import platform
from pathlib import Path


CANVAS_FORMAT_VERSION = 1


def get_canvas_directory() -> Path:
    """Get the platform-appropriate canvas storage directory.

    Returns:
        Path to canvas directory (created if needed):
        - macOS/Linux: ~/.config/tempera-edit/canvases/
        - Windows: %APPDATA%/tempera-edit/canvases/
    """
    system = platform.system()
    if system == 'Windows':
        base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
    else:
        base = Path.home() / '.config'

    canvas_dir = base / 'tempera-edit' / 'canvases'
    canvas_dir.mkdir(parents=True, exist_ok=True)
    return canvas_dir


def list_canvases() -> list[str]:
    """List all saved canvas names (sorted, without .json extension)."""
    canvas_dir = get_canvas_directory()
    return sorted(p.stem for p in canvas_dir.glob('*.json'))


def save_canvas(name: str, state_dict: dict, metadata: dict) -> Path:
    """Save a canvas to the canvas directory.

    Args:
        name: Canvas name (used as filename, .json appended).
        state_dict: Serialized state from StateManager.serialize_state().
        metadata: Additional metadata (e.g. grid_mode).

    Returns:
        Path to the saved file.
    """
    canvas = {
        'version': CANVAS_FORMAT_VERSION,
        'metadata': metadata,
        'state': state_dict,
    }
    filepath = get_canvas_directory() / f'{name}.json'
    with open(filepath, 'w') as f:
        json.dump(canvas, f, indent=2)
    return filepath


def load_canvas(name: str) -> tuple[dict, dict]:
    """Load a canvas from the canvas directory.

    Args:
        name: Canvas name (without .json extension).

    Returns:
        Tuple of (state_dict, metadata).

    Raises:
        FileNotFoundError: If canvas file doesn't exist.
    """
    filepath = get_canvas_directory() / f'{name}.json'
    with open(filepath, 'r') as f:
        canvas = json.load(f)

    if 'version' in canvas and 'state' in canvas:
        return canvas['state'], canvas.get('metadata', {})

    # Legacy fallback: treat entire file as a preset (no metadata)
    return canvas, {}


def delete_canvas(name: str) -> bool:
    """Delete a canvas file.

    Returns:
        True if deleted, False if not found.
    """
    filepath = get_canvas_directory() / f'{name}.json'
    if filepath.exists():
        filepath.unlink()
        return True
    return False
