"""A small offline desktop app for chromatic guitar practice."""

import json
import random
import re
import threading
import time
import tkinter as tk
from tkinter import messagebox
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

try:
    import winsound
except ImportError:
    winsound = None

from routine import make_exercise
from view import BG, CORAL, MUTED, build_ui


def format_duration(seconds: float) -> str:
    total = max(0, int(seconds))
    minutes, remainder = divmod(total, 60)
    return f"{minutes}:{remainder:02d}"


def parse_duration_mmss(value: str) -> int:
    text = (value or "").strip()
    if not text:
        raise ValueError("곡 길이를 입력하세요.")
    if ":" not in text:
        raise ValueError("분:초 형식으로 입력하세요. 예: 3:20")
    minutes_text, seconds_text = text.split(":", 1)
    try:
        minutes = int(minutes_text)
        seconds = int(seconds_text)
    except ValueError as exc:
        raise ValueError("분:초 형식이 올바르지 않습니다.") from exc
    if minutes < 0 or seconds < 0 or seconds >= 60:
        raise ValueError("초는 0~59 사이여야 합니다.")
    return minutes * 60 + seconds


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
        self.goal = None
        self.goal_duration_seconds = 0
        self.session_target_seconds = 0
        self.search_results = []
        self.search_in_progress = False
        self.goal_label = None
        self.song_length_label = None
        self.time_goal_label = None
        self.remaining_time_label = None
        self.search_results_data = []
        self.mode_var = None
        self.time_multiplier_var = None
        self.manual_duration_entry = None
        self.song_bpm_entry = None
        build_ui(self)

    def update_time_display(self) -> None:
        if not self.active:
            return
        if self.mode_var.get() == "time":
            remaining = max(0.0, self.session_target_seconds - (time.monotonic() - self.started_at))
            label = f"남은 시간: {format_duration(remaining)}"
            if self.remaining_time_label is not None:
                self.remaining_time_label.config(text=label)
            if self.time_goal_label is not None:
                self.time_goal_label.config(text=f"목표 시간: {format_duration(self.session_target_seconds)}")
        else:
            if self.remaining_time_label is not None:
                self.remaining_time_label.config(text="루틴 모드")

    def start_session(self) -> None:
        try:
            self.routine_count = int(self.routine_count_input.get())
            self.routine_repetitions = int(self.repetitions_input.get())
            if not 1 <= self.routine_repetitions <= 100:
                raise ValueError("루틴당 반복 횟수는 1~100회로 입력하세요.")
            mode = self.mode_var.get()
            if mode == "routine":
                low, high = int(self.min_bpm.get()), int(self.max_bpm.get())
                if not 1 <= self.routine_count <= 30:
                    raise ValueError("루틴 개수는 1~30개로 입력하세요.")
                if low < 40 or high > 240 or low > high:
                    raise ValueError("BPM은 40~240 범위에서 최소값이 최대값 이하여야 합니다.")
            else:
                if self.goal is None:
                    raise ValueError("먼저 곡을 검색하고 선택해 주세요.")
                if self.goal_duration_seconds <= 0:
                    raise ValueError("곡 길이 정보가 없거나 유효하지 않습니다. 곡 길이를 직접 입력해 주세요.")
                song_bpm = self.song_bpm_entry.get().strip()
                if not song_bpm:
                    raise ValueError("곡 BPM을 입력해 주세요.")
                try:
                    song_bpm = int(song_bpm)
                except ValueError as exc:
                    raise ValueError("곡 BPM은 숫자로 입력해 주세요.") from exc
                if not 40 <= song_bpm <= 240:
                    raise ValueError("곡 BPM은 40~240 범위여야 합니다.")
                multiplier = int(self.time_multiplier_var.get())
                self.session_target_seconds = self.goal_duration_seconds * multiplier
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
                return
        except ValueError as error:
            messagebox.showerror("입력 확인", str(error) or "숫자를 입력하세요.")
            return

        self.started_at = time.monotonic()
        self.active = True
        self.completed_count = 0
        self.history = []
        self.session_target_seconds = 0
        self.start_button.config(state="disabled")
        self.finish_button.config(state="normal")
        for control in self.session_inputs:
            control.config(state="disabled")
        self.next_exercise()
        self._tick()

    def next_exercise(self) -> None:
        if not self.active or self.completed_count >= self.routine_count:
            if self.mode_var.get() == "time" and self.active:
                pass
            else:
                return

        if self.mode_var.get() == "time":
            try:
                bpm = int(self.song_bpm_entry.get().strip())
            except ValueError:
                bpm = 120
        else:
            bpm = random.randint(int(self.min_bpm.get()), int(self.max_bpm.get()))

        self.current = make_exercise(self.difficulty.get(), bpm, bpm)
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
        if self.mode_var.get() == "time":
            remaining = max(0.0, self.session_target_seconds - (time.monotonic() - self.started_at))
            self.remaining_label.config(text=f"{format_duration(remaining)} 남음")
            if self.time_goal_label is not None:
                self.time_goal_label.config(text=f"목표 시간: {format_duration(self.session_target_seconds)}")
        else:
            self.remaining_label.config(text=f"{self.completed_count + 1} / {self.routine_count}")
        self.last_beat = -1

    def _tick(self) -> None:
        if not self.active:
            return

        if self.mode_var.get() == "time":
            elapsed = time.monotonic() - self.started_at
            remaining = max(0.0, self.session_target_seconds - elapsed)
            if self.remaining_time_label is not None:
                self.remaining_time_label.config(text=f"남은 시간: {format_duration(remaining)}")
            if elapsed >= self.session_target_seconds:
                self.finish_session()
                return

        elapsed = time.monotonic() - self.routine_started_at
        interval = 60.0 / self.current.bpm
        beat = int(elapsed / interval)
        if beat >= self.beats_per_routine:
            self.completed_count += 1
            if self.mode_var.get() == "time":
                self.next_exercise()
                elapsed = 0.0
                beat = 0
            else:
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

    def search_song(self) -> None:
        if self.active:
            return
        query = (self.search_entry.get() or "").strip()
        if not query:
            messagebox.showwarning("검색", "검색어를 입력하세요.")
            return
        if self.search_in_progress:
            return
        self.search_in_progress = True
        self.search_button.config(state="disabled", text="검색 중...")
        self.search_status_label.config(text="검색 중...", fg=MUTED)
        self.search_results.delete(0, tk.END)
        thread = threading.Thread(target=self._fetch_search_results, args=(query,), daemon=True)
        thread.start()

    def _fetch_search_results(self, query: str) -> None:
        encoded_query = urllib_parse.quote_plus(query)
        url = f"https://itunes.apple.com/search?term={encoded_query}&media=music&entity=song&limit=10"
        try:
            request = urllib_request.Request(url, headers={"User-Agent": "GuitarPractice/1.0"})
            with urllib_request.urlopen(request, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8", errors="replace"))
        except (urllib_error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
            message = f"인터넷 연결을 확인해 주세요.\n{error.__class__.__name__}: {error}"
            self.root.after(0, lambda: self._apply_search_error(message))
            return

        results = []
        for item in payload.get("results", []):
            title = item.get("trackName") or item.get("collectionName")
            artist = item.get("artistName") or "알 수 없음"
            album = item.get("collectionName") or "앨범 정보 없음"
            if title:
                result = {
                    "title": title,
                    "artist": artist,
                    "album": album,
                    "trackTimeMillis": item.get("trackTimeMillis"),
                    "kind": item.get("kind"),
                }
                results.append(result)

        self.root.after(0, lambda: self._apply_search_results(results))

    def _apply_search_error(self, message: str) -> None:
        self.search_in_progress = False
        self.search_button.config(state="normal", text="검색")
        self.search_status_label.config(text=message, fg="#ffb2a3")
        self.search_results.delete(0, tk.END)
        self.search_results.insert(tk.END, "검색 결과를 불러오지 못했습니다.")
        self.search_results_data = []

    def _apply_search_results(self, results: list[dict]) -> None:
        self.search_in_progress = False
        self.search_button.config(state="normal", text="검색")
        self.search_results_data = results
        self.search_results.delete(0, tk.END)
        if not results:
            self.search_status_label.config(text="검색 결과가 없습니다.", fg=MUTED)
            self.search_results.insert(tk.END, "검색 결과 없음")
            return
        for result in results:
            title = result.get("title") or "제목 없음"
            artist = result.get("artist") or "아티스트 없음"
            duration = result.get("trackTimeMillis")
            label = f"{title} - {artist}"
            if duration is not None:
                label += f" ({format_duration(int(duration) / 1000)})"
            self.search_results.insert(tk.END, label)
        self.search_status_label.config(text=f"{len(results)}개의 결과를 찾았습니다.", fg="#8de0bd")

    def on_search_result_selected(self, event=None) -> None:
        if self.active or self.search_in_progress:
            return
        if not getattr(self, "search_results_data", []):
            return
        selection = self.search_results.curselection()
        if not selection:
            return
        item = self.search_results_data[selection[0]]
        self.goal = item
        self.goal_label.config(text=f"연습 목표 곡: {item['title']} - {item['artist']}", fg="#8de0bd")
        duration_ms = item.get("trackTimeMillis")
        if isinstance(duration_ms, (int, float)) and duration_ms > 0:
            self.goal_duration_seconds = int(duration_ms / 1000)
            self.song_length_label.config(text=f"곡 길이: {format_duration(self.goal_duration_seconds)}")
            self.search_status_label.config(text=f"선택됨: {item['title']} ({item['artist']}) / {format_duration(self.goal_duration_seconds)}", fg="#8de0bd")
        else:
            self.goal_duration_seconds = 0
            self.song_length_label.config(text="곡 길이 정보 없음")
            self.search_status_label.config(text=f"선택됨: {item['title']} ({item['artist']}) / 곡 길이 정보 없음", fg="#8de0bd")
        self.time_goal_label.config(text="목표 시간: 설정 전")

    def apply_manual_duration(self) -> None:
        if self.active:
            return
        value = (self.manual_duration_entry.get() or "").strip()
        if not value:
            messagebox.showwarning("곡 길이 입력", "곡 길이를 입력해 주세요. (예: 3:20)")
            return
        try:
            total_seconds = parse_duration_mmss(value)
        except ValueError as error:
            messagebox.showwarning("곡 길이 입력", str(error))
            return
        self.goal_duration_seconds = total_seconds
        self.song_length_label.config(text=f"곡 길이: {format_duration(total_seconds)}")
        self.search_status_label.config(text=f"곡 길이 수동 입력: {format_duration(total_seconds)}", fg="#8de0bd")

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
        actual_seconds = int(time.monotonic() - self.started_at)
        lines = [f"완료 루틴: {self.completed_count} / {self.routine_count}개" if self.mode_var.get() == "routine" else f"완료 루틴: {self.completed_count}개",
                 f"총 연습 시간: {format_duration(actual_seconds)}", "", "이번 세션 루틴:"]

        if self.goal:
            title = self.goal.get("title") or "제목 없음"
            artist = self.goal.get("artist") or "아티스트 없음"
            album = self.goal.get("album") or "앨범 정보 없음"
            lines.append(f"연습 목표: {title} - {artist} / {album}")
            if self.goal_duration_seconds > 0:
                lines.append(f"곡 길이: {format_duration(self.goal_duration_seconds)}")
            else:
                lines.append("곡 길이: 곡 길이 정보 없음")
            if self.mode_var.get() == "time":
                lines.append(f"목표 연습 시간: {format_duration(self.session_target_seconds)}")
                lines.append(f"실제 연습 시간: {format_duration(actual_seconds)}")

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
        self.time_goal_label.config(text="목표 시간: 설정 전")
        if self.remaining_time_label is not None:
            self.remaining_time_label.config(text="루틴 모드")
        messagebox.showinfo("연습 기록", "\n".join(lines))
        if close_window:
            self.root.destroy()


def main() -> None:
    root = tk.Tk()
    GuitarPracticeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
