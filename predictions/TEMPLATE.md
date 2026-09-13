# Pre-registered prediction — <scenario>, committed <YYYY-MM-DD HH:MM>

Copy to `prediction_<timestamp>.md`, fill in, and **commit before the first chaos run**. Graded on
the quality of the reasoning, not on the accuracy of the numbers (CLAUDE.md §2).

## Configuration under test
Ramp stages, bake seconds, poll interval, decision mode, offered rps, injected fault — the exact
values, so this prediction is falsifiable against a specific run.

## Predictions
| Quantity | Predicted | Reasoning |
|---|---|---|
| Stage at which rollback fires | | |
| Time from fault injection to rollback (s) | | |
| Blast radius (requests served by the bad canary) | | |
| Requests affected as % of all traffic in the run | | |

## Derivation
Show the arithmetic — offered rate x canary weight x time-to-detect — rather than asserting a
number. Detection time should follow from the sample size the decision rule needs, not from a guess.

## What would falsify this
Name the observation that would mean the reasoning was wrong, not merely the number off.

## After the run
Recorded outcome, and a *mechanistic* explanation of any deviation. "It was faster than expected"
is not an explanation.
