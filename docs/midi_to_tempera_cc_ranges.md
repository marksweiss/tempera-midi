# MIDI CC Ranges for Tempera

The Tempera does not consistently map incoming CC values to the range of available values for a particuluar setting.
This is because different controls have different ranges of values, different semantics, and affect performance
differently and on different curves of values.

As a result, there is no simple rule for mapping the 0-127 range of MIDI CC values to the range of values for a
particular setting. The process of discovering the range of values for a given setting and its effect is one of
trial and error and also requires some subjective additional context to understand the effect of the setting.

The following table documents the range of values for each setting, and the corresponding MIDI CC value that maps to
the minimum and maximum values for the setting.

TODO: Complete for all settings

| MIDI CC Message   | Tempera Setting | MIDI CC Value | Tempera Value | Notes |
|-------------------|-----------------|---------------|---------------|-------|
| GRAIN_LENGTH_CELL | Grain length    | 16            | 0.2222        |       |
| GRAIN_LENGTH_CELL | Grain length    | 64            | 0.8888        |       |
| GRAIN_LENGTH_CELL | Grain length    | 80            | 2.0000        |       |
| GRAIN_LENGTH_CELL | Grain length    | 96            | 4.0000        |       |
| GRAIN_LENGTH_CELL | Grain length    | 112           | 6.0000        |       |
| GRAIN_LENGTH_CELL | Grain length    | 127           | 8.0000        |       |
| GRAIN_DENSITY     | Grain density   | 16            | 0.5000        |       |
| GRAIN_DENSITY     | Grain density   | 32            | 1.0000        |       |
| GRAIN_DENSITY     | Grain density   | 48            | 2.0000        |       |
| GRAIN_DENSITY     | Grain density   | 56            | 3.0000        |       |
| GRAIN_DENSITY     | Grain density   | 64            | 6.0000        |       |
| GRAIN_DENSITY     | Grain density   | 80            | 18.0000       |       |
| GRAIN_DENSITY     | Grain density   | 96            | 34.0000       |       |
| GRAIN_DENSITY     | Grain density   | 112           | 60.0000       |       |
| GRAIN_DENSITY     | Grain density   | 127           | 100.0000      |       |

