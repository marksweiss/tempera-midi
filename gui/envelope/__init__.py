"""Envelope automation module for Tempera GUI."""

# Use lazy imports to avoid circular import issues
__all__ = ['Envelope', 'EnvelopePoint', 'EnvelopePanel', 'EnvelopeCanvas', 'EnvelopeManager']


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
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
