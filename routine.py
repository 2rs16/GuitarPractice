"""Offline chromatic guitar exercise generation."""

from dataclasses import dataclass
from itertools import permutations
import random

STRINGS = ("6 E (low)", "5 A", "4 D", "3 G", "2 B", "1 E (high)")
FINGERINGS = tuple(
    order for order in permutations((1, 2, 3, 4))
    if all(abs(left - right) <= 2 for left, right in zip(order, order[1:]))
)


@dataclass(frozen=True)
class Exercise:
    fingers: tuple[int, int, int, int]
    strings: tuple[str, ...]
    direction: str
    bpm: int
    repetitions: int
    start_fret: int


def make_exercise(difficulty: str, min_bpm: int, max_bpm: int) -> Exercise:
    """Make a playable four-fret pattern, favoring difficulty-appropriate tempos."""
    if difficulty not in ("Easy", "Medium", "Hard"):
        raise ValueError("difficulty must be Easy, Medium, or Hard")
    if min_bpm < 40 or max_bpm > 240 or min_bpm > max_bpm:
        raise ValueError("BPM range must be within 40..240 and ordered")

    span = max_bpm - min_bpm
    if difficulty == "Easy":
        bpm = random.randint(min_bpm, min_bpm + span // 3)
        fingers = random.choice(((1, 2, 3, 4), (4, 3, 2, 1)))
        repetitions = random.randint(2, 4)
    elif difficulty == "Medium":
        bpm = random.randint(min_bpm, max_bpm)
        fingers = random.choice(FINGERINGS)
        repetitions = random.randint(3, 6)
    else:
        bpm = random.randint(min_bpm + (span * 2) // 3, max_bpm)
        fingers = random.choice(FINGERINGS)
        repetitions = random.randint(5, 8)

    direction = random.choice(("Low to high", "High to low"))
    strings = STRINGS if direction == "Low to high" else tuple(reversed(STRINGS))
    return Exercise(fingers, strings, direction, bpm, repetitions, random.randint(1, 9))


def _self_test() -> None:
    for difficulty in ("Easy", "Medium", "Hard"):
        for _ in range(300):
            exercise = make_exercise(difficulty, 60, 120)
            assert sorted(exercise.fingers) == [1, 2, 3, 4]
            assert all(abs(a - b) <= 2 for a, b in zip(exercise.fingers, exercise.fingers[1:]))
            assert 1 <= exercise.start_fret <= 9
            assert exercise.strings in (STRINGS, tuple(reversed(STRINGS)))
            assert 60 <= exercise.bpm <= 120
            assert 2 <= exercise.repetitions <= 8
    print("300 patterns per difficulty passed.")


if __name__ == "__main__":
    _self_test()
