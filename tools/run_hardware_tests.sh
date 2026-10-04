#!/usr/bin/env bash

RUN_HARDWARE_TESTS=1 TEMPERA_PORT='Tempera' uv run python -m unittest discover test -v