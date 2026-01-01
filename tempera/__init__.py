"""Tempera MIDI control library."""

# Lazy imports to avoid circular dependency with midi.py
def __getattr__(name):
    if name == 'Emitter':
        from tempera.emitter import Emitter
        return Emitter
    elif name == 'EmitterPool':
        from tempera.emitter_pool import EmitterPool
        return EmitterPool
    elif name == 'TemperaGlobal':
        from tempera.tempera_global import TemperaGlobal
        return TemperaGlobal
    elif name == 'Track':
        from tempera.track import Track
        return Track
    raise AttributeError(f"module 'tempera' has no attribute {name!r}")

__all__ = ['Emitter', 'EmitterPool', 'TemperaGlobal', 'Track']
