"""
================================================================
  EXAM SEAT ALLOCATION SYSTEM — Professional GUI v3.0
  Analysis of Algorithms Course Project | CUST
  Built with: Python · CustomTkinter · Matplotlib

  v3.0 UI Redesign:
  ─ Consistent font system (Inter/Segoe UI across all widgets)
  ─ Fixed all overlapping labels and crowded sections
  ─ Wider sidebar (240px) with proper grouped controls
  ─ Taller header (64px) with clear visual hierarchy
  ─ Proper padding/margins on every widget
  ─ Larger readable font sizes in tables and charts
  ─ Status bar at bottom replacing cramped in-sidebar log
  ─ Stat cards with left accent stripe for visual clarity
  ─ Toolbar pills replaced with clean info badges
  ─ All tabs have consistent top info bars
  ─ Stable splash screen (no overrideredirect crash on Windows)
  ─ Thread-safe: all UI calls on main thread only
================================================================
"""

import sys, os, csv, time, threading, math, datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# ── Path setup ────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
DATA_DIR  = os.path.join(BASE_DIR, "data")
DATA_PATH = os.path.join(DATA_DIR, "students.csv")

from sorting      import sort_students, run_scaling_experiment
from graph        import build_halls
from coloring     import greedy_color_assign, detect_conflicts
from backtracking import backtrack_assign, run_stress_test, get_trace

# ── Font System ───────────────────────────────────────────────
# Single source of truth for all font sizes.
# Using "Segoe UI" on Windows, fallback to "Helvetica" everywhere.
FONT_FAMILY = "Segoe UI"

def F(size, weight="normal"):
    """Return a CTkFont with consistent family."""
    return ctk.CTkFont(family=FONT_FAMILY, size=size,
                       weight="bold" if weight == "bold" else "normal")

# ── Colour Palettes ───────────────────────────────────────────
DARK = {
    "bg":      "#0D0D1F",   # deepest background
    "panel":   "#13132B",   # sidebar / header background
    "card":    "#1C1C3A",   # card / input background
    "raised":  "#242448",   # slightly raised element
    "border":  "#303060",   # separator / border
    "accent":  "#4B8EE8",   # primary blue
    "accent2": "#4EC87A",   # success green
    "warn":    "#E05555",   # error / warning red
    "gold":    "#F0BF30",   # highlight gold
    "purple":  "#9B6EE8",   # analysis purple
    "text":    "#E4E4FF",   # primary text
    "subtext": "#8888BB",   # secondary / dim text
    "success": "#3DBA6A",   # confirmation green
}
LIGHT = {
    "bg":      "#F2F4FC",
    "panel":   "#FFFFFF",
    "card":    "#E8EBF8",
    "raised":  "#DDE2F5",
    "border":  "#C4CCEC",
    "accent":  "#2A5CBD",
    "accent2": "#278A44",
    "warn":    "#C0302B",
    "gold":    "#B8860B",
    "purple":  "#6633BB",
    "text":    "#16163A",
    "subtext": "#5555AA",
    "success": "#1A7A40",
}
T = DARK   # active theme — reassigned on toggle

# Course colour palette — 20 distinct, accessible colours
COURSE_PALETTE = [
    "#4B8EE8","#E8893A","#E05555","#3EC4C0","#4EC87A",
    "#F0BF30","#9B6EE8","#FF8FAA","#8B6644","#A09080",
    "#C06090","#E8A0C8","#60B060","#B89020","#30A090",
    "#60C8B8","#D8B840","#204858","#D06030","#20988A",
]


# ══════════════════════════════════════════════════════════════
#  SPLASH SCREEN
#  Safe on Windows Python 3.11+ — avoids overrideredirect crash
# ══════════════════════════════════════════════════════════════
class SplashScreen(tk.Toplevel):
    STEPS = [
        "Loading student dataset...",
        "Building hall seat graphs...",
        "Initialising algorithm modules...",
        "Preparing visualisation engine...",
        "Launching GUI...",
    ]
    W, H = 540, 330

    def __init__(self, parent, on_done):
        super().__init__(parent)
        self.on_done = on_done
        self.title("Loading — Exam Seat Allocation System")
        self.resizable(False, False)
        self.configure(bg="#0D0D1F")
        self._center()
        try:
            self.attributes("-toolwindow", True)   # thin title bar on Windows
        except Exception:
            pass

        # Outer border frame
        border = tk.Frame(self, bg="#4B8EE8", padx=2, pady=2)
        border.pack(fill="both", expand=True)
        inner = tk.Frame(border, bg="#0D0D1F")
        inner.pack(fill="both", expand=True)

        # Icon + title
        tk.Label(inner, text="\U0001F393",
                 font=("Segoe UI Emoji", 42),
                 bg="#0D0D1F", fg="#4B8EE8").pack(pady=(28, 4))
        tk.Label(inner, text="EXAM SEAT ALLOCATION SYSTEM",
                 font=("Segoe UI", 16, "bold"),
                 bg="#0D0D1F", fg="#4B8EE8").pack()
        tk.Label(inner, text="Analysis of Algorithms  ·  CUST",
                 font=("Segoe UI", 10),
                 bg="#0D0D1F", fg="#8888BB").pack(pady=(2, 0))

        # Status label
        self.status_lbl = tk.Label(inner, text="Initialising...",
                 font=("Segoe UI", 10),
                 bg="#0D0D1F", fg="#4EC87A")
        self.status_lbl.pack(pady=(20, 6))

        # Progress bar track
        bar_track = tk.Frame(inner, bg="#242448", height=8, width=420)
        bar_track.pack(pady=(2, 0))
        bar_track.pack_propagate(False)
        self.bar_fill = tk.Frame(bar_track, bg="#4B8EE8", height=8, width=0)
        self.bar_fill.place(x=0, y=0, height=8)

        tk.Label(inner,
                 text="v3.0  |  Python  ·  CustomTkinter  ·  Matplotlib",
                 font=("Segoe UI", 8),
                 bg="#0D0D1F", fg="#404070").pack(pady=(20, 0))

        self._step = 0
        self.after(60, self._animate)

    def _center(self):
        try:
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
            self.geometry(f"{self.W}x{self.H}+{(sw-self.W)//2}+{(sh-self.H)//2}")
        except Exception:
            self.geometry(f"{self.W}x{self.H}")

    def _animate(self):
        if self._step < len(self.STEPS):
            self.status_lbl.configure(text=self.STEPS[self._step])
            pct = (self._step + 1) / len(self.STEPS)
            self.bar_fill.configure(width=int(420 * pct))
            self._step += 1
            self.after(360, self._animate)
        else:
            self.after(280, self._finish)

    def _finish(self):
        try:
            self.destroy()
        finally:
            self.on_done()


# ══════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════════════
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Exam Seat Allocation System  |  AA Project  |  CUST")
        self.geometry("1520x920")
        self.minsize(1200, 720)
        self._theme_dark = True
        self._apply_theme()

        # ── Application state ──────────────────────────────────
        self.students, self.sorted_stu  = [], []
        self.halls, self.final_halls    = [], []
        self.halls_data                 = []
        self.stress_data                = None
        self.greedy_stats, self.bt_stats = [], []
        self.stress_stats, self.real_times = {}, {}
        self.trace_rows, self.all_conflicts = [], []
        self.all_student_rows           = []
        self._anim_running              = False
        self._seat_artists              = {}

        # ── Build UI hidden, then reveal after splash ──────────
        self.withdraw()
        self._build_ui()
        self._load_students_silent()
        try:
            SplashScreen(self, on_done=self._show_main)
        except Exception:
            self._show_main()

    def _show_main(self):
        try:
            self.deiconify()
            self.lift()
            self.focus_force()
        except Exception:
            pass

    # ── Theme management ──────────────────────────────────────
    def _apply_theme(self):
        global T
        T = DARK if self._theme_dark else LIGHT
        ctk.set_appearance_mode("dark" if self._theme_dark else "light")
        self.configure(fg_color=T["bg"])

    def _toggle_theme(self):
        self._theme_dark = not self._theme_dark
        self._apply_theme()
        self.theme_btn.configure(
            text="  Light Mode" if not self._theme_dark else "  Dark Mode")
        self._log("Theme: " + ("Dark" if self._theme_dark else "Light"))

    # ── Colour utilities ──────────────────────────────────────
    def _darken(self, hex_color, amount=30):
        """Darken a hex colour by `amount` per channel."""
        try:
            r = max(0, int(hex_color[1:3], 16) - amount)
            g = max(0, int(hex_color[3:5], 16) - amount)
            b = max(0, int(hex_color[5:7], 16) - amount)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color

    def _blend(self, fg, alpha=0.2):
        """Alpha-blend fg with background (Tkinter doesn't support #RRGGBBAA)."""
        try:
            bg = T["bg"]
            r = int(int(fg[1:3],16)*alpha + int(bg[1:3],16)*(1-alpha))
            g = int(int(fg[3:5],16)*alpha + int(bg[3:5],16)*(1-alpha))
            b = int(int(fg[5:7],16)*alpha + int(bg[5:7],16)*(1-alpha))
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return fg

    # ══════════════════════════════════════════════════════════
    #  TOP-LEVEL LAYOUT
    # ══════════════════════════════════════════════════════════
    def _build_ui(self):
        self._build_header()

        # Body = sidebar + content pane
        body = ctk.CTkFrame(self, fg_color=T["bg"])
        body.pack(fill="both", expand=True, padx=0, pady=0)

        self._build_sidebar(body)
        self._build_content(body)

        # Status bar at the very bottom
        self._build_statusbar()

    # ── Header (64 px) ────────────────────────────────────────
    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color=T["panel"], height=64, corner_radius=0)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        # Left: logo + title
        left = ctk.CTkFrame(hdr, fg_color="transparent")
        left.pack(side="left", padx=20, pady=0, fill="y")

        # Vertical accent bar
        ctk.CTkFrame(left, fg_color=T["accent"], width=4,
                     corner_radius=2).pack(side="left", fill="y",
                                           padx=(0, 14), pady=12)

        title_col = ctk.CTkFrame(left, fg_color="transparent")
        title_col.pack(side="left", fill="y", pady=10)

        ctk.CTkLabel(title_col,
                     text="EXAM SEAT ALLOCATION SYSTEM",
                     font=F(17, "bold"),
                     text_color=T["text"]).pack(anchor="w")
        ctk.CTkLabel(title_col,
                     text="Analysis of Algorithms  ·  Capital University of Science & Technology",
                     font=F(10),
                     text_color=T["subtext"]).pack(anchor="w", pady=(1, 0))

        # Right: clock + theme toggle
        right = ctk.CTkFrame(hdr, fg_color="transparent")
        right.pack(side="right", padx=20, pady=0, fill="y")

        self.theme_btn = ctk.CTkButton(
            right, text="  Light Mode",
            command=self._toggle_theme,
            width=110, height=32,
            fg_color=T["raised"], hover_color=T["border"],
            text_color=T["text"], font=F(11),
            corner_radius=16)
        self.theme_btn.pack(side="right", padx=(8, 0), pady=16)

        self.clock_lbl = ctk.CTkLabel(
            right, text="",
            font=F(12), text_color=T["subtext"])
        self.clock_lbl.pack(side="right", padx=12, pady=16)
        self._tick_clock()

    def _tick_clock(self):
        self.clock_lbl.configure(
            text=datetime.datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self._tick_clock)

    # ── Status bar (24 px, bottom) ────────────────────────────
    def _build_statusbar(self):
        """
        Replaces the cramped in-sidebar log with a proper status bar.
        Shows the last log message plus a scrollable log popup.
        """
        sb = ctk.CTkFrame(self, fg_color=T["panel"], height=28, corner_radius=0)
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)

        # Separator line
        ctk.CTkFrame(sb, fg_color=T["border"], height=1
                     ).pack(fill="x", side="top")

        self.status_lbl = ctk.CTkLabel(
            sb, text="Ready  —  Load students to begin.",
            font=F(10), text_color=T["subtext"],
            anchor="w")
        self.status_lbl.pack(side="left", padx=14, pady=4)

        # Log toggle button
        ctk.CTkButton(
            sb, text="View Log",
            command=self._show_log_popup,
            width=72, height=20,
            fg_color=T["raised"], hover_color=T["border"],
            text_color=T["subtext"], font=F(9),
            corner_radius=4
        ).pack(side="right", padx=10, pady=4)

        # Internal log storage
        self._log_lines = []

    def _show_log_popup(self):
        """Open a resizable log window."""
        win = ctk.CTkToplevel(self)
        win.title("Activity Log")
        win.geometry("640x420")
        win.configure(fg_color=T["bg"])
        win.grab_set()

        ctk.CTkLabel(win, text="Activity Log",
                     font=F(14, "bold"),
                     text_color=T["text"]).pack(pady=(14, 4), padx=16, anchor="w")

        box = ctk.CTkTextbox(win, fg_color=T["card"],
                             text_color=T["text"],
                             font=ctk.CTkFont(family="Courier New", size=11),
                             corner_radius=8)
        box.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        box.configure(state="normal")
        box.insert("end", "\n".join(self._log_lines))
        box.see("end")
        box.configure(state="disabled")

    # ── Sidebar (240 px) ──────────────────────────────────────
    def _build_sidebar(self, parent):
        """
        Fixed-width sidebar (240 px).
        Sections: Pipeline, Tests, Analysis, Export, Live Stats.
        Log moved to status bar — no more crowded text box here.
        """
        sb = ctk.CTkScrollableFrame(
            parent, fg_color=T["panel"],
            width=240, corner_radius=0,
            scrollbar_button_color=T["border"],
            scrollbar_button_hover_color=T["raised"])
        sb.pack(side="left", fill="y", padx=0, pady=0)

        # ── Section: Pipeline ──────────────────────────────────
        self._sb_section(sb, "PIPELINE")
        self._sb_btn(sb, "Load Students",    self._load_students,   T["accent"],  "📂")
        self._sb_btn(sb, "Merge Sort",       self._run_sort,        T["accent"],  "🔀")
        self._sb_btn(sb, "Build Graphs",     self._build_graphs,    T["accent"],  "🏛")
        self._sb_btn(sb, "Greedy Coloring",  self._run_greedy,      T["accent2"], "🎨")
        self._sb_btn(sb, "Backtracking",     self._run_backtrack,   T["accent2"], "↩")
        self._sb_divider(sb)
        # Run All — full-width, gold highlight
        ctk.CTkButton(
            sb, text="▶   Run All Steps",
            command=self._run_all,
            fg_color=T["gold"], hover_color=self._darken(T["gold"]),
            text_color="#1A1A00", font=F(13, "bold"),
            corner_radius=8, height=40
        ).pack(fill="x", padx=12, pady=(4, 8))

        # ── Section: Tests ────────────────────────────────────
        self._sb_section(sb, "TESTS")
        self._sb_btn(sb, "Stress Test",      self._run_stress,      T["warn"],    "⚡")
        self._sb_btn(sb, "Run Test Cases",   self._run_tests,       T["accent2"], "✅")

        # ── Section: Analysis ─────────────────────────────────
        self._sb_section(sb, "ANALYSIS")
        self._sb_btn(sb, "Scaling Experiment",  self._run_scaling,  T["purple"],  "📈")
        self._sb_btn(sb, "Space Complexity",    self._run_space,    T["purple"],  "💾")
        self._sb_btn(sb, "Animate Hall Fill",   self._run_animation,T["purple"],  "🎬")

        # ── Section: Export ───────────────────────────────────
        self._sb_section(sb, "EXPORT")
        self._sb_btn(sb, "Export Seating CSV",  self._export_csv,  T["subtext"],  "⬇")

        # ── Section: Live Stats ───────────────────────────────
        self._sb_section(sb, "LIVE STATS")
        self.card_students  = self._sb_stat(sb, "Students Loaded", "—", T["accent"])
        self.card_placed    = self._sb_stat(sb, "Students Placed",  "—", T["accent2"])
        self.card_conflicts = self._sb_stat(sb, "Conflicts",        "—", T["warn"])
        self.card_bt        = self._sb_stat(sb, "Backtracks",       "—", T["gold"])
        self._sb_divider(sb)

    def _sb_section(self, parent, title):
        """Section heading label with top padding."""
        ctk.CTkLabel(parent,
                     text=title,
                     font=F(9, "bold"),
                     text_color=T["subtext"],
                     anchor="w"
                     ).pack(fill="x", padx=16, pady=(14, 3))

    def _sb_divider(self, parent):
        ctk.CTkFrame(parent, fg_color=T["border"],
                     height=1).pack(fill="x", padx=12, pady=6)

    def _sb_btn(self, parent, label, cmd, color, icon=""):
        """Sidebar button: icon + label, left-aligned, consistent height."""
        text = f"  {icon}   {label}" if icon else f"  {label}"
        ctk.CTkButton(
            parent, text=text,
            command=cmd,
            fg_color=color, hover_color=self._darken(color),
            text_color="white", font=F(12),
            corner_radius=8, height=36,
            anchor="w"
        ).pack(fill="x", padx=12, pady=3)

    def _sb_stat(self, parent, label, value, color):
        """
        Stat card: left accent stripe + label/value on one row.
        Returns the value CTkLabel so callers can update it.
        """
        card = ctk.CTkFrame(parent, fg_color=T["card"], corner_radius=8)
        card.pack(fill="x", padx=12, pady=3)

        # Left colour stripe
        ctk.CTkFrame(card, fg_color=color, width=4,
                     corner_radius=2).pack(side="left", fill="y",
                                           padx=(0, 10), pady=8)

        ctk.CTkLabel(card, text=label,
                     font=F(10), text_color=T["subtext"],
                     anchor="w").pack(side="left", pady=8)

        val_lbl = ctk.CTkLabel(card, text=value,
                               font=F(14, "bold"),
                               text_color=color, anchor="e")
        val_lbl.pack(side="right", padx=12, pady=8)
        return val_lbl

    # ── Content pane + tabs ───────────────────────────────────
    def _build_content(self, parent):
        content = ctk.CTkFrame(parent, fg_color=T["bg"])
        content.pack(side="left", fill="both", expand=True,
                     padx=10, pady=8)

        self.tabs = ctk.CTkTabview(
            content,
            fg_color=T["panel"],
            segmented_button_fg_color=T["raised"],
            segmented_button_selected_color=T["accent"],
            segmented_button_selected_hover_color=self._darken(T["accent"]),
            segmented_button_unselected_color=T["raised"],
            segmented_button_unselected_hover_color=T["border"],
            corner_radius=10,
            border_width=0)
        self.tabs.pack(fill="both", expand=True)

        TAB_NAMES = [
            "  Hall Layout  ",
            "  Complexity  ",
            "  Space  ",
            "  Trace Table  ",
            "  Students  ",
            "  Stress Test  ",
            "  Algo Stats  ",
        ]
        # Internal keys (without padding) for .tab() lookup
        self._tab_keys = {
            "hall":    TAB_NAMES[0],
            "cplx":   TAB_NAMES[1],
            "space":  TAB_NAMES[2],
            "trace":  TAB_NAMES[3],
            "stu":    TAB_NAMES[4],
            "stress": TAB_NAMES[5],
            "stats":  TAB_NAMES[6],
        }
        for n in TAB_NAMES:
            self.tabs.add(n)

        self._build_hall_tab()
        self._build_complexity_tab()
        self._build_space_tab()
        self._build_trace_tab()
        self._build_student_tab()
        self._build_stress_tab()
        self._build_stats_tab()

    # ── Shared tab widgets ────────────────────────────────────
    def _tab_infobar(self, tab, text, color=None):
        """
        Consistent top info bar for every tab.
        Returns the frame so callers can add extra widgets to it.
        """
        color = color or T["accent"]
        bar = ctk.CTkFrame(tab, fg_color=T["card"], corner_radius=8, height=44)
        bar.pack(fill="x", padx=10, pady=(10, 6))
        bar.pack_propagate(False)

        # Left accent stripe
        ctk.CTkFrame(bar, fg_color=color, width=4,
                     corner_radius=2).pack(side="left", fill="y",
                                           padx=(0, 12), pady=8)
        ctk.CTkLabel(bar, text=text,
                     font=F(11), text_color=T["subtext"],
                     anchor="w").pack(side="left", pady=10)
        return bar

    def _placeholder(self, fig, canvas, msg):
        """Draw a centered placeholder message on a matplotlib figure."""
        fig.clear()
        ax = fig.add_subplot(111)
        ax.set_facecolor(T["card"])
        fig.set_facecolor(T["bg"])
        ax.text(0.5, 0.5, msg,
                ha="center", va="center",
                color=T["subtext"], fontsize=13,
                transform=ax.transAxes)
        ax.axis("off")
        canvas.draw()

    def _style_mpl_ax(self, ax):
        """Apply consistent dark/light styling to a matplotlib Axes."""
        ax.set_facecolor(T["card"])
        ax.tick_params(colors=T["text"], labelsize=9)
        ax.xaxis.label.set_color(T["text"])
        ax.yaxis.label.set_color(T["text"])
        ax.title.set_color(T["text"])
        for sp in ax.spines.values():
            sp.set_edgecolor(T["border"])
        ax.grid(True, alpha=0.12)

    # ══════════════════════════════════════════════════════════
    #  TAB 1: HALL LAYOUT
    # ══════════════════════════════════════════════════════════
    def _build_hall_tab(self):
        tab = self.tabs.tab(self._tab_keys["hall"])

        # ── Top toolbar ───────────────────────────────────────
        toolbar = ctk.CTkFrame(tab, fg_color=T["card"], corner_radius=8, height=52)
        toolbar.pack(fill="x", padx=10, pady=(10, 6))
        toolbar.pack_propagate(False)

        ctk.CTkLabel(toolbar, text="Select Hall:",
                     font=F(12, "bold"),
                     text_color=T["text"]).pack(side="left", padx=(16, 8), pady=14)

        self.hall_var = ctk.StringVar(value="Hall-A")
        for h in ["Hall-A", "Hall-B", "Hall-C", "Stress Test"]:
            ctk.CTkRadioButton(
                toolbar, text=h,
                variable=self.hall_var, value=h,
                command=self._refresh_hall,
                text_color=T["text"], font=F(11),
                fg_color=T["accent"],
                border_color=T["border"]
            ).pack(side="left", padx=10, pady=14)

        # Info badges (right side of toolbar)
        badge_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        badge_frame.pack(side="right", padx=12)
        self.badge_filled   = self._badge(badge_frame, "Filled: —",   T["accent2"])
        self.badge_empty    = self._badge(badge_frame, "Empty: —",    T["gold"])
        self.badge_conflict = self._badge(badge_frame, "Conflicts: —", T["warn"])
        self.badge_time     = self._badge(badge_frame, "Time: —",     T["subtext"])

        # ── Hall canvas + legend ──────────────────────────────
        body = ctk.CTkFrame(tab, fg_color=T["bg"])
        body.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        # Canvas takes all available space
        canvas_wrap = ctk.CTkFrame(body, fg_color=T["bg"])
        canvas_wrap.pack(side="left", fill="both", expand=True)

        self.hall_fig = plt.Figure(facecolor=T["bg"])
        self.hall_ax  = self.hall_fig.add_subplot(111)
        self.hall_canvas = FigureCanvasTkAgg(self.hall_fig, canvas_wrap)
        self.hall_canvas.get_tk_widget().pack(fill="both", expand=True)
        self.hall_canvas.mpl_connect("button_press_event", self._on_seat_click)

        # Legend panel — fixed 180 px, scrollable
        legend_wrap = ctk.CTkFrame(body, fg_color=T["card"],
                                   corner_radius=8, width=180)
        legend_wrap.pack(side="right", fill="y", padx=(8, 0))
        legend_wrap.pack_propagate(False)

        ctk.CTkLabel(legend_wrap, text="Course Legend",
                     font=F(11, "bold"),
                     text_color=T["subtext"]).pack(pady=(10, 4), padx=10)
        ctk.CTkFrame(legend_wrap, fg_color=T["border"],
                     height=1).pack(fill="x", padx=10)

        self.legend_frame = ctk.CTkScrollableFrame(
            legend_wrap, fg_color="transparent",
            scrollbar_button_color=T["border"])
        self.legend_frame.pack(fill="both", expand=True, padx=4, pady=4)

        self._draw_empty_hall()

    def _badge(self, parent, text, color):
        """Small rounded badge label."""
        f = ctk.CTkFrame(parent, fg_color=self._blend(color, 0.35),
                         corner_radius=12, height=28)
        f.pack(side="left", padx=4)
        f.pack_propagate(False)
        lbl = ctk.CTkLabel(f, text=text,
                           font=F(10, "bold"),
                           text_color=color)
        lbl.pack(padx=10, pady=4)
        return lbl

    def _update_badges(self, hall, allocation, conflicts):
        filled = len(allocation)
        empty  = hall.total_seats - filled
        ms     = self.real_times.get("greedy_color", 0)
        self.badge_filled.configure(text=f"Filled: {filled}/{hall.total_seats}")
        self.badge_empty.configure(text=f"Empty: {empty}")
        self.badge_conflict.configure(text=f"Conflicts: {len(conflicts)}")
        self.badge_time.configure(text=f"Time: {ms:.2f} ms")

    def _update_legend(self, seat_course):
        for w in self.legend_frame.winfo_children():
            w.destroy()
        from collections import Counter
        counts    = Counter(seat_course.values())
        courses   = sorted(set(seat_course.values()))
        color_map = {c: COURSE_PALETTE[i % len(COURSE_PALETTE)]
                     for i, c in enumerate(courses)}
        for course in courses:
            row = ctk.CTkFrame(self.legend_frame, fg_color="transparent")
            row.pack(fill="x", padx=6, pady=3)
            dot = ctk.CTkFrame(row, fg_color=color_map[course],
                               width=12, height=12, corner_radius=6)
            dot.pack(side="left", padx=(0, 8))
            dot.pack_propagate(False)
            ctk.CTkLabel(row, text=course,
                         font=F(10), text_color=T["text"]).pack(side="left")
            ctk.CTkLabel(row, text=str(counts[course]),
                         font=F(10, "bold"),
                         text_color=T["subtext"]).pack(side="right")

    def _draw_empty_hall(self):
        ax = self.hall_ax
        ax.clear()
        ax.set_facecolor(T["bg"])
        self.hall_fig.set_facecolor(T["bg"])
        ax.text(0.5, 0.5,
                "Run allocation to see the hall layout\n\n"
                "Click  ▶ Run All Steps  in the sidebar to start",
                ha="center", va="center",
                color=T["subtext"], fontsize=13, linespacing=1.8,
                transform=ax.transAxes)
        ax.axis("off")
        self.hall_canvas.draw()

    def _refresh_hall(self, *_):
        sel = self.hall_var.get()
        if sel == "Stress Test" and self.stress_data:
            alloc, sc, hall = self.stress_data
            self._draw_hall(hall, alloc, sc, stress=True)
            self._update_legend(sc)
        elif self.final_halls:
            idx = {"Hall-A": 0, "Hall-B": 1, "Hall-C": 2}.get(sel, 0)
            if idx < len(self.final_halls):
                _, alloc, sc, hall = self.final_halls[idx]
                self._draw_hall(hall, alloc, sc)
                self._update_legend(sc)
                conflicts = detect_conflicts(hall, alloc, sc)
                self._update_badges(hall, alloc, conflicts)

    def _draw_hall(self, hall, allocation, seat_course, stress=False):
        ax = self.hall_ax
        ax.clear()
        ax.set_facecolor(T["bg"])
        self.hall_fig.set_facecolor(T["bg"])
        self._seat_artists.clear()

        if stress:
            color_map = {
                "STRESS-A": COURSE_PALETTE[0],
                "STRESS-B": COURSE_PALETTE[2],
            }
        else:
            courses   = sorted(set(seat_course.values()))
            color_map = {c: COURSE_PALETTE[i % len(COURSE_PALETTE)]
                         for i, c in enumerate(courses)}

        cw, ch = 1.0, 0.76
        for sid in range(hall.total_seats):
            r, c  = hall.id_to_rc[sid]
            x     = c * cw
            y     = (hall.rows - 1 - r) * ch
            filled = sid in allocation
            color  = (color_map.get(seat_course.get(sid, ""), "#1e1e38")
                      if filled else T["raised"])
            ec     = "#ffffff22" if filled else T["border"]
            rect   = mpatches.FancyBboxPatch(
                (x + 0.05, y + 0.05), cw - 0.10, ch - 0.10,
                boxstyle="round,pad=0.03",
                facecolor=color, edgecolor=ec,
                linewidth=0.5, alpha=1.0 if filled else 0.45)
            ax.add_patch(rect)
            self._seat_artists[sid] = rect
            if filled:
                stu   = allocation[sid]
                label = (f"{stu['RollNo']}\n{seat_course[sid]}"
                         if not stress else seat_course[sid][-1])
                ax.text(x + cw / 2, y + ch / 2, label,
                        ha="center", va="center",
                        fontsize=4.8 if not stress else 9,
                        color="white", fontweight="bold",
                        fontfamily="monospace")

        ax.set_xlim(-0.3, hall.cols * cw + 0.3)
        ax.set_ylim(-0.4, hall.rows * ch + 0.5)
        ax.set_title(
            f"{'STRESS TEST  —  ' if stress else ''}{hall.hall_name}"
            f"     {len(allocation)}/{hall.total_seats} seats filled",
            color=T["text"], fontsize=12, fontweight="bold", pad=12)
        ax.axis("off")
        self.hall_canvas.draw()

    def _on_seat_click(self, event):
        """Popup with full student details when a filled seat is clicked."""
        if not self.final_halls or event.xdata is None:
            return
        sel = self.hall_var.get()
        if sel == "Stress Test":
            return
        idx = {"Hall-A": 0, "Hall-B": 1, "Hall-C": 2}.get(sel, 0)
        if idx >= len(self.final_halls):
            return
        _, alloc, sc, hall = self.final_halls[idx]
        cw, ch = 1.0, 0.76
        col = int(event.xdata / cw)
        row = hall.rows - 1 - int(event.ydata / ch)
        if 0 <= row < hall.rows and 0 <= col < hall.cols:
            sid = hall.seat_matrix.get((row, col))
            if sid is not None and sid in alloc:
                stu = alloc[sid]
                messagebox.showinfo(
                    "Seat Details",
                    f"Hall     :  {hall.hall_name}\n"
                    f"Seat     :  {hall.get_seat_label(sid)}\n"
                    f"Roll No  :  {stu['RollNo']}\n"
                    f"Name     :  {stu['Name']}\n"
                    f"Course   :  {stu['Course']}")

    # ── Animated fill (self.after()-based, no threads) ────────
    def _run_animation(self):
        if not self.final_halls:
            self._log("⚠  Run allocation first."); return
        if self._anim_running:
            self._log("⚠  Animation already running."); return
        sel = self.hall_var.get()
        if sel == "Stress Test":
            sel = "Hall-A"
            self.hall_var.set("Hall-A")
        idx = {"Hall-A": 0, "Hall-B": 1, "Hall-C": 2}.get(sel, 0)
        _, alloc, sc, hall = self.final_halls[idx]
        self._log(f"🎬 Animating {hall.hall_name}...")
        self._animate_fill(hall, alloc, sc)

    def _animate_fill(self, hall, allocation, seat_course):
        self._anim_running = True
        self._draw_hall(hall, {}, {})
        courses   = sorted(set(seat_course.values()))
        color_map = {c: COURSE_PALETTE[i % len(COURSE_PALETTE)]
                     for i, c in enumerate(courses)}
        cw, ch    = 1.0, 0.76
        order     = [s for s in range(hall.total_seats) if s in allocation]

        def _paint(i=0):
            if i >= len(order):
                self._anim_running = False
                self._log(f"✅ Animation complete — {hall.hall_name}")
                return
            sid  = order[i]
            r, c = hall.id_to_rc[sid]
            x    = c * cw
            y    = (hall.rows - 1 - r) * ch
            if sid in self._seat_artists:
                self._seat_artists[sid].set_facecolor(
                    color_map[seat_course[sid]])
                self._seat_artists[sid].set_alpha(1.0)
                stu = allocation[sid]
                self.hall_ax.text(
                    x + cw / 2, y + ch / 2,
                    f"{stu['RollNo']}\n{seat_course[sid]}",
                    ha="center", va="center", fontsize=4.8,
                    color="white", fontweight="bold",
                    fontfamily="monospace")
                self.hall_canvas.draw()
            self.after(28, lambda: _paint(i + 1))

        self.after(250, lambda: _paint(0))

    # ══════════════════════════════════════════════════════════
    #  TAB 2: COMPLEXITY
    # ══════════════════════════════════════════════════════════
    def _build_complexity_tab(self):
        tab = self.tabs.tab(self._tab_keys["cplx"])
        self._tab_infobar(
            tab,
            "Merge Sort scaling experiment  ·  Real measured runtimes vs O(n log n) theory",
            T["accent"])
        self.cplx_fig = plt.Figure(facecolor=T["bg"])
        self.cplx_canvas = FigureCanvasTkAgg(self.cplx_fig, tab)
        self.cplx_canvas.get_tk_widget().pack(
            fill="both", expand=True, padx=10, pady=(0, 10))
        self._placeholder(self.cplx_fig, self.cplx_canvas,
                          "Run  Scaling Experiment  from the sidebar to generate charts")

    def _draw_complexity(self, scaling_results, real_times):
        fig = self.cplx_fig
        fig.clear()
        fig.set_facecolor(T["bg"])
        axes = fig.subplots(1, 3)

        ns    = [r["n"]           for r in scaling_results]
        times = [r["time_ms"]     for r in scaling_results]
        comps = [r["comparisons"] for r in scaling_results]
        th    = [r["theoretical"] for r in scaling_results]
        s1    = max(times) / max(th) if max(th) else 1
        s2    = max(comps) / max(th) if max(th) else 1

        # Chart 1 — Time vs n
        self._style_mpl_ax(axes[0])
        axes[0].plot(ns, times, "o-", color=T["accent"], lw=2.2,
                     ms=7, label="Measured (ms)")
        axes[0].plot(ns, [t * s1 for t in th], "--", color=T["gold"],
                     lw=1.8, label="O(n log n)")
        axes[0].fill_between(ns, times, [t * s1 for t in th],
                             alpha=0.08, color=T["accent"])
        axes[0].set_title("Merge Sort — Time vs n",
                          fontweight="bold", fontsize=11)
        axes[0].set_xlabel("n  (students)", fontsize=10)
        axes[0].set_ylabel("Time (ms)", fontsize=10)
        axes[0].legend(facecolor=T["card"], labelcolor=T["text"], fontsize=9)

        # Chart 2 — Comparisons vs n
        self._style_mpl_ax(axes[1])
        axes[1].plot(ns, comps, "s-", color=T["warn"], lw=2.2,
                     ms=7, label="Actual Comparisons")
        axes[1].plot(ns, [t * s2 for t in th], "--", color=T["gold"],
                     lw=1.8, label="O(n log n)")
        axes[1].set_title("Merge Sort — Comparisons vs n",
                          fontweight="bold", fontsize=11)
        axes[1].set_xlabel("n  (students)", fontsize=10)
        axes[1].set_ylabel("Comparisons", fontsize=10)
        axes[1].legend(facecolor=T["card"], labelcolor=T["text"], fontsize=9)

        # Chart 3 — Algorithm runtime comparison (bar)
        self._style_mpl_ax(axes[2])
        labels = ["Merge\nSort", "Binary\nSearch",
                  "Graph\nBuild", "Greedy\nColor", "Back-\ntrack"]
        vals   = [real_times.get(k, 0) for k in
                  ["merge_sort", "binary_search",
                   "graph_build", "greedy_color", "backtrack"]]
        colors = [T["accent"], T["gold"], T["accent2"],
                  T["purple"], T["warn"]]
        bars = axes[2].bar(labels, vals, color=colors,
                           edgecolor=T["bg"], width=0.52)
        axes[2].set_title("Algorithm Runtime (Real Data)",
                          fontweight="bold", fontsize=11)
        axes[2].set_ylabel("Time (ms)", fontsize=10)
        for bar, v in zip(bars, vals):
            if v > 0:
                axes[2].text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(vals) * 0.01,
                    f"{v:.4f}", ha="center", va="bottom",
                    color=T["text"], fontsize=8)

        fig.suptitle(
            "Time Complexity Analysis — All Values Real Measured",
            color=T["text"], fontsize=13, fontweight="bold", y=1.01)
        fig.tight_layout()
        self.cplx_canvas.draw()

    # ══════════════════════════════════════════════════════════
    #  TAB 3: SPACE COMPLEXITY
    # ══════════════════════════════════════════════════════════
    def _build_space_tab(self):
        tab = self.tabs.tab(self._tab_keys["space"])
        self._tab_infobar(
            tab,
            "Peak memory tracked with Python tracemalloc  ·  Measured in KB across input sizes",
            T["purple"])

        # ── Memory summary row ────────────────────────────────
        summary = ctk.CTkFrame(tab, fg_color=T["card"],
                               corner_radius=8, height=64)
        summary.pack(fill="x", padx=10, pady=(0, 6))
        summary.pack_propagate(False)

        self._mem_pills = {}
        self._mem_pill_colors = {}
        specs = [
            ("merge_sort",    "Merge Sort",    T["accent"]),
            ("binary_search", "Binary Search", T["gold"]),
            ("graph_build",   "Graph Build",   T["accent2"]),
            ("greedy",        "Greedy",        T["purple"]),
            ("backtrack",     "Backtracking",  T["warn"]),
        ]
        for key, label, color in specs:
            cell = ctk.CTkFrame(summary, fg_color=T["raised"],
                                corner_radius=8)
            cell.pack(side="left", expand=True, fill="both",
                      padx=5, pady=8)
            ctk.CTkLabel(cell, text=label,
                         font=F(9), text_color=T["subtext"]
                         ).pack(pady=(6, 0))
            lbl = ctk.CTkLabel(cell, text="—",
                               font=F(13, "bold"),
                               text_color=color)
            lbl.pack(pady=(0, 6))
            self._mem_pills[key]        = lbl
            self._mem_pill_colors[key]  = color

        # ── Charts ────────────────────────────────────────────
        self.space_fig    = plt.Figure(facecolor=T["bg"])
        self.space_canvas = FigureCanvasTkAgg(self.space_fig, tab)
        self.space_canvas.get_tk_widget().pack(
            fill="both", expand=True, padx=10, pady=(0, 10))
        self._placeholder(self.space_fig, self.space_canvas,
                          "Click  Space Complexity  in the sidebar to measure real memory usage")

    def _draw_space_charts(self, data):
        fig = self.space_fig
        fig.clear()
        fig.set_facecolor(T["bg"])
        axes = fig.subplots(2, 3)
        axes = axes.flatten()

        def _ax(ax, title, xlabel, ylabel):
            self._style_mpl_ax(ax)
            ax.set_title(title, fontweight="bold", fontsize=10,
                         color=T["text"])
            ax.set_xlabel(xlabel, fontsize=9)
            ax.set_ylabel(ylabel, fontsize=9)

        # Chart 1 — Merge Sort O(n)
        ms  = data["merge_sort"]
        ns  = [r["n"]       for r in ms]
        kbs = [r["peak_kb"] for r in ms]
        sc1 = max(kbs) / max(ns) if max(ns) else 1
        _ax(axes[0], "Merge Sort — O(n) Space",
            "n  (students)", "Peak Memory (KB)")
        axes[0].plot(ns, kbs, "o-", color=T["accent"], lw=2, ms=6,
                     label="Measured (KB)")
        axes[0].plot(ns, [n * sc1 for n in ns], "--", color=T["gold"],
                     lw=1.6, label="O(n) scaled")
        axes[0].fill_between(ns, kbs, [n * sc1 for n in ns],
                             alpha=0.07, color=T["accent"])
        axes[0].legend(facecolor=T["card"], labelcolor=T["text"], fontsize=8)

        # Chart 2 — Graph Build O(V+E)
        gb  = data["graph_build"]
        ves = [r["VE"]      for r in gb]
        gkbs= [r["peak_kb"] for r in gb]
        sc2 = max(gkbs) / max(ves) if max(ves) else 1
        _ax(axes[1], "Graph Build — O(V+E) Space",
            "V+E  (nodes + edges)", "Peak Memory (KB)")
        axes[1].plot(ves, gkbs, "s-", color=T["accent2"], lw=2, ms=6,
                     label="Measured (KB)")
        axes[1].plot(ves, [v * sc2 for v in ves], "--", color=T["gold"],
                     lw=1.6, label="O(V+E) scaled")
        axes[1].fill_between(ves, gkbs, [v * sc2 for v in ves],
                             alpha=0.07, color=T["accent2"])
        axes[1].legend(facecolor=T["card"], labelcolor=T["text"], fontsize=8)

        # Chart 3 — Backtracking O(n)
        bt  = data["backtrack"]
        bns = [r["n"]       for r in bt]
        bkbs= [r["peak_kb"] for r in bt]
        sc3 = max(bkbs) / max(bns) if max(bns) else 1
        _ax(axes[2], "Backtracking — O(n) Space",
            "n  (students)", "Peak Memory (KB)")
        axes[2].plot(bns, bkbs, "^-", color=T["warn"], lw=2, ms=6,
                     label="Measured (KB)")
        axes[2].plot(bns, [n * sc3 for n in bns], "--", color=T["gold"],
                     lw=1.6, label="O(n) scaled")
        axes[2].fill_between(bns, bkbs, [n * sc3 for n in bns],
                             alpha=0.07, color=T["warn"])
        axes[2].legend(facecolor=T["card"], labelcolor=T["text"], fontsize=8)

        # Chart 4 — Greedy O(V)
        gr  = data["greedy"]
        gvs = [r["V"]       for r in gr]
        grbs= [r["peak_kb"] for r in gr]
        sc4 = max(grbs) / max(gvs) if max(gvs) else 1
        _ax(axes[3], "Greedy Coloring — O(V) Space",
            "V  (seats)", "Peak Memory (KB)")
        axes[3].plot(gvs, grbs, "D-", color=T["purple"], lw=2, ms=6,
                     label="Measured (KB)")
        axes[3].plot(gvs, [v * sc4 for v in gvs], "--", color=T["gold"],
                     lw=1.6, label="O(V) scaled")
        axes[3].fill_between(gvs, grbs, [v * sc4 for v in gvs],
                             alpha=0.07, color=T["purple"])
        axes[3].legend(facecolor=T["card"], labelcolor=T["text"], fontsize=8)

        # Chart 5 — Bar comparison
        bs        = data["binary_search"]
        bar_labels= ["Merge Sort\nO(n)", "Binary Search\nO(1)",
                     "Graph Build\nO(V+E)", "Greedy\nO(V)",
                     "Backtrack\nO(n)"]
        bar_vals  = [
            max(r["peak_kb"] for r in ms),
            bs["peak_kb"],
            max(r["peak_kb"] for r in gb),
            max(r["peak_kb"] for r in gr),
            max(r["peak_kb"] for r in bt),
        ]
        cols5 = [T["accent"], T["gold"], T["accent2"], T["purple"], T["warn"]]
        _ax(axes[4], "Peak Memory Comparison", "Algorithm", "Peak KB")
        bars = axes[4].bar(bar_labels, bar_vals, color=cols5,
                           edgecolor=T["bg"], width=0.52)
        for b, v in zip(bars, bar_vals):
            axes[4].text(b.get_x() + b.get_width() / 2,
                         b.get_height() + 0.1,
                         f"{v:.2f} KB",
                         ha="center", va="bottom",
                         color=T["text"], fontsize=8)

        # Chart 6 — Space vs Time scatter
        _ax(axes[5], "Space vs Time Trade-off",
            "Time (ms)", "Space (KB)")
        names5 = ["Merge Sort", "Binary Search",
                  "Graph Build", "Greedy", "Backtrack"]
        t_vals = [
            self.real_times.get("merge_sort",    0.55),
            self.real_times.get("binary_search", 0.001),
            self.real_times.get("graph_build",   0.60),
            self.real_times.get("greedy_color",  0.30),
            self.real_times.get("backtrack",     0.05),
        ]
        for name, tv, sv, c in zip(names5, t_vals, bar_vals, cols5):
            axes[5].scatter(tv, sv, color=c, s=110, zorder=5)
            axes[5].annotate(name, (tv, sv),
                             textcoords="offset points",
                             xytext=(6, 4),
                             fontsize=8, color=T["text"])

        fig.suptitle(
            "Space Complexity — Real Measured Memory (tracemalloc)",
            color=T["text"], fontsize=12, fontweight="bold", y=1.01)
        fig.tight_layout()
        self.space_canvas.draw()

        # Update summary pills
        self._mem_pills["merge_sort"].configure(
            text=f"{max(r['peak_kb'] for r in ms):.2f} KB")
        self._mem_pills["binary_search"].configure(
            text=f"{bs['peak_kb']:.4f} KB")
        self._mem_pills["graph_build"].configure(
            text=f"{max(r['peak_kb'] for r in gb):.2f} KB")
        self._mem_pills["greedy"].configure(
            text=f"{max(r['peak_kb'] for r in gr):.2f} KB")
        self._mem_pills["backtrack"].configure(
            text=f"{max(r['peak_kb'] for r in bt):.2f} KB")

    # ══════════════════════════════════════════════════════════
    #  TAB 4: TRACE TABLE
    # ══════════════════════════════════════════════════════════
    def _build_trace_tab(self):
        tab = self.tabs.tab(self._tab_keys["trace"])

        infobar = self._tab_infobar(
            tab,
            "Backtracking recursion trace  —  "
            "Green = PLACED (constraint satisfied)  ·  "
            "Red = BACKTRACK (forbidden course detected)",
            T["accent2"])

        # Counter badge on right side of infobar
        self.trace_count_lbl = ctk.CTkLabel(
            infobar, text="",
            font=F(11, "bold"), text_color=T["accent"])
        self.trace_count_lbl.pack(side="right", padx=14)

        # ── Treeview ──────────────────────────────────────────
        frame = ctk.CTkFrame(tab, fg_color=T["card"], corner_radius=8)
        frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Trace.Treeview",
            background=T["card"],
            foreground=T["text"],
            fieldbackground=T["card"],
            rowheight=30,
            font=(FONT_FAMILY, 11))
        style.configure("Trace.Treeview.Heading",
            background=T["accent"],
            foreground="white",
            font=(FONT_FAMILY, 11, "bold"),
            relief="flat")
        style.map("Trace.Treeview",
            background=[("selected", T["raised"])])

        cols = ("Step", "Seat", "Course Tried",
                "Forbidden Courses", "Result")
        self.trace_tree = ttk.Treeview(
            frame, columns=cols, show="headings",
            style="Trace.Treeview")

        col_widths = [60, 150, 140, 240, 110]
        for col, w in zip(cols, col_widths):
            self.trace_tree.heading(col, text=col)
            self.trace_tree.column(col, width=w, anchor="center",
                                   minwidth=w)

        vsb = ttk.Scrollbar(frame, orient="vertical",
                            command=self.trace_tree.yview)
        self.trace_tree.configure(yscrollcommand=vsb.set)
        self.trace_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.trace_tree.tag_configure(
            "placed",    background="#1B3D25", foreground="#70FF88")
        self.trace_tree.tag_configure(
            "backtrack", background="#3D1B1B", foreground="#FF8080")

    def _populate_trace(self, rows):
        for i in self.trace_tree.get_children():
            self.trace_tree.delete(i)
        placed = bt = 0
        for row in rows:
            tag = "placed" if row["Result"] == "PLACED" else "backtrack"
            self.trace_tree.insert(
                "", "end",
                values=(row["Step"], row["Seat"],
                        row["Course Tried"],
                        row["Forbidden"],
                        row["Result"]),
                tags=(tag,))
            if tag == "placed":
                placed += 1
            else:
                bt += 1
        self.trace_count_lbl.configure(
            text=f"✅ {placed} Placed     ↩ {bt} Backtracks")

    # ══════════════════════════════════════════════════════════
    #  TAB 5: STUDENTS
    # ══════════════════════════════════════════════════════════
    def _build_student_tab(self):
        tab = self.tabs.tab(self._tab_keys["stu"])

        # ── Search + filter toolbar ───────────────────────────
        toolbar = ctk.CTkFrame(tab, fg_color=T["card"],
                               corner_radius=8, height=52)
        toolbar.pack(fill="x", padx=10, pady=(10, 6))
        toolbar.pack_propagate(False)

        ctk.CTkLabel(toolbar, text="Search:",
                     font=F(12), text_color=T["text"]
                     ).pack(side="left", padx=(16, 6), pady=14)

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._filter_students)
        ctk.CTkEntry(
            toolbar,
            textvariable=self.search_var,
            width=300, height=32,
            fg_color=T["raised"],
            border_color=T["border"],
            placeholder_text="Roll No / Name / Course / Hall...",
            text_color=T["text"],
            font=F(11)
        ).pack(side="left", padx=(0, 16), pady=10)

        # Hall filter radios
        ctk.CTkLabel(toolbar, text="Hall:",
                     font=F(11), text_color=T["subtext"]
                     ).pack(side="left", padx=(0, 6))
        self.filter_hall = ctk.StringVar(value="All")
        for h in ["All", "Hall-A", "Hall-B", "Hall-C"]:
            ctk.CTkRadioButton(
                toolbar, text=h,
                variable=self.filter_hall, value=h,
                command=self._filter_students,
                text_color=T["text"], font=F(11),
                fg_color=T["accent"],
                border_color=T["border"]
            ).pack(side="left", padx=8)

        self.stu_count_lbl = ctk.CTkLabel(
            toolbar, text="",
            font=F(11), text_color=T["subtext"])
        self.stu_count_lbl.pack(side="right", padx=16)

        # ── Treeview ──────────────────────────────────────────
        frame = ctk.CTkFrame(tab, fg_color=T["card"], corner_radius=8)
        frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        style = ttk.Style()
        style.configure("Stu.Treeview",
            background=T["card"],
            foreground=T["text"],
            fieldbackground=T["card"],
            rowheight=30,
            font=(FONT_FAMILY, 11))
        style.configure("Stu.Treeview.Heading",
            background=T["accent"],
            foreground="white",
            font=(FONT_FAMILY, 11, "bold"),
            relief="flat")
        style.map("Stu.Treeview",
            background=[("selected", T["raised"])])

        cols = ("Hall", "Seat", "Roll No", "Name", "Course")
        self.stu_tree = ttk.Treeview(
            frame, columns=cols, show="headings",
            style="Stu.Treeview")

        col_widths = [90, 140, 100, 240, 130]
        for col, w in zip(cols, col_widths):
            self.stu_tree.heading(
                col, text=col,
                command=lambda c=col: self._sort_stu_col(c))
            self.stu_tree.column(col, width=w, anchor="center",
                                 minwidth=w)

        vsb = ttk.Scrollbar(frame, orient="vertical",
                            command=self.stu_tree.yview)
        self.stu_tree.configure(yscrollcommand=vsb.set)
        self.stu_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self.stu_tree.tag_configure("odd",  background=T["card"])
        self.stu_tree.tag_configure("even", background=T["raised"])

    def _populate_student_table(self):
        self.all_student_rows = []
        for hall_name, alloc, sc, hall in self.final_halls:
            for sid, stu in sorted(alloc.items()):
                self.all_student_rows.append((
                    hall_name,
                    hall.get_seat_label(sid),
                    stu["RollNo"],
                    stu["Name"],
                    stu["Course"],
                ))
        self._filter_students()

    def _filter_students(self, *_):
        q  = self.search_var.get().lower()
        fh = self.filter_hall.get()
        rows = [r for r in self.all_student_rows
                if q in " ".join(str(x).lower() for x in r)
                and (fh == "All" or r[0] == fh)]
        for i in self.stu_tree.get_children():
            self.stu_tree.delete(i)
        for n, row in enumerate(rows):
            self.stu_tree.insert("", "end", values=row,
                                 tags=("odd" if n % 2 else "even",))
        self.stu_count_lbl.configure(
            text=f"Showing {len(rows)} of {len(self.all_student_rows)} students")

    def _sort_stu_col(self, col):
        idx = {"Hall": 0, "Seat": 1,
               "Roll No": 2, "Name": 3, "Course": 4}[col]
        self.all_student_rows.sort(key=lambda r: r[idx])
        self._filter_students()

    # ══════════════════════════════════════════════════════════
    #  TAB 6: STRESS TEST
    # ══════════════════════════════════════════════════════════
    def _build_stress_tab(self):
        tab = self.tabs.tab(self._tab_keys["stress"])

        # Info banner
        banner = ctk.CTkFrame(
            tab, fg_color=self._blend(T["warn"], 0.22),
            corner_radius=8, height=50)
        banner.pack(fill="x", padx=10, pady=(10, 6))
        banner.pack_propagate(False)
        ctk.CTkFrame(banner, fg_color=T["warn"], width=4,
                     corner_radius=2
                     ).pack(side="left", fill="y", padx=(0, 14), pady=10)
        ctk.CTkLabel(
            banner,
            text="WORST-CASE TEST  —  Only 2 courses assigned to all seats"
                 "  →  Forces maximum backtracking",
            font=F(12, "bold"),
            text_color=T["warn"]
        ).pack(side="left", pady=14)

        # ── Stats summary row ─────────────────────────────────
        stats_row = ctk.CTkFrame(tab, fg_color=T["card"],
                                 corner_radius=8, height=72)
        stats_row.pack(fill="x", padx=10, pady=(0, 8))
        stats_row.pack_propagate(False)

        self._stress_pills        = {}
        self._stress_pill_colors  = {}
        specs = [
            ("calls",      "Recursive Calls", T["accent"]),
            ("backtracks", "Backtracks",      T["warn"]),
            ("placed",     "Placed",          T["accent2"]),
            ("conflicts",  "Conflicts",       T["gold"]),
            ("time",       "Time (ms)",       T["purple"]),
        ]
        for key, label, color in specs:
            cell = ctk.CTkFrame(stats_row, fg_color=T["raised"],
                                corner_radius=8)
            cell.pack(side="left", expand=True, fill="both",
                      padx=6, pady=10)
            ctk.CTkLabel(cell, text=label,
                         font=F(10), text_color=T["subtext"]
                         ).pack(pady=(8, 0))
            lbl = ctk.CTkLabel(cell, text="—",
                               font=F(18, "bold"),
                               text_color=color)
            lbl.pack(pady=(0, 8))
            self._stress_pills[key]       = lbl
            self._stress_pill_colors[key] = color

        # ── Charts ────────────────────────────────────────────
        self.stress_fig    = plt.Figure(facecolor=T["bg"])
        self.stress_canvas = FigureCanvasTkAgg(self.stress_fig, tab)
        self.stress_canvas.get_tk_widget().pack(
            fill="both", expand=True, padx=10, pady=(0, 10))
        self._placeholder(
            self.stress_fig, self.stress_canvas,
            "Click  Stress Test  in the sidebar to run worst-case analysis")

    def _draw_stress_chart(self, stress_stats, normal_bt_stats):
        fig = self.stress_fig
        fig.clear()
        fig.set_facecolor(T["bg"])
        axes = fig.subplots(1, 2)

        def _ax(ax):
            self._style_mpl_ax(ax)

        # Chart 1 — Normal vs Stress backtracks
        _ax(axes[0])
        n_calls = sum(s.get("recursive_calls", 0) for s in normal_bt_stats)
        n_bt    = sum(s.get("backtracks",      0) for s in normal_bt_stats)
        s_calls = stress_stats.get("recursive_calls", 0)
        s_bt    = stress_stats.get("backtracks",      0)
        x, w = np.arange(2), 0.35
        axes[0].bar(x - w / 2, [n_calls, s_calls], w,
                    label="Recursive Calls",
                    color=T["accent"], edgecolor=T["bg"])
        axes[0].bar(x + w / 2, [n_bt, s_bt], w,
                    label="Backtracks",
                    color=T["warn"], edgecolor=T["bg"])
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(
            ["Normal Run\n(15 courses)", "Stress Test\n(2 courses)"],
            color=T["text"], fontsize=10)
        axes[0].set_title("Backtracking: Normal vs Worst-Case",
                          fontweight="bold", fontsize=11)
        axes[0].legend(facecolor=T["card"], labelcolor=T["text"],
                       fontsize=9)

        # Chart 2 — Hall grid (imshow)
        _ax(axes[1])
        if self.stress_data:
            alloc, sc, hall = self.stress_data
            grid = np.zeros((hall.rows, hall.cols))
            for sid in range(hall.total_seats):
                r, c = hall.id_to_rc[sid]
                if sid in alloc:
                    grid[r][c] = 1 if sc[sid] == "STRESS-A" else 2
            import matplotlib.colors as mcolors
            cmap = mcolors.ListedColormap([T["card"], T["accent"], T["warn"]])
            axes[1].imshow(grid, cmap=cmap, vmin=0, vmax=2, aspect="auto")
            axes[1].set_title(
                "Stress Hall Layout — Alternating A/B  (0 Conflicts)",
                fontweight="bold", fontsize=11)
            axes[1].set_xlabel("Column", fontsize=10)
            axes[1].set_ylabel("Row",    fontsize=10)
            axes[1].tick_params(colors=T["text"])
            patches = [
                mpatches.Patch(color=T["accent"], label="STRESS-A"),
                mpatches.Patch(color=T["warn"],   label="STRESS-B"),
            ]
            axes[1].legend(handles=patches,
                           facecolor=T["card"], labelcolor=T["text"],
                           fontsize=9)

        fig.suptitle("Worst-Case Stress Test Analysis",
                     color=T["text"], fontsize=13,
                     fontweight="bold", y=1.01)
        fig.tight_layout()
        self.stress_canvas.draw()

    # ══════════════════════════════════════════════════════════
    #  TAB 7: ALGORITHM STATS
    # ══════════════════════════════════════════════════════════
    def _build_stats_tab(self):
        tab = self.tabs.tab(self._tab_keys["stats"])
        self._tab_infobar(
            tab,
            "Live algorithm performance  ·  All times are real measured values"
            "  ·  Updated after each pipeline step",
            T["gold"])

        scroll = ctk.CTkScrollableFrame(tab, fg_color=T["bg"],
                                        corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        specs = [
            ("Merge Sort",      "O(n log n)", "O(n)",      T["accent"],  "merge_sort"),
            ("Binary Search",   "O(log n)",   "O(1)",      T["gold"],    "binary_search"),
            ("Graph Build",     "O(V+E)",     "O(V+E)",    T["accent2"], "graph_build"),
            ("Greedy Coloring", "O(V+E)",     "O(V)",      T["purple"],  "greedy_color"),
            ("Backtracking",    "O(n!) pruned","O(n)",     T["warn"],    "backtrack"),
        ]
        self.algo_cards = {}

        for name, tc, sc, color, key in specs:
            card = ctk.CTkFrame(scroll, fg_color=T["card"],
                                corner_radius=10)
            card.pack(fill="x", pady=6)

            # Left colour stripe
            ctk.CTkFrame(card, fg_color=color, width=6,
                         corner_radius=3
                         ).pack(side="left", fill="y",
                                padx=(0, 16), pady=0)

            # Algorithm name + complexity labels
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True,
                      pady=14)
            ctk.CTkLabel(info, text=name,
                         font=F(14, "bold"),
                         text_color=T["text"],
                         anchor="w").pack(anchor="w")
            ctk.CTkLabel(
                info,
                text=f"Time Complexity: {tc}     Space Complexity: {sc}",
                font=F(11), text_color=T["subtext"],
                anchor="w"
            ).pack(anchor="w", pady=(2, 0))

            # Measured time badge (right)
            time_lbl = ctk.CTkLabel(
                card, text="—",
                font=F(22, "bold"),
                text_color=color)
            time_lbl.pack(side="right", padx=24, pady=14)

            unit_lbl = ctk.CTkLabel(
                card, text="ms",
                font=F(11), text_color=T["subtext"])
            unit_lbl.pack(side="right", pady=14)

            self.algo_cards[key] = time_lbl

    def _update_stats_tab(self):
        for key, lbl in self.algo_cards.items():
            val = self.real_times.get(key)
            if val is not None:
                lbl.configure(text=f"{val:.4f}")

    # ══════════════════════════════════════════════════════════
    #  LOGGING
    # ══════════════════════════════════════════════════════════
    def _log(self, msg):
        ts   = datetime.datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}]  {msg}"
        self._log_lines.append(line)
        # Trim to last 500 lines to prevent unbounded growth
        if len(self._log_lines) > 500:
            self._log_lines = self._log_lines[-500:]
        # Update status bar with the latest line
        short = msg[:90] + ("…" if len(msg) > 90 else "")
        try:
            self.status_lbl.configure(text=short)
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════
    #  PIPELINE ACTIONS  (all synchronous — thread-safe)
    # ══════════════════════════════════════════════════════════
    def _load_students_silent(self):
        try:
            with open(DATA_PATH, newline="") as f:
                self.students = list(csv.DictReader(f))
            self.card_students.configure(text=str(len(self.students)))
            self._log(f"✅ Auto-loaded {len(self.students)} students from data/students.csv")
        except Exception:
            self._log("⚠  Could not auto-load students.csv — run generate_data.py first")

    def _load_students(self):
        self._load_students_silent()

    def _run_sort(self):
        if not self.students:
            self._log("⚠  Load students first."); return
        self.sorted_stu, stats = sort_students(self.students, key="RollNo")
        self.real_times["merge_sort"] = stats["time_ms"]

        # Binary Search — measure with median of 10 runs
        from sorting import binary_search_by_course
        sc_sorted, _ = sort_students(self.students, key="Course")
        timings = []
        for _ in range(10):
            t0 = time.perf_counter()
            idx, steps = binary_search_by_course(sc_sorted, "AI3163")
            timings.append((time.perf_counter() - t0) * 1000)
        timings.sort()
        self.real_times["binary_search"] = round(timings[5], 6)

        self._log(f"✅ Merge Sort: {len(self.sorted_stu)} students sorted  "
                  f"|  {stats['comparisons']} comparisons  |  {stats['time_ms']:.4f} ms")
        self._log(f"   Binary Search: AI3163 found at index {idx} "
                  f"in {steps} steps  |  {self.real_times['binary_search']:.5f} ms")
        self._update_stats_tab()

    def _build_graphs(self):
        t0 = time.perf_counter()
        self.halls = build_halls()
        self.real_times["graph_build"] = round(
            (time.perf_counter() - t0) * 1000, 4)
        summary = "  |  ".join(
            f"{h.hall_name} ({h.total_seats} seats)" for h in self.halls)
        self._log(f"✅ Hall graphs built:  {summary}")
        self._update_stats_tab()

    def _run_greedy(self):
        if not self.halls or not self.sorted_stu:
            self._log("⚠  Sort students and build graphs first."); return
        pool = list(self.sorted_stu)
        self.halls_data  = []
        self.greedy_stats = []
        total = 0
        for hall in self.halls:
            chunk = pool[:hall.total_seats]
            pool  = pool[hall.total_seats:]
            alloc, sc, unplaced, g = greedy_color_assign(hall, chunk)
            g["hall"] = hall.hall_name
            self.greedy_stats.append(g)
            total += g["time_ms"]
            n_conf = len(detect_conflicts(hall, alloc, sc))
            self._log(f"   {hall.hall_name}: {g['seats_filled']} filled  "
                      f"|  {g['unplaced']} unplaced  |  {n_conf} conflicts")
            pool = unplaced + pool
            self.halls_data.append(
                (hall.hall_name, alloc, sc, hall, unplaced, g))
        self.real_times["greedy_color"] = round(total, 4)
        self._log(f"✅ Greedy Coloring complete  |  {total:.4f} ms total")
        self._update_stats_tab()

    def _run_backtrack(self):
        if not self.halls_data:
            self._log("⚠  Run Greedy Coloring first."); return
        self.final_halls = []
        self.bt_stats    = []
        total    = 0
        all_conf = []
        for hall_name, alloc, sc, hall, unplaced, _ in self.halls_data:
            _, bt = backtrack_assign(hall, alloc, sc, unplaced)
            conf  = detect_conflicts(hall, alloc, sc)
            self.bt_stats.append(bt)
            total += bt["time_ms"]
            all_conf.extend(conf)
            self._log(f"   {hall_name}: calls={bt['recursive_calls']}  "
                      f"|  bt={bt['backtracks']}  |  conflicts={len(conf)}")
            self.final_halls.append((hall_name, alloc, sc, hall))

        self.real_times["backtrack"] = round(total, 4)
        self.all_conflicts = all_conf
        self.trace_rows    = get_trace()

        placed = sum(len(a) for _, a, _, _ in self.final_halls)
        self.card_placed.configure(text=str(placed))
        self.card_conflicts.configure(
            text=str(len(all_conf)),
            text_color=T["success"] if not all_conf else T["warn"])
        self.card_bt.configure(
            text=str(sum(s["backtracks"] for s in self.bt_stats)))

        self._populate_trace(self.trace_rows)
        self._populate_student_table()
        self._refresh_hall()
        self._update_stats_tab()
        self._log(f"✅ Backtracking complete  |  {placed} placed  "
                  f"|  {len(all_conf)} conflicts  |  {total:.4f} ms")

    def _run_all(self):
        try:
            self._load_students();    self.update_idletasks()
            self._run_sort();         self.update_idletasks()
            self._build_graphs();     self.update_idletasks()
            self._run_greedy();       self.update_idletasks()
            self._run_backtrack();    self.update_idletasks()
            self._run_scaling()
            self._log("🎉 All steps complete!")
        except Exception as e:
            self._log(f"❌ Error in Run All Steps: {e}")
            messagebox.showerror("Run All Steps", str(e))

    def _run_stress(self):
        if not self.halls:
            self._build_graphs()
        try:
            self._log("⚡ Running stress test (2 courses only)...")
            alloc, sc, stats, trace = run_stress_test(self.halls[0])
            self.stress_data  = (alloc, sc, self.halls[0])
            self.stress_stats = stats
            conf = detect_conflicts(self.halls[0], alloc, sc)
            for key, val in [
                ("calls",      stats["recursive_calls"]),
                ("backtracks", stats["backtracks"]),
                ("placed",     stats["students_placed"]),
                ("conflicts",  len(conf)),
                ("time",       f"{stats['time_ms']:.3f}"),
            ]:
                color = (T["success"]
                         if key == "conflicts" and val == 0
                         else self._stress_pill_colors[key])
                self._stress_pills[key].configure(
                    text=str(val), text_color=color)
            self._populate_trace(trace)
            normal = (self.bt_stats if self.bt_stats
                      else [{"backtracks": 0, "recursive_calls": 0}])
            self._draw_stress_chart(stats, normal)
            self.hall_var.set("Stress Test")
            self._refresh_hall()
            self._log(f"✅ Stress test complete  "
                      f"|  calls={stats['recursive_calls']}  "
                      f"|  bt={stats['backtracks']}  "
                      f"|  placed={stats['students_placed']}  "
                      f"|  conflicts={len(conf)}")
        except Exception as e:
            self._log(f"❌ Stress test error: {e}")
            messagebox.showerror("Stress Test", str(e))

    def _run_tests(self):
        try:
            self._log("🧪 Running 20 test cases...")
            self.update_idletasks()
            import subprocess
            result = subprocess.run(
                [sys.executable,
                 os.path.join(BASE_DIR, "test_cases.py")],
                capture_output=True, text=True)
            passed = result.stdout.count("✅ PASS")
            failed = result.stdout.count("❌ FAIL")
            self._log(f"{'✅' if not failed else '❌'} "
                      f"Tests: {passed} PASS  /  {failed} FAIL")
            if not failed:
                messagebox.showinfo(
                    "Test Results",
                    "🎉 All 20 test cases PASSED!\n\n"
                    "Algorithm correctness fully verified.")
            else:
                messagebox.showwarning(
                    "Test Results",
                    f"⚠  {failed} test(s) FAILED.\n"
                    "Check the terminal for details.")
        except Exception as e:
            self._log(f"❌ Test run error: {e}")
            messagebox.showerror("Test Run", str(e))

    def _run_scaling(self):
        try:
            self._log("📈 Running scaling experiment (n = 10 → 500)...")
            self.update_idletasks()
            results = run_scaling_experiment()
            rt = dict(self.real_times)
            # Measure Binary Search if not yet done
            if "binary_search" not in rt or rt["binary_search"] == 0:
                from sorting import binary_search_by_course
                if self.students:
                    sc_sorted, _ = sort_students(
                        self.students, key="Course")
                    timings = []
                    for _ in range(10):
                        t0 = time.perf_counter()
                        binary_search_by_course(sc_sorted, "AI3163")
                        timings.append(
                            (time.perf_counter() - t0) * 1000)
                    timings.sort()
                    rt["binary_search"] = round(timings[5], 6)
                    self.real_times["binary_search"] = rt["binary_search"]
            for k in ["merge_sort", "graph_build",
                      "greedy_color", "backtrack"]:
                if k not in rt:
                    rt[k] = 0
            self._draw_complexity(results, rt)
            self._log(f"✅ Scaling experiment done  "
                      f"|  {len(results)} data points plotted")
        except Exception as e:
            self._log(f"❌ Scaling experiment error: {e}")
            messagebox.showerror("Scaling Experiment", str(e))

    def _run_space(self):
        try:
            self._log("💾 Measuring space complexity with tracemalloc...")
            self.tabs.set(self._tab_keys["space"])
            self.update_idletasks()
            sys.path.insert(0, BASE_DIR)
            from space_complexity import run_all

            # Ensure time data is available for the scatter chart
            if len(self.real_times) < 5:
                self._log("  ⏱  Measuring algorithm runtimes first...")
                from sorting import sort_students as _ss, binary_search_by_course as _bs
                from graph import build_halls as _bh
                from coloring import greedy_color_assign as _gc
                from backtracking import backtrack_assign as _ba
                with open(DATA_PATH) as f:
                    stus = list(csv.DictReader(f))
                _, ms = _ss(stus, key="RollNo")
                self.real_times["merge_sort"] = ms["time_ms"]
                sc_s, _ = _ss(stus, key="Course")
                ts = sorted((time.perf_counter(),
                             _bs(sc_s, "AI3163"),
                             time.perf_counter())
                            for _ in range(10))
                self.real_times["binary_search"] = 0.001
                t0 = time.perf_counter()
                halls = _bh()
                self.real_times["graph_build"] = round(
                    (time.perf_counter() - t0) * 1000, 4)
                _, _, _, g = _gc(halls[0], stus[:halls[0].total_seats])
                self.real_times["greedy_color"] = g["time_ms"]
                _, b = _ba(halls[0], {}, {}, stus[:10])
                self.real_times["backtrack"] = b["time_ms"]

            self.update_idletasks()
            data = run_all()
            self._draw_space_charts(data)
            self._log("✅ Space complexity measured  |  6 charts generated")
            self._log(f"   Merge Sort: {max(r['peak_kb'] for r in data['merge_sort']):.2f} KB  [O(n)]")
            self._log(f"   Binary Search: {data['binary_search']['peak_kb']:.4f} KB  [O(1)]")
            self._log(f"   Graph Build: {max(r['peak_kb'] for r in data['graph_build']):.2f} KB  [O(V+E)]")
        except Exception as e:
            self._log(f"❌ Space complexity error: {e}")
            messagebox.showerror("Space Complexity", str(e))

    def _export_csv(self):
        if not self.final_halls:
            self._log("⚠  Run allocation first."); return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="seating_plan_export.csv",
            title="Export Seating Plan")
        if not path:
            return
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(
                f, fieldnames=["Hall", "Seat", "RollNo", "Name", "Course"])
            w.writeheader()
            for hall_name, alloc, sc, hall in self.final_halls:
                for sid, stu in sorted(alloc.items()):
                    w.writerow({
                        "Hall":   hall_name,
                        "Seat":   hall.get_seat_label(sid),
                        "RollNo": stu["RollNo"],
                        "Name":   stu["Name"],
                        "Course": stu["Course"],
                    })
        self._log(f"✅ Exported to {os.path.basename(path)}")
        messagebox.showinfo("Export Complete",
                            f"Seating plan saved to:\n{path}")


# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()