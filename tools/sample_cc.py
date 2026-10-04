"""Interactively sample how Tempera displays a parameter across CC values 0-127.

Sends exact CC values to the device; after each one you type the value shown on
Tempera's screen. Results are merged into tempera/display_maps.json, which the GUI
uses to show real parameter values instead of raw CC numbers.

Usage:
    TEMPERA_PORT='Tempera' uv run python -m tools.sample_cc grain_length_cell
    uv run python -m tools.sample_cc --list
    uv run python -m tools.sample_cc spray_x --step 4

Only the non-linear emitter parameters in SAMPLED_PARAMS can be sampled; they are
sampled on Emitter 1 (all four emitters share the same curves). Tempera's MIDI
channel setting must be 'All' (or 2).

The CC is swept every --step values. At each prompt:
    <number>  record the displayed value
    <enter>   skip this CC value
    r         resend the CC (e.g. if the screen did not update)
    q         stop sampling and save what has been recorded so far
"""

import argparse
import os
import sys

import mido

from tempera.constants import TEMPERA_PORT_NAME
from tempera.display_map import (
    SAMPLED_PARAMS, DisplayMap, load_display_maps, save_display_maps,
)
from tempera.emitter import EMITTER_1_CC_MAP

EMITTER_CHANNEL = 2

# All sampled parameters are floating point on Tempera: a typed '7' means 7.0, so show at least one decimal
MIN_DECIMALS = 1

# Parameter name -> (CC number, MIDI channel)
SAMPLEABLE_PARAMS: dict[str, tuple[int, int]] = {
    name: (EMITTER_1_CC_MAP[name], EMITTER_CHANNEL) for name in SAMPLED_PARAMS
}


def sweep_values(step: int) -> list[int]:
    """CC values to sample: 0, step, 2*step, ... always ending at 127."""
    values = list(range(0, 128, step))
    if values[-1] != 127:
        values.append(127)
    return values


def decimals_of(text: str) -> int:
    return len(text.split('.', 1)[1]) if '.' in text else 0


def prompt_value(output, param: str, cc_num: int, channel: int, cc_value: int) -> str | None:
    """Send one CC value and read the displayed value. Returns the text, '' to skip, None to quit."""
    message = mido.Message('control_change', channel=channel - 1, control=cc_num, value=cc_value)
    output.send(message)
    while True:
        answer = input(f'  {param}: CC {cc_num} = {cc_value:3d} -> displayed value: ').strip()
        if answer.lower() == 'q':
            return None
        if answer.lower() == 'r':
            output.send(message)
            continue
        if answer == '':
            return ''
        try:
            float(answer)
            return answer
        except ValueError:
            print('    Enter a number, blank to skip, r to resend, q to stop.')


def sample(param: str, port: str, step: int) -> tuple[dict[int, float], int]:
    """Run the interactive sweep. Returns ({cc_value: displayed_value}, max decimals typed)."""
    cc_num, channel = SAMPLEABLE_PARAMS[param]
    samples: dict[int, float] = {}
    decimals = MIN_DECIMALS

    with mido.open_output(port) as output:
        print(f'Sampling {param} (CC {cc_num}, channel {channel}). Watch the value on Tempera.\n')

        queue = sweep_values(step)
        while queue:
            for cc_value in queue:
                answer = prompt_value(output, param, cc_num, channel, cc_value)
                if answer is None:
                    return samples, decimals
                if answer:
                    samples[cc_value] = float(answer)
                    decimals = max(decimals, decimals_of(answer))

            extra = input('\nExtra CC values to sample where the curve bends '
                          '(space separated), blank to finish: ').split()
            if extra in ([], ['q']):
                break
            try:
                queue = [int(v) for v in extra if 0 <= int(v) <= 127]
            except ValueError:
                print('  Ignoring: CC values must be integers 0-127.')
                queue = []

    return samples, decimals


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('param', nargs='?', help='Parameter to sample (see --list)')
    parser.add_argument('--list', action='store_true', help='List sampleable parameters and which are sampled')
    parser.add_argument('--step', type=int, default=8, help='CC step for the sweep (default 8, giving 17 points)')
    parser.add_argument('--unit', default=None, help="Suffix shown after the value in the GUI, e.g. '%%' or 'ms'")
    parser.add_argument('--replace', action='store_true', help='Discard existing points instead of merging')
    parser.add_argument('--port', default=os.environ.get(TEMPERA_PORT_NAME, 'Tempera'), help='MIDI output port')
    args = parser.parse_args()

    maps = load_display_maps()

    if args.list or not args.param:
        for name, (cc_num, channel) in SAMPLEABLE_PARAMS.items():
            status = f'{len(maps[name].points)} points' if name in maps else 'not sampled'
            print(f'  {name:<22} CC {cc_num:3d}  ch {channel}  {status}')
        return

    if args.param not in SAMPLEABLE_PARAMS:
        sys.exit(f'Unknown parameter {args.param!r}. Use --list to see options.')
    if not 1 <= args.step <= 127:
        sys.exit('--step must be in range 1..127')

    try:
        samples, decimals = sample(args.param, args.port, args.step)
    except OSError as e:
        sys.exit(f'Exception: {e}. Is your Tempera connected via USB Midi to this device?')
    except (KeyboardInterrupt, EOFError):
        sys.exit('\nAborted; nothing saved.')

    if not samples:
        print('No values recorded; nothing saved.')
        return

    existing = maps.get(args.param)
    points = {} if (args.replace or existing is None) else dict(existing.points)
    points.update(samples)
    maps[args.param] = DisplayMap(
        points=tuple(points.items()),
        decimals=max(decimals, existing.decimals if existing and not args.replace else 0),
        unit=args.unit if args.unit is not None else (existing.unit if existing else ''),
    )
    save_display_maps(maps)
    print(f'\nSaved {len(points)} points for {args.param} to tempera/display_maps.json')


if __name__ == '__main__':
    main()
