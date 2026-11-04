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

    canvas = tk.Canvas(body, bg=BG, highlightthickness=0, width=320)
    canvas.pack(side="left", fill="y")
    scrollbar = tk.Scrollbar(body, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="left", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-event.delta / 120), "units"))
    canvas.bind_all("<Shift-MouseWheel>", lambda event: canvas.xview_scroll(int(-event.delta / 120), "units"))

    setup = tk.Frame(canvas, bg=PANEL, padx=24, pady=22, width=300)
    canvas.create_window((0, 0), window=setup, anchor="nw", width=300)
    setup.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

    tk.Label(setup, text="SESSION SETUP", bg=PANEL, fg=MINT,
             font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 20))

    app.mode_var = tk.StringVar(value="routine")
    mode_row = tk.Frame(setup, bg=PANEL)
    mode_row.pack(fill="x", pady=(0, 14))
    tk.Label(mode_row, text="연습 모드", bg=PANEL, fg=MUTED,
             font=("Malgun Gothic", 10)).pack(anchor="w", pady=(0, 6))
    mode_frame = tk.Frame(mode_row, bg=PANEL)
    mode_frame.pack(fill="x")
    tk.Radiobutton(mode_frame, text="루틴 개수 모드", variable=app.mode_var, value="routine",
                   bg=PANEL, fg=TEXT, selectcolor=PANEL, activebackground=PANEL,
                   font=("Malgun Gothic", 10)).pack(anchor="w")
    tk.Radiobutton(mode_frame, text="곡 길이 기반 시간 모드", variable=app.mode_var, value="time",
                   bg=PANEL, fg=TEXT, selectcolor=PANEL, activebackground=PANEL,
                   font=("Malgun Gothic", 10)).pack(anchor="w")
    app.session_inputs = [app.routine_count_input, app.repetitions_input,
                          app.level_menu, app.min_bpm, app.max_bpm, mode_frame]

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

    app.time_multiplier_var = tk.StringVar(value="1")
    time_mode_row = tk.Frame(setup, bg=PANEL)
    time_mode_row.pack(fill="x", pady=(16, 0))
    tk.Label(time_mode_row, text="시간 배수", bg=PANEL, fg=MUTED,
             font=("Malgun Gothic", 10)).pack(anchor="w", pady=(0, 6))
    tk.OptionMenu(time_mode_row, app.time_multiplier_var, "1", "2", "3").pack(fill="x")

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

    search_panel = tk.Frame(setup, bg="#1f2d2a", padx=16, pady=16)
    search_panel.pack(fill="x", pady=(18, 0))
    tk.Label(search_panel, text="연습 목표 곡 검색", bg="#1f2d2a", fg=MINT,
             font=("Malgun Gothic", 10, "bold")).pack(anchor="w")
    search_row = tk.Frame(search_panel, bg="#1f2d2a")
    search_row.pack(fill="x", pady=(10, 8))
    app.search_entry = tk.Entry(search_row, bg="#273630", fg=TEXT, insertbackground=TEXT,
                                relief="flat", font=("Segoe UI", 11), width=18)
    app.search_entry.pack(side="left", fill="x", expand=True)
    app.search_button = tk.Button(search_row, text="검색", command=app.search_song,
                                 bg="#34423c", fg=TEXT, activebackground="#45564e",
                                 relief="flat", font=("Malgun Gothic", 9), padx=10,
                                 cursor="hand2")
    app.search_button.pack(side="left", padx=(8, 0))
    app.search_status_label = tk.Label(search_panel, text="곡 제목 또는 가수명으로 검색", bg="#1f2d2a",
                                       fg=MUTED, font=("Malgun Gothic", 9), justify="left")
    app.search_status_label.pack(anchor="w", pady=(0, 8))
    app.search_results = tk.Listbox(search_panel, bg="#273630", fg=TEXT, relief="flat",
                                    height=6, activestyle="none", font=("Malgun Gothic", 9))
    app.search_results.pack(fill="both")
    app.search_results.bind("<<ListboxSelect>>", app.on_search_result_selected)
    app.search_results_data = []

    app.song_length_label = tk.Label(search_panel, text="곡 길이 정보 없음", bg="#1f2d2a",
                                     fg=MUTED, font=("Malgun Gothic", 9), justify="left")
    app.song_length_label.pack(anchor="w", pady=(8, 0))

    app.time_goal_label = tk.Label(search_panel, text="목표 시간: 설정 전", bg="#1f2d2a",
                                   fg=MUTED, font=("Malgun Gothic", 9), justify="left")
    app.time_goal_label.pack(anchor="w", pady=(4, 0))

    app.remaining_time_label = tk.Label(search_panel, text="루틴 모드", bg="#1f2d2a",
                                       fg=MUTED, font=("Malgun Gothic", 9), justify="left")
    app.remaining_time_label.pack(anchor="w", pady=(4, 0))

    bpm_row = tk.Frame(search_panel, bg="#1f2d2a")
    bpm_row.pack(fill="x", pady=(10, 0))
    tk.Label(bpm_row, text="곡 BPM", bg="#1f2d2a", fg=MUTED,
             font=("Malgun Gothic", 10)).pack(anchor="w", pady=(0, 5))
    app.song_bpm_entry = tk.Entry(bpm_row, bg="#273630", fg=TEXT, insertbackground=TEXT,
                                  relief="flat", font=("Segoe UI", 10), width=12)
    app.song_bpm_entry.insert(0, "120")
    app.song_bpm_entry.pack(fill="x")
    app.session_inputs.append(app.song_bpm_entry)

    manual_row = tk.Frame(search_panel, bg="#1f2d2a")
    manual_row.pack(fill="x", pady=(8, 0))
    app.manual_duration_entry = tk.Entry(manual_row, bg="#273630", fg=TEXT, insertbackground=TEXT,
                                         relief="flat", font=("Segoe UI", 10), width=12)
    app.manual_duration_entry.insert(0, "3:20")
    app.manual_duration_entry.pack(side="left", fill="x", expand=True)
    app.session_inputs.append(app.manual_duration_entry)
    tk.Button(manual_row, text="곡 길이 직접 입력", command=app.apply_manual_duration,
              bg="#34423c", fg=TEXT, activebackground="#45564e", relief="flat",
              font=("Malgun Gothic", 9), padx=8, cursor="hand2").pack(side="left", padx=(8, 0))

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

    app.goal_label = tk.Label(exercise, text="연습 목표 곡: 없음",
                             bg=PANEL, fg=MUTED, font=("Malgun Gothic", 11), justify="left",
                             wraplength=520)
    app.goal_label.pack(anchor="w", pady=(18, 0))

    beat_row = tk.Frame(exercise, bg=PANEL)
    beat_row.pack(anchor="w", pady=(24, 0))
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
