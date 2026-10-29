"""Tkinter layout for the practice app."""

import tkinter as tk

BG = "#111817"
PANEL = "#1b2623"
TEXT = "#f0f3e8"
MUTED = "#a2b2a7"
MINT = "#8de0bd"
CORAL = "#ff806b"


def build_ui(app) -> None:
    root = app.root
    header = tk.Frame(root, bg=BG)
    header.pack(fill="x", padx=34, pady=(26, 20))
    tk.Label(header, text="CHROMATIC PRACTICE", bg=BG, fg=MINT,
             font=("Segoe UI", 10, "bold")).pack(anchor="w")
    tk.Label(header, text="오늘의 기타 연습", bg=BG, fg=TEXT,
             font=("Malgun Gothic", 25, "bold")).pack(anchor="w", pady=(3, 0))

    body = tk.Frame(root, bg=BG)
    body.pack(fill="both", expand=True, padx=34, pady=(0, 30))
    setup = tk.Frame(body, bg=PANEL, padx=24, pady=22, width=300)
    setup.pack(side="left", fill="y")
    setup.pack_propagate(False)
    tk.Label(setup, text="SESSION SETUP", bg=PANEL, fg=MINT,
             font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 20))
    app.routine_count_input = field(setup, "루틴 개수", "5")
    app.repetitions_input = field(setup, "루틴당 반복 횟수", "4")
    app.difficulty = tk.StringVar(value="Medium")
    tk.Label(setup, text="난이도", bg=PANEL, fg=MUTED,
             font=("Malgun Gothic", 10)).pack(anchor="w", pady=(14, 5))
    app.level_menu = tk.OptionMenu(setup, app.difficulty, "Easy", "Medium", "Hard")
    app.level_menu.config(bg="#273630", fg=TEXT, activebackground="#354a40",
                          activeforeground=TEXT, highlightthickness=0, relief="flat", anchor="w")
    app.level_menu["menu"].config(bg="#273630", fg=TEXT)
    app.level_menu.pack(fill="x")
    row = tk.Frame(setup, bg=PANEL)
    row.pack(fill="x", pady=(15, 0))
    app.min_bpm = field(row, "최소 BPM", "70", side="left")
    app.max_bpm = field(row, "최대 BPM", "120", side="right")
    app.session_inputs = [app.routine_count_input, app.repetitions_input,
                          app.level_menu, app.min_bpm, app.max_bpm]
    app.start_button = tk.Button(setup, text="연습 시작  →", command=app.start_session,
                                 bg=MINT, fg="#10231b", activebackground="#b5f0d4",
                                 relief="flat", font=("Malgun Gothic", 11, "bold"),
                                 padx=12, pady=11, cursor="hand2")
    app.start_button.pack(fill="x", pady=(26, 0))
    app.finish_button = tk.Button(setup, text="세션 종료 및 기록 보기", command=app.finish_session,
                                  bg="#34423c", fg=TEXT, activebackground="#45564e",
                                  relief="flat", font=("Malgun Gothic", 10), pady=9,
                                  state="disabled", cursor="hand2")
    app.finish_button.pack(fill="x", pady=(9, 0))

    live = tk.Frame(body, bg=BG)
    live.pack(side="left", fill="both", expand=True, padx=(24, 0))
    metrics = tk.Frame(live, bg=BG)
    metrics.pack(fill="x")
    app.remaining_label = metric(metrics, "루틴 진행", "-- / --", "left")
    app.bpm_label = metric(metrics, "현재 BPM", "---", "right")
    exercise = tk.Frame(live, bg=PANEL, padx=26, pady=23)
    exercise.pack(fill="both", expand=True, pady=(18, 0))
    tk.Label(exercise, text="CURRENT EXERCISE", bg=PANEL, fg=MINT,
             font=("Segoe UI", 10, "bold")).pack(anchor="w")
    app.pattern_label = tk.Label(exercise, text="준비되면 연습 시작을 눌러주세요",
                                 bg=PANEL, fg=TEXT, font=("Malgun Gothic", 20, "bold"),
                                 wraplength=520, justify="left")
    app.pattern_label.pack(anchor="w", pady=(28, 14))
    app.details_label = tk.Label(exercise, text="손가락 패턴과 메트로놈이 여기에 표시됩니다.",
                                 bg=PANEL, fg=MUTED, font=("Malgun Gothic", 11),
                                 justify="left", wraplength=520)
    app.details_label.pack(anchor="w")
    beat_row = tk.Frame(exercise, bg=PANEL)
    beat_row.pack(anchor="w", pady=(40, 0))
    app.beat_lights = []
    for index in range(4):
        light = tk.Label(beat_row, text=f"  {index + 1}  ", bg="#35423d", fg=MUTED,
                         font=("Segoe UI", 14, "bold"), pady=8)
        light.pack(side="left", padx=(0, 8))
        app.beat_lights.append(light)
def field(parent, label: str, value: str, side=None):
    group = tk.Frame(parent, bg=PANEL)
    if side:
        group.pack(side=side, fill="x", expand=True,
                   padx=(0, 8) if side == "left" else (8, 0))
    else:
        group.pack(fill="x")
    tk.Label(group, text=label, bg=PANEL, fg=MUTED,
             font=("Malgun Gothic", 10)).pack(anchor="w", pady=(14, 5))
    entry = tk.Entry(group, bg="#273630", fg=TEXT, insertbackground=TEXT,
                     relief="flat", font=("Segoe UI", 12), width=8)
    entry.insert(0, value)
    entry.pack(fill="x", ipady=8)
    return entry


def metric(parent, title: str, value: str, side: str):
    block = tk.Frame(parent, bg=PANEL, padx=18, pady=14)
    block.pack(side=side, fill="x", expand=True,
               padx=(0, 8) if side == "left" else (8, 0))
    tk.Label(block, text=title, bg=PANEL, fg=MUTED,
             font=("Malgun Gothic", 10)).pack(anchor="w")
    label = tk.Label(block, text=value, bg=PANEL, fg=TEXT,
                     font=("Segoe UI", 24, "bold"))
    label.pack(anchor="w", pady=(2, 0))
    return label
