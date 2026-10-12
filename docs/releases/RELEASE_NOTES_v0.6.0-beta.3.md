# Mobile Fuel Stations v0.6.0-beta.3

## Coordinator lifecycle diagnostics

This beta adds read-only runtime evidence for diagnosing the beta.2 startup
state without changing the existing 15-minute polling behavior:

- coordinator instance identity and listener count;
- configured polling interval and whether Home Assistant currently has a
  periodic refresh callback scheduled;
- last update/provider attempt and success timestamps;
- GPS availability and GPS-listener registration without coordinates;
- startup-recovery and recovery-task status.

The next refresh deadline is reported as unknown because Home Assistant Core
stores only a cancellation callback for the timer. No deadline is inferred.

The live beta.2 investigation did not prove whether polling was absent,
unscheduled, or failing inside the update path. Therefore beta.3 does not add
a speculative retry architecture or alter coordinator polling semantics.

## Validation scope

This branch is prepared for local Python, frontend, build, Hassfest/Validate,
diff, and secret checks. No Home Assistant reload/restart, VM104 change, push,
tag, merge, or GitHub release is part of this work.
