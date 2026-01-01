# Contributing to Tempera MIDI

Thanks for your interest in contributing! This is a small community project, and contributions of all kinds are welcome.

## Ways to Contribute

- **Bug reports**: Open an issue with steps to reproduce
- **Bug fixes**: Submit a PR with a fix
- **Features**: Open an issue to discuss before implementing
- **Documentation**: Improvements to docs or examples
- **Hardware testing**: Testing on your Tempera and reporting results

## Development Setup

1. Install [uv](https://github.com/astral-sh/uv) if you haven't already
2. Clone the repo and install dependencies:
   ```bash
   git clone https://github.com/marksweiss/tempera-midi.git
   cd tempera-midi
   uv sync
   ```

## Running Tests

### Virtual Port Tests (No Hardware Required)

These tests verify MIDI message generation without needing a Tempera:

```bash
uv run python -m unittest discover test -v
```

### Hardware Tests

If you have a Tempera connected:

```bash
RUN_HARDWARE_TESTS=1 TEMPERA_PORT='Tempera' uv run python -m unittest discover test -v
```

## Submitting Changes

1. Fork the repository
2. Create a branch for your changes
3. Make your changes and ensure tests pass
4. Submit a pull request

For larger changes, please open an issue first to discuss the approach.

## Questions?

Open an issue or reach out to the maintainer.
