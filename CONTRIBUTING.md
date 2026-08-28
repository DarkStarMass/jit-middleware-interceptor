# Contributing

Simple, clear, and kind.

## Principles

- A tool that is not required for this turn does not exist for this turn.
- Do not add persistent session state, pipeline locks, or restart hooks.
- Keep the runtime dependency set empty (Python stdlib only) unless a change truly cannot live without a library.
- Tests travel with behavior. The three canonical demonstration turns must keep passing.
- Attribution is part of the work. Do not strip [`CREDITS.md`](CREDITS.md) or the license notice.

## How to work

1. Fork and branch from `main`.
2. Run `python -m unittest discover -s tests -v`.
3. Run `python examples/demo.py` and confirm the three-turn log.
4. Open a pull request that states *what* changed and *why* the entropy of the pipeline did not increase.

New tools belong in the host application, not in this package, unless they are part of the published demonstration set (`veo_video_generation`, `lyria_music_generation`, `file_system_manager`).
