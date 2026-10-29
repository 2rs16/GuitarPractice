"""A small offline desktop app for chromatic guitar practice."""

import time
import tkinter as tk
from tkinter import messagebox

try:
    import winsound
except ImportError:
    winsound = None

from routine import make_exercise
from view import BG, CORAL, MUTED, build_ui


class GuitarPracticeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Chromatic Practice | 기타 연습 루틴")
        self.root.geometry("980x650")
        self.root.minsize(860, 590)
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)
        self.started_at = 0.0
        self.routine_started_at = 0.0
        self.routine_count = 0
        self.routine_repetitions = 0
        self.completed_count = 0
        self.beats_per_routine = 0
        self.active = False
        self.after_id = None
        self.last_beat = -1
        self.history = []
        self.current = None
        build_ui(self)

    def start_session(self) -> None:
        try:
            self.routine_count = int(self.routine_count_input.get())
            self.routine_repetitions = int(self.repetitions_input.get())
            low, high = int(self.min_bpm.get()), int(self.max_bpm.get())
            if not 1 <= self.routine_count <= 30:
                raise ValueError("루틴 개수는 1~30개로 입력하세요.")
            if not 1 <= self.routine_repetitions <= 100:
                raise ValueError("루틴당 반복 횟수는 1~100회로 입력하세요.")
            if low < 40 or high > 240 or low > high:
                raise ValueError("BPM은 40~240 범위에서 최소값이 최대값 이하여야 합니다.")
        except ValueError as error:
            messagebox.showerror("입력 확인", str(error) or "숫자를 입력하세요.")
            return
        self.started_at = time.monotonic()
        self.active = True
        self.completed_count = 0
        self.history = []
        self.start_button.config(state="disabled")
        self.finish_button.config(state="normal")
        for control in self.session_inputs:
            control.config(state="disabled")
        self.next_exercise()
        self._tick()

    def next_exercise(self) -> None:
        if not self.active or self.completed_count >= self.routine_count:
            return
        self.current = make_exercise(self.difficulty.get(), int(self.min_bpm.get()), int(self.max_bpm.get()))
        self.history.append((self.current, self.routine_repetitions))
        self.routine_started_at = time.monotonic()
        self.beats_per_routine = self.routine_repetitions * len(self.current.strings) * len(self.current.fingers)
        exercise = self.current
        self.pattern_label.config(text=f"{exercise.start_fret}~{exercise.start_fret + 3} 프렛 · {exercise.direction}")
        strings = "  →  ".join(exercise.strings)
        self.details_label.config(text=(f"손가락 순서   {' - '.join(map(str, exercise.fingers))}\n"
                                        f"줄 진행          {strings}\n"
                                        f"반복 횟수       {self.routine_repetitions}회"))
        self.bpm_label.config(text=str(exercise.bpm))
        self.remaining_label.config(text=f"{self.completed_count + 1} / {self.routine_count}")
        self.last_beat = -1

    def _tick(self) -> None:
        if not self.active:
            return
        elapsed = time.monotonic() - self.routine_started_at
        interval = 60.0 / self.current.bpm
        beat = int(elapsed / interval)
        if beat >= self.beats_per_routine:
            self.completed_count += 1
            if self.completed_count >= self.routine_count:
                self.finish_session()
                return
            self.next_exercise()
            elapsed = 0.0
            beat = 0
        if beat != self.last_beat:
            self.last_beat = beat
            active_light = beat % 4
            for index, light in enumerate(self.beat_lights):
                light.config(bg=CORAL if index == active_light else "#35423d",
                             fg=BG if index == active_light else MUTED)
            try:
                if winsound:
                    winsound.Beep(880 if active_light == 0 else 660, 35)
                else:
                    self.root.bell()
            except RuntimeError:
                pass
        self.after_id = self.root.after(30, self._tick)

    def finish_session(self) -> None:
        self._end_session(close_window=False)

    def close_window(self) -> None:
        if self.started_at:
            self._end_session(close_window=True)
            return
        self.root.destroy()

    def _end_session(self, close_window: bool) -> None:
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None
        if not self.started_at:
            if close_window:
                self.root.destroy()
            return
        self.active = False
        elapsed = int(time.monotonic() - self.started_at)
        lines = [f"완료 루틴: {self.completed_count} / {self.routine_count}개",
                 f"총 연습 시간: {elapsed // 60}분 {elapsed % 60}초", "", "이번 세션 루틴:"]
        for index, (item, repetitions) in enumerate(self.history, 1):
            fingers = "-".join(map(str, item.fingers))
            status = "완료" if index <= self.completed_count else "진행 중 종료"
            lines.append(f"{index}. {status} / {item.start_fret}~{item.start_fret + 3}프렛 / {fingers} / "
                         f"{item.direction} / {item.bpm} BPM / {repetitions}회")
        self.started_at = 0.0
        self.start_button.config(state="normal")
        self.finish_button.config(state="disabled")
        for control in self.session_inputs:
            control.config(state="normal")
        self.remaining_label.config(text="-- / --")
        self.bpm_label.config(text="---")
        self.pattern_label.config(text="준비되면 연습 시작을 눌러주세요")
        self.details_label.config(text="손가락 패턴과 메트로놈이 여기에 표시됩니다.")
        messagebox.showinfo("연습 기록", "\n".join(lines))
        if close_window:
            self.root.destroy()


def main() -> None:
    root = tk.Tk()
    GuitarPracticeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
