"""Envelope automation module for Tempera GUI."""

# Use lazy imports to avoid circular import issues
__all__ = [
    'Envelope', 'EnvelopePoint', 'EnvelopePanel', 'EnvelopeCanvas',
    'EnvelopeManager', 'EnvelopePreset', 'generate_preset_points', 'PresetButton'
]


def __getattr__(name):
    """Lazy import for envelope classes."""
    if name in ('Envelope', 'EnvelopePoint'):
        from gui.envelope.envelope import Envelope, EnvelopePoint
        return Envelope if name == 'Envelope' else EnvelopePoint
    elif name in ('EnvelopePanel', 'EnvelopeCanvas'):
        from gui.envelope.envelope_panel import EnvelopePanel, EnvelopeCanvas
        return EnvelopePanel if name == 'EnvelopePanel' else EnvelopeCanvas
    elif name == 'EnvelopeManager':
        from gui.envelope.envelope_manager import EnvelopeManager
        return EnvelopeManager
    elif name in ('EnvelopePreset', 'generate_preset_points'):
        from gui.envelope.envelope_presets import EnvelopePreset, generate_preset_points
        return EnvelopePreset if name == 'EnvelopePreset' else generate_preset_points
    elif name == 'PresetButton':
        from gui.envelope.preset_button import PresetButton
        return PresetButton
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
