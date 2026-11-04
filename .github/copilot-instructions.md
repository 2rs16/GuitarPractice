# Copilot instructions for GuitarPractice

## Project shape
- This repo is a small offline desktop app for chromatic guitar practice; it does not use a web stack or package manager.
- The app entry point is `main.py`; it creates a `GuitarPracticeApp` and starts `root.mainloop()`.
- `view.py` is the UI layer: `build_ui(app)` creates the Tkinter widgets, styles, and session controls. Keep layout/state wiring there when changing the screen.
- `routine.py` defines the exercise model and generation logic. `make_exercise(...)` returns a dataclass `Exercise` with finger order, string path, BPM, fret start, and repetition count.
- `main.py` coordinates runtime state (`active`, `history`, `completed_count`, `after_id`, etc.) and uses `after()` scheduling instead of threads.

## Core behavior and constraints
- Exercise rules are intentionally strict: difficulty is `Easy | Medium | Hard`, BPM is within 40..240, and the generated finger sequence must be playable (`sorted(fingers) == [1,2,3,4]` and adjacent finger gaps <= 2).
- Session flow is: validate inputs -> start timer -> call `next_exercise()` -> `_tick()` updates beat lights and sound -> finish at routine count.
- The app supports cancellation mid-session via `finish_session()` and shows a summary dialog with per-routine status.
- Keep changes compatible with the existing UI style: dark green/charcoal palette and Korean labels (`루틴 개수`, `연습 시작`, etc.).

## Workflow
- Run the app with: `python main.py`
- Run the generator safety check with: `python routine.py`
- The project depends only on Python standard library modules (`tkinter`, `time`, `random`, `itertools`, `dataclasses`). Do not add external dependencies unless the request explicitly requires it.

## Editing guidance
- Prefer adding logic to `routine.py` for exercise-generation changes and to `view.py` for widgets/labels/colors.
- Keep `main.py` focused on orchestration and validation; avoid burying exercise rules there.
- When changing the beat/timing behavior, preserve the `after(30, self._tick)` pattern and `winsound.Beep(...)` fallback behavior.
- When changing exercise generation, keep the existing self-test assertions in `routine.py` valid.

## Example conventions
- Use the existing data class pattern (`Exercise`) rather than introducing separate dicts for exercise state.
- Follow the current naming style: `start_session`, `next_exercise`, `_tick`, `finish_session`, `close_window`, `build_ui`, `field`, `metric`.
- Prefer direct `tkinter` state/config updates (e.g., `config(...)`) over custom observer abstractions.
